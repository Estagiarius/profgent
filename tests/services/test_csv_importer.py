from datetime import date
from app.services.data_service import DataService
from sqlalchemy.orm import Session

def test_batch_upsert_students_and_enroll_scenarios(data_service: DataService, db_session: Session):
    """
    Test the full lifecycle of batch upserting students and enrollments:
    1. Initial import of new students.
    2. Re-importing with status changes, data updates, and new students.
    3. Re-importing with duplicates in the source data, ensuring only the last entry is used.
    4. Verifying that students not in the latest import are NOT removed from the class.
    """
    # Setup: Create a course and a class
    course = data_service.add_course("Test Course", "TC101")
    class_ = data_service.create_class("Test Class", course.id)
    db_session.flush()

    # --- Scenario 1: Initial Import ---
    initial_student_data = [
        {
            "full_name": "John Doe", "first_name": "John", "last_name": "Doe",
            "birth_date": date(2010, 1, 1), "status": "Ativo"
        },
        {
            "full_name": "Jane Smith", "first_name": "Jane", "last_name": "Smith",
            "birth_date": date(2011, 2, 2), "status": "Ativo"
        }
    ]

    data_service.batch_upsert_students_and_enroll(class_.id, initial_student_data)
    db_session.flush()

    # Verification for Initial Import
    enrollments = data_service.get_enrollments_for_class(class_.id)
    assert len(enrollments) == 2
    assert data_service.get_student_count() == 2

    john_enrollment = next(e for e in enrollments if e.student.first_name == "John")
    assert john_enrollment.status == "Ativo"
    assert john_enrollment.student.birth_date == date(2010, 1, 1)
    assert john_enrollment.call_number == 1

    jane_enrollment = next(e for e in enrollments if e.student.first_name == "Jane")
    assert jane_enrollment.call_number == 2

    # --- Scenario 2: Re-import with Updates and a New Student ---
    updated_student_data = [
        {
            "full_name": "John Doe", "first_name": "John", "last_name": "Doe",
            "birth_date": date(2010, 1, 15), "status": "Transferido" # Status and birth_date updated
        },
        {
            "full_name": "Jane Smith", "first_name": "Jane", "last_name": "Smith",
            "birth_date": date(2011, 2, 2), "status": "Ativo" # No change
        },
        {
            "full_name": "Peter Jones", "first_name": "Peter", "last_name": "Jones",
            "birth_date": date(2012, 3, 3), "status": "Ativo" # New student
        }
    ]

    data_service.batch_upsert_students_and_enroll(class_.id, updated_student_data)
    db_session.flush()

    # Verification for Update
    enrollments = data_service.get_enrollments_for_class(class_.id)
    assert len(enrollments) == 3
    assert data_service.get_student_count() == 3

    # Check John Doe's updated status and birth date
    john_enrollment_updated = next(e for e in enrollments if e.student.first_name == "John")
    assert john_enrollment_updated.status == "Transferido"
    assert john_enrollment_updated.student.birth_date == date(2010, 1, 15)

    # Check Peter Jones was added with the next call number
    peter_enrollment = next(e for e in enrollments if e.student.first_name == "Peter")
    assert peter_enrollment is not None
    assert peter_enrollment.status == "Ativo"
    assert peter_enrollment.call_number == 3

    # --- Scenario 3: Re-import with Internal Duplicates ---
    # The logic should process only the *last* instance of a student from the CSV.
    duplicate_student_data = [
        {
            "full_name": "John Doe", "first_name": "John", "last_name": "Doe",
            "birth_date": date(2010, 1, 15), "status": "Ativo" # Reverted to Ativo
        },
        {
            "full_name": "Duplicate Person", "first_name": "Duplicate", "last_name": "Person",
            "birth_date": date(2013, 4, 4), "status": "Ativo"
        },
        {
            "full_name": "Duplicate Person", "first_name": "Duplicate", "last_name": "Person",
            "birth_date": date(2013, 4, 4), "status": "BAIXA" # This is the one that should be imported
        }
    ]

    data_service.batch_upsert_students_and_enroll(class_.id, duplicate_student_data)
    db_session.flush()

    # Verification for Duplicates
    enrollments = data_service.get_enrollments_for_class(class_.id)

    # Existing students (Jane, Peter) are not in the new file, but should remain enrolled.
    # John's status is updated, and Duplicate Person is added. Total should be 4.
    assert len(enrollments) == 4, "Students not in the CSV should not be removed"
    assert data_service.get_student_count() == 4

    # John's status should be updated back to Ativo
    john_final_enrollment = next(e for e in enrollments if e.student.first_name == "John")
    assert john_final_enrollment.status == "Ativo"

    # The duplicate person should have been added once with the final status
    duplicate_enrollment = next(e for e in enrollments if e.student.first_name == "Duplicate")
    assert duplicate_enrollment is not None
    assert duplicate_enrollment.status == "BAIXA"
    assert duplicate_enrollment.call_number == 4
