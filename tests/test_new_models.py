import pytest
from datetime import date
from sqlalchemy.orm import Session
from app.services.data_service import DataService
from app.models.student import Student
from app.models.course import Course
from app.models.class_ import Class
from app.models.lesson import Lesson
from app.models.incident import Incident

def test_create_lesson_and_incident(data_service: DataService, db_session: Session):
    # 1. Setup: Create prerequisite objects using the service
    student = data_service.add_student("John", "Doe")
    assert student is not None
    course = data_service.add_course("Test Course", "TC101")
    assert course is not None
    class_ = data_service.create_class("Test Class", course.id)
    assert class_ is not None

    # 2. Create a Lesson using the test's db_session
    new_lesson = Lesson(
        date=date.today(),
        title="Introduction to Testing",
        content="This is the content of the lesson.",
        class_id=class_.id
    )
    db_session.add(new_lesson)
    db_session.commit()
    db_session.refresh(new_lesson)

    # Verify Lesson creation
    assert new_lesson.id is not None
    assert new_lesson.title == "Introduction to Testing"
    assert new_lesson.class_.id == class_.id

    # 3. Create an Incident using the test's db_session
    new_incident = Incident(
        date=date.today(),
        description="Student was very participative.",
        class_id=class_.id,
        student_id=student.id
    )
    db_session.add(new_incident)
    db_session.commit()
    db_session.refresh(new_incident)

    # Verify Incident creation
    assert new_incident.id is not None
    assert new_incident.description == "Student was very participative."
    assert new_incident.class_.id == class_.id
    assert new_incident.student.id == student.id

    # 4. Verify back-population
    db_session.refresh(class_)
    db_session.refresh(student)
    assert len(class_.lessons) == 1
    assert class_.lessons[0].title == "Introduction to Testing"
    assert len(class_.incidents) == 1
    assert len(student.incidents) == 1
    assert student.incidents[0].description == "Student was very participative."
