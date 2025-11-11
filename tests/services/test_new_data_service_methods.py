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

def test_analysis_methods(data_service: DataService):
    # 1. Setup: Create a realistic scenario
    course = data_service.add_course("Math", "MAT101")
    class_ = data_service.create_class("Grade 6 Math", course.id)

    # Students
    student_ok = data_service.add_student("Alice", "Aventura")
    student_low_grades = data_service.add_student("Bruno", "Baixanota")
    student_high_incidents = data_service.add_student("Carlos", "Comportamento")
    student_both = data_service.add_student("Daniela", "Desafio")

    # Enroll students
    data_service.add_student_to_class(student_ok.id, class_.id, 1)
    data_service.add_student_to_class(student_low_grades.id, class_.id, 2)
    data_service.add_student_to_class(student_high_incidents.id, class_.id, 3)
    data_service.add_student_to_class(student_both.id, class_.id, 4)

    # Assessments (total weight = 10.0)
    exam1 = data_service.add_assessment(class_.id, "Midterm Exam", 4.0)
    exam2 = data_service.add_assessment(class_.id, "Final Exam", 6.0)

    # Grades
    # Alice (Good)
    data_service.add_grade(student_ok.id, exam1.id, 8.0)
    data_service.add_grade(student_ok.id, exam2.id, 7.5)
    # Bruno (Low Grades)
    data_service.add_grade(student_low_grades.id, exam1.id, 4.0) # Below threshold
    data_service.add_grade(student_low_grades.id, exam2.id, 5.0)
    # Carlos (Good Grades, High Incidents)
    data_service.add_grade(student_high_incidents.id, exam1.id, 9.0)
    data_service.add_grade(student_high_incidents.id, exam2.id, 8.5)
    # Daniela (Low Grades and High Incidents)
    data_service.add_grade(student_both.id, exam1.id, 4.5) # Below threshold
    data_service.add_grade(student_both.id, exam2.id, 6.0)

    # Incidents
    today = date.today()
    data_service.create_incident(class_.id, student_high_incidents.id, "Disruptive behavior", today)
    data_service.create_incident(class_.id, student_high_incidents.id, "Late for class", today)
    data_service.create_incident(class_.id, student_both.id, "Forgot homework", today)
    data_service.create_incident(class_.id, student_both.id, "Unprepared for lesson", today)
    data_service.create_incident(class_.id, student_both.id, "Distracted others", today) # 3 incidents

    # 2. Test get_student_performance_summary for Alice
    summary = data_service.get_student_performance_summary(student_ok.id, class_.id)
    assert summary is not None
    assert summary["student_name"] == "Alice Aventura"
    assert summary["incident_count"] == 0
    # Expected: (8.0 * 4.0 + 7.5 * 6.0) / (4.0 + 6.0) = (32 + 45) / 10 = 7.7
    assert summary["weighted_average"] == 7.7
    assert len(summary["grades"]) == 2
    assert summary["highest_grade"]["score"] == 8.0
    assert summary["lowest_grade"]["score"] == 7.5

    # 3. Test get_students_at_risk (default thresholds: grade < 5.0, incidents >= 2)
    at_risk = data_service.get_students_at_risk(class_.id)

    assert len(at_risk) == 3
    at_risk_names = {s["student_name"] for s in at_risk}
    assert "Bruno Baixanota" in at_risk_names
    assert "Carlos Comportamento" in at_risk_names
    assert "Daniela Desafio" in at_risk_names

    for student in at_risk:
        if student["student_name"] == "Bruno Baixanota":
            assert len(student["reasons"]) == 1
            assert "Nota mais baixa: 4.00" in student["reasons"][0]
        if student["student_name"] == "Carlos Comportamento":
            assert len(student["reasons"]) == 1
            assert "2 incidentes registrados" in student["reasons"][0]
        if student["student_name"] == "Daniela Desafio":
            # Both conditions met
            assert len(student["reasons"]) == 2
            assert "Nota mais baixa: 4.50" in student["reasons"]
            assert "3 incidentes registrados" in student["reasons"]

    # 4. Test get_students_at_risk with custom thresholds
    at_risk_custom = data_service.get_students_at_risk(class_.id, grade_threshold=4.2, incident_threshold=3)

    assert len(at_risk_custom) == 2
    at_risk_custom_names = {s["student_name"] for s in at_risk_custom}
    assert "Bruno Baixanota" in at_risk_custom_names # Still has a grade of 4.0
    assert "Daniela Desafio" in at_risk_custom_names # Still has 3 incidents
