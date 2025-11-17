from app.services.data_service import DataService
from app.tools import database_tools
from app.tools.database_tools import get_student_grade, list_courses_for_student, get_class_average
import pytest

def test_get_student_grade_found(data_service: DataService):
    """Test get_student_grade when the grade is found."""
    database_tools.data_service = data_service # Monkeypatch before tool call
    student = data_service.add_student("John", "Doe")
    course = data_service.add_course("Math 101", "M101")
    class_ = data_service.create_class("1A", course['id'])
    assessment = data_service.add_assessment(class_['id'], "Final Exam", 1.0)
    data_service.add_student_to_class(student['id'], class_['id'], 1) # Enroll student
    data_service.add_grade(student['id'], assessment['id'], 95.5)

    result = get_student_grade("John Doe", "Math 101")
    assert "95.5" in result
    assert "John Doe" in result
    assert "Math 101" in result

def test_get_student_grade_not_found(data_service: DataService):
    """Test get_student_grade when the student or course is not found."""
    database_tools.data_service = data_service
    result = get_student_grade("Jane Doe", "Nonexistent Course")
    assert "Student 'Jane Doe' not found." in result

def test_list_courses_for_student(data_service: DataService):
    """Test listing courses for a student."""
    database_tools.data_service = data_service
    student = data_service.add_student("Alice", "Smith")
    course1 = data_service.add_course("History 202", "H202")
    course2 = data_service.add_course("Art 101", "A101")
    class1 = data_service.create_class("1A", course1['id'])
    class2 = data_service.create_class("1B", course2['id'])
    assessment1 = data_service.add_assessment(class1['id'], "Essay", 1.0)
    assessment2 = data_service.add_assessment(class2['id'], "Project", 1.0)
    data_service.add_grade(student['id'], assessment1['id'], 88.0)
    data_service.add_grade(student['id'], assessment2['id'], 92.0)

    result = list_courses_for_student("Alice Smith")
    assert "History 202" in result
    assert "Art 101" in result

def test_get_class_average(data_service: DataService):
    """Test calculating the class average for a course."""
    database_tools.data_service = data_service
    student1 = data_service.add_student("Bob", "Ray")
    student2 = data_service.add_student("Charlie", "Day")
    course = data_service.add_course("Physics 303", "P303")
    class_ = data_service.create_class("1A", course['id'])
    assessment = data_service.add_assessment(class_['id'], "Lab 1", 1.0)
    data_service.add_student_to_class(student1['id'], class_['id'], 1) # Enroll student
    data_service.add_student_to_class(student2['id'], class_['id'], 2) # Enroll student
    data_service.add_grade(student1['id'], assessment['id'], 70)
    data_service.add_grade(student2['id'], assessment['id'], 90)

    result = get_class_average("Physics 303")
    assert "80.00" in result
