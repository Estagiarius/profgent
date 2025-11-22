import pytest
from sqlalchemy import event
from datetime import date
from app.services.data_service import DataService
from app.models.student import Student
from app.models.grade import Grade

def test_enrollment_date_serialization(data_service, db_session):
    """
    Verifies that Student.enrollment_date is passed as a string (serialized),
    not as a date object.
    """
    # Setup strict type checking listener
    def check_enrollment_date_type(mapper, connection, target):
        if target.enrollment_date is not None and not isinstance(target.enrollment_date, str):
            raise TypeError(f"enrollment_date must be str, got {type(target.enrollment_date)}")

    # Register the listener
    event.listen(Student, 'before_insert', check_enrollment_date_type)

    try:
        # Setup data for import
        course = data_service.add_course("Test Course", "TC999")
        class_ = data_service.create_class("Test Class", course['id'])

        csv_content = "Nome do Aluno;Data de Nascimento;Situação do Aluno\nTest Student;01/01/2000;Ativo"

        # Action: Import students
        result = data_service.import_students_from_csv(class_['id'], csv_content)

        # Verification
        # If the bug exists, the listener raises TypeError.
        # import_students_from_csv catches Exception and puts it in errors.
        # So if errors contains our TypeError message, the bug is present.
        for err in result['errors']:
            if "enrollment_date must be str" in str(err):
                pytest.fail(f"Bug detected: {err}")

        # Also fail if other errors occurred preventing the check
        assert not result['errors'], f"Import failed with errors: {result['errors']}"

    finally:
        event.remove(Student, 'before_insert', check_enrollment_date_type)

def test_grade_date_recorded_serialization(data_service, db_session):
    """
    Verifies that Grade.date_recorded is passed as a string (serialized),
    not as a date object.
    """
    # Setup strict type checking listener
    def check_date_recorded_type(mapper, connection, target):
        if target.date_recorded is not None and not isinstance(target.date_recorded, str):
            raise TypeError(f"date_recorded must be str, got {type(target.date_recorded)}")

    event.listen(Grade, 'before_insert', check_date_recorded_type)

    try:
        # Setup data
        student = data_service.add_student("Grade", "Tester")
        course = data_service.add_course("Grade Course", "GC1")
        class_ = data_service.create_class("Grade Class", course['id'])
        assessment = data_service.add_assessment(class_['id'], "Test 1", 1.0)
        data_service.add_student_to_class(student['id'], class_['id'], 1)

        # Action 1: add_grade
        try:
            data_service.add_grade(student['id'], assessment['id'], 8.0)
        except TypeError as e:
             if "date_recorded must be str" in str(e):
                 pytest.fail("Bug detected in add_grade: date_recorded passed as date object.")
             raise e

        # Action 2: upsert_grades_for_class (new grade)
        assessment2 = data_service.add_assessment(class_['id'], "Test 2", 1.0)
        grades_data = [{'student_id': student['id'], 'assessment_id': assessment2['id'], 'score': 9.0}]

        try:
            data_service.upsert_grades_for_class(class_['id'], grades_data)
        except TypeError as e:
             if "date_recorded must be str" in str(e):
                 pytest.fail("Bug detected in upsert_grades_for_class: date_recorded passed as date object.")
             raise e

    finally:
        event.remove(Grade, 'before_insert', check_date_recorded_type)
