from datetime import date
import pytest
from sqlalchemy.exc import IntegrityError
from app.services.data_service import DataService
from app.models.lesson import Lesson
from app.models.incident import Incident

def test_delete_class_with_dependencies(data_service: DataService, db_session):
    """
    Test that deleting a class also deletes its associated lessons and incidents,
    preventing IntegrityError.
    """
    # Setup
    course = data_service.add_course("Test Course", "TC101")
    class_ = data_service.create_class("Test Class", course['id'])
    student = data_service.add_student("Test", "Student")

    # Add Lesson
    lesson = data_service.create_lesson(class_['id'], "Lesson 1", "Content", date.today())

    # Enroll student
    data_service.add_student_to_class(student['id'], class_['id'], 1)

    # Add Incident
    incident = data_service.create_incident(class_['id'], student['id'], "Incident 1", date.today())

    db_session.flush()

    # Verify existence
    assert len(data_service.get_lessons_for_class(class_['id'])) == 1
    assert len(data_service.get_incidents_for_class(class_['id'])) == 1

    # Action: Delete Class
    # This is expected to fail before the fix
    try:
        data_service.delete_class(class_['id'])
        db_session.flush()
    except IntegrityError:
        pytest.fail("IntegrityError raised when deleting class with dependencies.")

    # Verification
    # Class should be gone
    assert data_service.get_class_by_id(class_['id']) is None

    # Dependent records should be gone
    # We can't use service methods that filter by class_id easily if the class is gone?
    # Actually we can, but let's query DB directly or assume if no error they are gone
    # (since FK would prevent deletion otherwise).
    # But let's be explicit.
    lessons = db_session.query(Lesson).filter(Lesson.class_id == class_['id']).all()
    incidents = db_session.query(Incident).filter(Incident.class_id == class_['id']).all()

    assert len(lessons) == 0
    assert len(incidents) == 0

def test_delete_student_with_dependencies(data_service: DataService, db_session):
    """
    Test that deleting a student also deletes their associated incidents,
    preventing IntegrityError.
    """
    # Setup
    student = data_service.add_student("Test", "Student 2")
    course = data_service.add_course("Test Course 2", "TC102")
    class_ = data_service.create_class("Test Class 2", course['id'])

    # Enroll student
    data_service.add_student_to_class(student['id'], class_['id'], 1)

    # Add Incident
    incident = data_service.create_incident(class_['id'], student['id'], "Incident 2", date.today())

    db_session.flush()

    # Verify existence
    incidents = db_session.query(Incident).filter(Incident.student_id == student['id']).all()
    assert len(incidents) == 1

    # Action: Delete Student
    try:
        data_service.delete_student(student['id'])
        db_session.flush()
    except IntegrityError:
        pytest.fail("IntegrityError raised when deleting student with dependencies.")

    # Verification
    assert data_service.get_student_by_name("Test Student 2") is None

    incidents = db_session.query(Incident).filter(Incident.student_id == student['id']).all()
    assert len(incidents) == 0
