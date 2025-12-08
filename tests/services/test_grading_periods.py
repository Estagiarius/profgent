import pytest
from datetime import date
from app.services.data_service import DataService
from app.models.student import Student
from app.models.class_ import Class
from app.models.course import Course
from app.models.class_subject import ClassSubject
from app.models.class_enrollment import ClassEnrollment
from app.models.assessment import Assessment
from app.models.grade import Grade

def test_grading_periods_logic(db_session):
    service = DataService(db_session)

    # Setup: Create Class, Course, Subject, Student, Enrollment
    c = Class(name="Test Class")
    course = Course(course_name="Math", course_code="MAT")
    db_session.add(c)
    db_session.add(course)
    db_session.flush()

    cs = ClassSubject(class_id=c.id, course_id=course.id)
    db_session.add(cs)
    db_session.flush()

    s = Student(first_name="John", last_name="Doe", enrollment_date="2023-01-01")
    db_session.add(s)
    db_session.flush()

    e = ClassEnrollment(class_id=c.id, student_id=s.id, call_number=1, status='Active')
    db_session.add(e)
    db_session.flush()

    # 1. Test adding assessments to different periods
    a1 = service.add_assessment(cs.id, "Prova 1", 10.0, grading_period=1)
    a2 = service.add_assessment(cs.id, "Prova 2", 10.0, grading_period=2)
    a3 = service.add_assessment(cs.id, "Prova 3", 10.0, grading_period=3)
    a4 = service.add_assessment(cs.id, "Prova 4", 10.0, grading_period=4)

    assert a1['grading_period'] == 1
    assert a4['grading_period'] == 4

    # 2. Add grades
    service.add_grade(s.id, a1['id'], 8.0)  # Period 1: 8.0
    service.add_grade(s.id, a2['id'], 7.0)  # Period 2: 7.0
    service.add_grade(s.id, a3['id'], 6.0)  # Period 3: 6.0
    service.add_grade(s.id, a4['id'], 9.0)  # Period 4: 9.0

    # 3. Calculate Period Averages
    averages = service.get_student_period_averages(s.id, cs.id)

    assert averages[1] == 8.0
    assert averages[2] == 7.0
    assert averages[3] == 6.0
    assert averages[4] == 9.0

    # Final Calculated should be (8+7+6+9)/4 = 30/4 = 7.5
    assert averages['final_calculated'] == 7.5
    assert averages['final_override'] is None

    # 4. Test Final Grade Override
    final_assessment = service.ensure_final_assessment(cs.id)
    assert final_assessment['name'] == "Média Final (Manual)"

    # Add override grade
    service.add_grade(s.id, final_assessment['id'], 10.0)

    averages_after_override = service.get_student_period_averages(s.id, cs.id)
    assert averages_after_override['final_calculated'] == 7.5
    assert averages_after_override['final_override'] == 10.0

def test_grading_period_validation(db_session):
    service = DataService(db_session)

    # Setup
    c = Class(name="Test Class 2")
    course = Course(course_name="Hist", course_code="HIS")
    db_session.add(c)
    db_session.add(course)
    db_session.flush()
    cs = ClassSubject(class_id=c.id, course_id=course.id)
    db_session.add(cs)
    db_session.flush()

    # Test invalid periods
    with pytest.raises(ValueError):
        service.add_assessment(cs.id, "Invalid", 1.0, grading_period=0)

    with pytest.raises(ValueError):
        service.add_assessment(cs.id, "Invalid", 1.0, grading_period=6)
