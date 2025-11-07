from app.services.data_service import DataService
from app.tools import database_write_tools
from app.tools.database_write_tools import add_new_student, add_new_course, add_new_grade
import pytest

# Fixture to inject the test DataService into the tool module
@pytest.fixture(autouse=True)
def patch_tool_data_service(data_service: DataService):
    """Monkeypatches the shared DataService instance in the services package."""
    database_write_tools.data_service = data_service

def test_add_new_student(data_service: DataService):
    """Test the add_new_student tool."""
    result = add_new_student("Test", "Student")
    assert "Successfully added" in result

    # Verify the student was actually created in the test DB
    student = data_service.get_student_by_name("Test Student")
    assert student is not None
    assert student.first_name == "Test"

def test_add_new_course(data_service: DataService):
    """Test the add_new_course tool."""
    result = add_new_course("Test Course", "TC101")
    assert "Successfully added" in result

    # Verify the course was created
    course = data_service.get_course_by_name("Test Course")
    assert course is not None
    assert course.course_code == "TC101"

def test_add_new_grade(data_service: DataService):
    """Test the add_new_grade tool."""
    # First, create the student and course to add a grade to
    student = data_service.add_student("Grade", "Student")
    course = data_service.add_course("Grading", "G101")
    class_ = data_service.create_class("1A", course.id)
    assessment = data_service.add_assessment(class_.id, "Final Project", 1.0)
    data_service.add_student_to_class(student.id, class_.id, 1) # Enroll student

    result = add_new_grade("Grade Student", "1A", "Final Project", 99.9)
    assert "Successfully added grade" in result

    # Verify the grade was created
    grades = data_service.get_grades_for_class(class_.id)
    assert len(grades) == 1
    assert grades[0].score == 99.9
    assert grades[0].assessment.name == "Final Project"
