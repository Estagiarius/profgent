import pytest
from datetime import date
from sqlalchemy.orm import Session
from app.services.data_service import DataService

def test_lesson_methods(data_service: DataService, db_session: Session):
    # 1. Setup
    course = data_service.add_course("Science", "SCI101")
    assert course is not None
    class_ = data_service.create_class("Grade 5 Science", course.id)
    assert class_ is not None

    today = date.today()

    # 2. Test create_lesson
    lesson1 = data_service.create_lesson(class_.id, "Photosynthesis", "Content about photosynthesis.", today)
    assert lesson1 is not None
    assert lesson1.title == "Photosynthesis"
    assert lesson1.class_id == class_.id

    # 3. Test get_lessons_for_class
    lessons = data_service.get_lessons_for_class(class_.id)
    assert len(lessons) == 1
    assert lessons[0].title == "Photosynthesis"

    # 4. Test update_lesson
    new_date = date(2024, 1, 1)
    data_service.update_lesson(lesson1.id, "Cellular Respiration", "New content.", new_date)

    db_session.refresh(lesson1)
    assert lesson1.title == "Cellular Respiration"
    assert lesson1.content == "New content."
    assert lesson1.date == new_date

    # 5. Test delete_lesson
    data_service.delete_lesson(lesson1.id)
    lessons_after_delete = data_service.get_lessons_for_class(class_.id)
    assert len(lessons_after_delete) == 0

def test_incident_methods(data_service: DataService):
    # 1. Setup
    student = data_service.add_student("Test", "Student")
    assert student is not None
    course = data_service.add_course("History", "HIS101")
    assert course is not None
    class_ = data_service.create_class("Grade 5 History", course.id)
    assert class_ is not None

    today = date.today()

    # 2. Test create_incident
    incident1 = data_service.create_incident(class_.id, student.id, "Excellent participation.", today)
    assert incident1 is not None
    assert incident1.description == "Excellent participation."
    assert incident1.student_id == student.id

    # 3. Test get_incidents_for_class
    incidents = data_service.get_incidents_for_class(class_.id)
    assert len(incidents) == 1
    # Verify that the student was eager-loaded
    assert incidents[0].student.first_name == "Test"
