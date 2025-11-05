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

def test_add_assessment(data_service: DataService):
    """Test adding a new assessment."""
    course = data_service.add_course("Science 101", "SCI101")
    class_ = data_service.create_class("1A", course.id)
    assessment = data_service.add_assessment(class_.id, "Midterm", 1.0)

    assert assessment is not None
    assert assessment.name == "Midterm"
    assert assessment.weight == 1.0
    assert assessment.class_id == class_.id

def test_add_grade(data_service: DataService):
    """Test adding a new grade."""
    student = data_service.add_student("Jane", "Doe")
    course = data_service.add_course("Science 101", "SCI101")
    class_ = data_service.create_class("1A", course.id)
    assessment = data_service.add_assessment(class_.id, "Midterm", 1.0)
    grade = data_service.add_grade(student.id, assessment.id, 85.5)

    assert grade is not None
    assert grade.score == 85.5

    # Verify the grade is associated correctly
    grades = data_service.get_grades_for_class(class_.id)
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

    # Verify that the old name is not found
    old_student = data_service.get_student_by_name("Jon Doe")
    assert old_student is None

    # Verify that the new name is found
    updated_student = data_service.get_student_by_name("John Doe")
    assert updated_student is not None
    assert updated_student.first_name == "John"

def test_delete_student(data_service: DataService):
    """Test deleting a student and their associated grades."""
    student = data_service.add_student("John", "Doe")
    course = data_service.add_course("History 101", "HIST101")
    class_ = data_service.create_class("1A", course.id)
    assessment = data_service.add_assessment(class_.id, "Final Exam", 1.0)
    data_service.add_grade(student.id, assessment.id, 92.0)

    assert data_service.get_student_count() == 1
    assert len(data_service.get_all_grades()) == 1

    data_service.delete_student(student.id)

    assert data_service.get_student_count() == 0
    # The associated grade should also be deleted due to cascade
    assert len(data_service.get_all_grades()) == 0

def test_get_student_by_name(data_service: DataService):
    """Test finding a student by name (case-insensitive)."""
    data_service.add_student("John", "Doe")

    found_student = data_service.get_student_by_name("john doe")
    assert found_student is not None
    assert found_student.first_name == "John"

    not_found_student = data_service.get_student_by_name("Jane Doe")
    assert not_found_student is None

# --- Class and Enrollment Tests ---

def test_create_class(data_service: DataService):
    """Test creating a new class."""
    course = data_service.add_course("Biology 101", "BIO101")
    class_ = data_service.create_class("1A", course.id)
    assert class_ is not None
    assert class_.name == "1A"
    assert class_.course_id == course.id

    all_classes = data_service.get_all_classes()
    assert len(all_classes) == 1

def test_add_student_to_class(data_service: DataService):
    """Test enrolling a student in a class."""
    student = data_service.add_student("Alice", "Wonderland")
    course = data_service.add_course("Literature", "LIT101")
    class_ = data_service.create_class("2B", course.id)

    enrollment = data_service.add_student_to_class(student.id, class_.id, 1)
    assert enrollment is not None
    assert enrollment.student_id == student.id
    assert enrollment.class_id == class_.id
    assert enrollment.call_number == 1

def test_get_students_in_class(data_service: DataService):
    """Test retrieving all students enrolled in a class."""
    student1 = data_service.add_student("Student", "One")
    student2 = data_service.add_student("Student", "Two")
    course = data_service.add_course("Gym", "GYM101")
    class_ = data_service.create_class("3C", course.id)

    data_service.add_student_to_class(student1.id, class_.id, 1)
    data_service.add_student_to_class(student2.id, class_.id, 2)

    enrolled_students = data_service.get_enrollments_for_class(class_.id)
    assert len(enrolled_students) == 2
    student_names = [f"{e.student.first_name} {e.student.last_name}" for e in enrolled_students]
    assert "Student One" in student_names
    assert "Student Two" in student_names

def test_update_enrollment_status(data_service: DataService):
    """Test updating the status of an enrollment."""
    student = data_service.add_student("Student", "One")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class", course.id)
    enrollment = data_service.add_student_to_class(student.id, class_.id, 1)
    assert enrollment.status == "Active"

    data_service.update_enrollment_status(enrollment.id, "Inactive")

    updated_enrollment = data_service.get_enrollments_for_class(class_.id)[0]
    assert updated_enrollment.status == "Inactive"

def test_get_unenrolled_students(data_service: DataService):
    """Test retrieving students not enrolled in a specific class."""
    student1 = data_service.add_student("Enrolled", "Student")
    student2 = data_service.add_student("Unenrolled", "Student")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class", course.id)
    data_service.add_student_to_class(student1.id, class_.id, 1)

    unenrolled = data_service.get_unenrolled_students(class_.id)
    assert len(unenrolled) == 1
    assert unenrolled[0].first_name == "Unenrolled"

def test_get_students_with_active_enrollment(data_service: DataService):
    """Test retrieving students who have at least one active enrollment."""
    student_active = data_service.add_student("Active", "Student")
    student_inactive = data_service.add_student("Inactive", "Student")
    student_none = data_service.add_student("None", "Student") # No enrollments

    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class", course.id)

    # Enroll student_active with status Active
    data_service.add_student_to_class(student_active.id, class_.id, 1, status="Active")
    # Enroll student_inactive with status Inactive
    data_service.add_student_to_class(student_inactive.id, class_.id, 2, status="Inactive")

    active_students = data_service.get_students_with_active_enrollment()
    assert len(active_students) == 1
    assert active_students[0].first_name == "Active"
