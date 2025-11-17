from datetime import date
from app.services.data_service import DataService
from sqlalchemy.orm import Session
import io

def dict_to_csv_string(data: list[dict], header: str) -> str:
    """Converts a list of dictionaries to a CSV string."""
    output = io.StringIO()
    output.write(header + "\n")
    for item in data:
        if item.get("birth_date"):
            item["birth_date_str"] = item["birth_date"].strftime("%d/%m/%Y")
        else:
            item["birth_date_str"] = ""

        output.write(f"1;{item['full_name']};{item['birth_date_str']};{item['status']}\n")

    return output.getvalue()

def test_batch_upsert_students_and_enroll_scenarios(data_service: DataService, db_session: Session):
    """
    Test the full lifecycle of student import, ensuring all operations occur
    within a single, consistent database session provided by the test fixtures.
    """
    course = data_service.add_course("Test Course", "TC101")
    class_ = data_service.create_class("Test Class", course['id'])
    db_session.flush()

    header = "Nº de chamada;Nome do Aluno;Data de Nascimento;Situação do Aluno"

    initial_student_data = [
        {"full_name": "John Doe", "first_name": "John", "last_name": "Doe", "birth_date": date(2010, 1, 1), "status": "Ativo"},
        {"full_name": "Jane Smith", "first_name": "Jane", "last_name": "Smith", "birth_date": date(2011, 2, 2), "status": "Ativo"}
    ]
    initial_csv_content = dict_to_csv_string(initial_student_data, header)
    data_service.import_students_from_csv(class_['id'], initial_csv_content)
    db_session.flush()

    enrollments = data_service.get_enrollments_for_class(class_['id'])
    assert len(enrollments) == 2
    assert data_service.get_student_count() == 2

    john_enrollment = next(e for e in enrollments if e['student_first_name'] == "John")
    assert john_enrollment['status'] == "Active"
    assert john_enrollment['student_birth_date'] == date(2010, 1, 1).isoformat()

    updated_student_data = [
        {"full_name": "John Doe", "first_name": "John", "last_name": "Doe", "birth_date": date(2010, 1, 15), "status": "Transferido"},
        {"full_name": "Jane Smith", "first_name": "Jane", "last_name": "Smith", "birth_date": date(2011, 2, 2), "status": "Ativo"},
        {"full_name": "Peter Jones", "first_name": "Peter", "last_name": "Jones", "birth_date": date(2012, 3, 3), "status": "Ativo"}
    ]
    updated_csv_content = dict_to_csv_string(updated_student_data, header)
    data_service.import_students_from_csv(class_['id'], updated_csv_content)
    db_session.flush()

    enrollments = data_service.get_enrollments_for_class(class_['id'])
    assert len(enrollments) == 3
    assert data_service.get_student_count() == 3

    john_enrollment_updated = next(e for e in enrollments if e['student_first_name'] == "John")
    assert john_enrollment_updated['status'] == "Inactive"

    # Re-fetch student data to check birth date
    john_student_updated = data_service.get_student_by_name("John Doe")
    assert john_student_updated['birth_date'] == date(2010, 1, 15).isoformat()

    duplicate_student_data = [
        {"full_name": "John Doe", "first_name": "John", "last_name": "Doe", "birth_date": date(2010, 1, 15), "status": "Ativo"},
        {"full_name": "Duplicate Person", "first_name": "Duplicate", "last_name": "Person", "birth_date": date(2013, 4, 4), "status": "Ativo"},
        {"full_name": "Duplicate Person", "first_name": "Duplicate", "last_name": "Person", "birth_date": date(2013, 4, 4), "status": "BAIXA"}
    ]
    duplicate_csv_content = dict_to_csv_string(duplicate_student_data, header)
    data_service.import_students_from_csv(class_['id'], duplicate_csv_content)
    db_session.flush()

    enrollments = data_service.get_enrollments_for_class(class_['id'])
    assert len(enrollments) == 4, "Students not in the CSV should not be removed"
    assert data_service.get_student_count() == 4

    john_final_enrollment = next(e for e in enrollments if e['student_first_name'] == "John")
    assert john_final_enrollment['status'] == "Active"

    duplicate_enrollment = next(e for e in enrollments if e['student_first_name'] == "Duplicate")
    assert duplicate_enrollment is not None
    assert duplicate_enrollment['status'] == "Inactive"

    db_session.commit()
