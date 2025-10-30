from app.services.data_service import DataService

def test_add_student(data_service: DataService):
    """Test adding a new student."""
    student = data_service.add_student("John", "Doe")
    assert student is not None
    assert student.first_name == "John"
    assert student.last_name == "Doe"
    assert data_service.get_student_count() == 1

def test_add_course(data_service: DataService):
    """Test adding a new course."""
    course = data_service.add_course("Math 101", "MATH101")
    assert course is not None
    assert course.course_name == "Math 101"
    assert data_service.get_course_count() == 1

def test_add_grade(data_service: DataService):
    """Test adding a new grade."""
    student = data_service.add_student("Jane", "Doe")
    course = data_service.add_course("Science 101", "SCI101")
    grade = data_service.add_grade(student.id, course.id, "Midterm", 85.5)

    assert grade is not None
    assert grade.score == 85.5

    # Verify the grade is associated correctly
    grades = data_service.get_grades_for_course(course.id)
    assert len(grades) == 1
    assert grades[0].student_id == student.id

def test_get_all_students(data_service: DataService):
    """Test retrieving all students."""
    data_service.add_student("John", "Doe")
    data_service.add_student("Jane", "Smith")
    students = data_service.get_all_students()
    assert len(students) == 2

def test_update_student(data_service: DataService):
    """Test updating a student's information."""
    student = data_service.add_student("Jon", "Doe")
    data_service.update_student(student.id, "John", "Doe")

    updated_student = data_service.get_student_by_name("John Doe")
    assert updated_student is not None
    assert updated_student.first_name == "John"

def test_delete_student(data_service: DataService):
    """Test deleting a student and their associated grades."""
    student = data_service.add_student("John", "Doe")
    course = data_service.add_course("History 101", "HIST101")
    data_service.add_grade(student.id, course.id, "Final Exam", 92.0)

    assert data_service.get_student_count() == 1
    assert len(data_service.get_all_grades()) == 1

    data_service.delete_student(student.id)

    assert data_service.get_student_count() == 0
    # The associated grade should also be deleted
    assert len(data_service.get_all_grades()) == 0

def test_get_student_by_name(data_service: DataService):
    """Test finding a student by name (case-insensitive)."""
    data_service.add_student("John", "Doe")

    found_student = data_service.get_student_by_name("john doe")
    assert found_student is not None
    assert found_student.first_name == "John"

    not_found_student = data_service.get_student_by_name("Jane Doe")
    assert not_found_student is None
