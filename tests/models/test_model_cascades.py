import pytest
from app.models.class_ import Class
from app.models.lesson import Lesson
from app.models.incident import Incident
from app.models.student import Student
from app.models.course import Course
from app.models.class_enrollment import ClassEnrollment
from datetime import date

def test_class_cascade_delete(db_session):
    """
    Verifies that deleting a Class via ORM automatically deletes dependent Lessons and Incidents
    thanks to the `cascade="all, delete-orphan"` configuration.
    """
    # Setup
    c = Course(course_name="Cascade Course", course_code="CC1")
    db_session.add(c)
    db_session.flush()

    cl = Class(name="Cascade Class", course_id=c.id)
    db_session.add(cl)
    db_session.flush()

    l = Lesson(class_id=cl.id, title="Lesson", content="Content", date=date.today())
    db_session.add(l)
    db_session.flush()

    # Action: Delete Class via ORM
    db_session.delete(cl)
    db_session.flush()

    # Verify Lesson is gone
    assert db_session.query(Lesson).filter_by(id=l.id).first() is None

def test_student_cascade_delete(db_session):
    """
    Verifies that deleting a Student via ORM automatically deletes dependent Incidents and Enrollments.
    """
    s = Student(first_name="Cascade", last_name="Student", enrollment_date="2023-01-01")
    db_session.add(s)
    c = Course(course_name="Cascade Course 2", course_code="CC2")
    db_session.add(c)
    db_session.flush()
    cl = Class(name="Cascade Class 2", course_id=c.id)
    db_session.add(cl)
    db_session.flush()

    i = Incident(class_id=cl.id, student_id=s.id, description="Incident", date=date.today())
    db_session.add(i)

    e = ClassEnrollment(class_id=cl.id, student_id=s.id, call_number=1)
    db_session.add(e)

    db_session.flush()

    # Action
    db_session.delete(s)
    db_session.flush()

    # Verify dependents are gone
    assert db_session.query(Incident).filter_by(id=i.id).first() is None
    assert db_session.query(ClassEnrollment).filter_by(id=e.id).first() is None
