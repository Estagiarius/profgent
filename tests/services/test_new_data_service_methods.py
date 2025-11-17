from datetime import date
from sqlalchemy.orm import Session
from app.services.data_service import DataService

def test_lesson_methods(data_service: DataService, db_session: Session):
    course = data_service.add_course("Science", "SCI101")
    class_ = data_service.create_class("Grade 5 Science", course['id'])
    today = date.today()

    lesson1 = data_service.create_lesson(class_['id'], "Photosynthesis", "Content about photosynthesis.", today)
    db_session.flush()
    assert lesson1['id'] is not None

    lessons = data_service.get_lessons_for_class(class_['id'])
    assert len(lessons) == 1
    assert lessons[0]['title'] == "Photosynthesis"

    new_date = date(2024, 1, 1)
    data_service.update_lesson(lesson1['id'], "Cellular Respiration", "New content.", new_date)
    db_session.flush()

    updated_lessons = data_service.get_lessons_for_class(class_['id'])
    assert updated_lessons[0]['title'] == "Cellular Respiration"
    assert updated_lessons[0]['content'] == "New content."
    assert updated_lessons[0]['date'] == new_date.isoformat()

    data_service.delete_lesson(lesson1['id'])
    db_session.flush()
    lessons_after_delete = data_service.get_lessons_for_class(class_['id'])
    assert len(lessons_after_delete) == 0

def test_incident_methods(data_service: DataService):
    student = data_service.add_student("Test", "Student")
    course = data_service.add_course("History", "HIS101")
    class_ = data_service.create_class("Grade 5 History", course['id'])
    today = date.today()

    data_service.create_incident(class_['id'], student['id'], "Excellent participation.", today)

    incidents = data_service.get_incidents_for_class(class_['id'])
    assert len(incidents) == 1
    assert incidents[0]['student_first_name'] == "Test"

def test_analysis_methods(data_service: DataService):
    course = data_service.add_course("Math", "MAT101")
    class_ = data_service.create_class("Grade 6 Math", course['id'])

    student_ok = data_service.add_student("Alice", "Aventura")
    student_low_grades = data_service.add_student("Bruno", "Baixanota")
    student_high_incidents = data_service.add_student("Carlos", "Comportamento")
    student_both = data_service.add_student("Daniela", "Desafio")

    data_service.add_student_to_class(student_ok['id'], class_['id'], 1)
    data_service.add_student_to_class(student_low_grades['id'], class_['id'], 2)
    data_service.add_student_to_class(student_high_incidents['id'], class_['id'], 3)
    data_service.add_student_to_class(student_both['id'], class_['id'], 4)

    exam1 = data_service.add_assessment(class_['id'], "Midterm Exam", 4.0)
    exam2 = data_service.add_assessment(class_['id'], "Final Exam", 6.0)

    data_service.add_grade(student_ok['id'], exam1['id'], 8.0)
    data_service.add_grade(student_ok['id'], exam2['id'], 7.5)
    data_service.add_grade(student_low_grades['id'], exam1['id'], 4.0)
    data_service.add_grade(student_low_grades['id'], exam2['id'], 5.0)
    data_service.add_grade(student_high_incidents['id'], exam1['id'], 9.0)
    data_service.add_grade(student_high_incidents['id'], exam2['id'], 8.5)
    data_service.add_grade(student_both['id'], exam1['id'], 4.5)
    data_service.add_grade(student_both['id'], exam2['id'], 6.0)

    today = date.today()
    data_service.create_incident(class_['id'], student_high_incidents['id'], "Disruptive behavior", today)
    data_service.create_incident(class_['id'], student_high_incidents['id'], "Late for class", today)
    data_service.create_incident(class_['id'], student_both['id'], "Forgot homework", today)
    data_service.create_incident(class_['id'], student_both['id'], "Unprepared for lesson", today)
    data_service.create_incident(class_['id'], student_both['id'], "Distracted others", today)

    summary = data_service.get_student_performance_summary(student_ok['id'], class_['id'])
    assert summary is not None
    assert summary["weighted_average"] == 7.7

    at_risk = data_service.get_students_at_risk(class_['id'])
    assert len(at_risk) == 3

    at_risk_custom = data_service.get_students_at_risk(class_['id'], grade_threshold=4.2, incident_threshold=3)
    assert len(at_risk_custom) == 1
