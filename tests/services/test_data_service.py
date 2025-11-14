from datetime import date
from app.services.data_service import DataService

def test_add_student(data_service: DataService):
    """Test adding a new student."""
    data_service.add_student("John", "Doe")
    assert data_service.get_student_count() == 1

def test_add_student_with_birth_date(data_service: DataService):
    """Test adding a new student with a birth date."""
    birth_date = date(2005, 5, 15)
    student = data_service.add_student("Jane", "Doe", birth_date=birth_date)
    assert student.birth_date == birth_date

def test_add_course(data_service: DataService):
    """Test adding a new course."""
    data_service.add_course("Math 101", "MATH101")
    assert data_service.get_course_count() == 1

def test_add_assessment(data_service: DataService):
    """Test adding a new assessment."""
    course = data_service.add_course("Science 101", "SCI101")
    class_ = data_service.create_class("1A", course.id)
    assessment = data_service.add_assessment(class_.id, "Midterm", 1.0)
    assert assessment.name == "Midterm"
    assert assessment.class_id == class_.id

def test_add_grade(data_service: DataService):
    """Test adding a new grade."""
    student = data_service.add_student("Jane", "Doe")
    course = data_service.add_course("Science 101", "SCI101")
    class_ = data_service.create_class("1A", course.id)
    assessment = data_service.add_assessment(class_.id, "Midterm", 1.0)
    data_service.add_student_to_class(student.id, class_.id, 1)
    data_service.add_grade(student.id, assessment.id, 85.5)
    grades = data_service.get_grades_for_class(class_.id)
    assert len(grades) == 1
    assert grades[0].score == 85.5

def test_get_all_students(data_service: DataService):
    """Test retrieving all students."""
    data_service.add_student("John", "Doe")
    data_service.add_student("Jane", "Smith")
    assert len(data_service.get_all_students()) == 2

def test_update_student(data_service: DataService, db_session):
    """Test updating a student's information."""
    student = data_service.add_student("Jon", "Doe")
    db_session.flush()
    data_service.update_student(student.id, "John", "Doe")
    db_session.flush()
    assert data_service.get_student_by_name("Jon Doe") is None
    updated_student = data_service.get_student_by_name("John Doe")
    assert updated_student is not None
    assert updated_student.first_name == "John"

def test_delete_student(data_service: DataService, db_session):
    """Test deleting a student and their associated grades."""
    student = data_service.add_student("John", "Doe")
    course = data_service.add_course("History 101", "HIST101")
    class_ = data_service.create_class("1A", course.id)
    assessment = data_service.add_assessment(class_.id, "Final Exam", 1.0)
    data_service.add_grade(student.id, assessment.id, 92.0)
    db_session.flush()
    assert data_service.get_student_count() == 1
    assert len(data_service.get_all_grades()) == 1
    data_service.delete_student(student.id)
    db_session.flush()
    assert data_service.get_student_count() == 0
    assert len(data_service.get_all_grades()) == 0

def test_get_student_by_name(data_service: DataService):
    """Test finding a student by name (case-insensitive)."""
    data_service.add_student("John", "Doe")
    assert data_service.get_student_by_name("john doe") is not None
    assert data_service.get_student_by_name("Jane Doe") is None

def test_create_class(data_service: DataService):
    """Test creating a new class."""
    course = data_service.add_course("Biology 101", "BIO101")
    data_service.create_class("1A", course.id)
    assert len(data_service.get_all_classes()) == 1

def test_add_student_to_class(data_service: DataService):
    """Test enrolling a student in a class."""
    student = data_service.add_student("Alice", "Wonderland")
    course = data_service.add_course("Literature", "LIT101")
    class_ = data_service.create_class("2B", course.id)
    enrollment = data_service.add_student_to_class(student.id, class_.id, 1)
    assert enrollment.student_id == student.id
    assert enrollment.class_id == class_.id

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

def test_update_enrollment_status(data_service: DataService, db_session):
    """Test updating the status of an enrollment."""
    student = data_service.add_student("Student", "One")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class", course.id)
    enrollment = data_service.add_student_to_class(student.id, class_.id, 1)
    db_session.flush()
    assert enrollment.status == "Active"
    data_service.update_enrollment_status(enrollment.id, "Inactive")
    db_session.flush()
    updated_enrollment = data_service.get_enrollments_for_class(class_.id)[0]
    assert updated_enrollment.status == "Inactive"

def test_get_unenrolled_students(data_service: DataService):
    """Test retrieving students not enrolled in a specific class."""
    student1 = data_service.add_student("Enrolled", "Student")
    data_service.add_student("Unenrolled", "Student")
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
    data_service.add_student("None", "Student")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class", course.id)
    data_service.add_student_to_class(student_active.id, class_.id, 1, status="Active")
    data_service.add_student_to_class(student_inactive.id, class_.id, 2, status="Inactive")
    active_students = data_service.get_students_with_active_enrollment()
    assert len(active_students) == 1
    assert active_students[0].first_name == "Active"

def test_get_next_call_number(data_service: DataService):
    """Test calculating the next call number for a class."""
    student1 = data_service.add_student("Student", "One")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class", course.id)
    assert data_service.get_next_call_number(class_.id) == 1
    data_service.add_student_to_class(student1.id, class_.id, 5)
    assert data_service.get_next_call_number(class_.id) == 6

def test_get_grades_for_class_filters_inactive_students(data_service: DataService):
    """Test that get_grades_for_class only returns grades for active students."""
    student_active = data_service.add_student("Active", "Student")
    student_inactive = data_service.add_student("Inactive", "Student")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class", course.id)
    assessment = data_service.add_assessment(class_.id, "Test", 1.0)
    data_service.add_student_to_class(student_active.id, class_.id, 1, status="Active")
    data_service.add_student_to_class(student_inactive.id, class_.id, 2, status="Inactive")
    data_service.add_grade(student_active.id, assessment.id, 100)
    data_service.add_grade(student_inactive.id, assessment.id, 50)
    grades = data_service.get_grades_for_class(class_.id)
    assert len(grades) == 1
    assert grades[0].student_id == student_active.id

def test_update_assessment(data_service: DataService, db_session):
    """Test updating an assessment's information."""
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class", course.id)
    assessment = data_service.add_assessment(class_.id, "Old Name", 1.0)
    db_session.flush()
    data_service.update_assessment(assessment.id, "New Name", 2.0)
    db_session.flush()
    updated_assessment = data_service.get_class_by_id(class_.id).assessments[0]
    assert updated_assessment.name == "New Name"
    assert updated_assessment.weight == 2.0

def test_delete_assessment(data_service: DataService, db_session):
    """Test deleting an assessment and its associated grades."""
    student = data_service.add_student("Student", "One")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class", course.id)
    assessment = data_service.add_assessment(class_.id, "Test to Delete", 1.0)
    data_service.add_student_to_class(student.id, class_.id, 1)
    data_service.add_grade(student.id, assessment.id, 100)
    db_session.flush()
    assert len(data_service.get_class_by_id(class_.id).assessments) == 1
    assert len(data_service.get_all_grades()) == 1
    data_service.delete_assessment(assessment.id)
    db_session.flush()

    # Expire the class_ object to force a reload of its relationships
    db_session.expire(class_)

    assert len(data_service.get_class_by_id(class_.id).assessments) == 0
    assert len(data_service.get_all_grades()) == 0

def test_grade_grid_logic(data_service: DataService, db_session):
    """Test weighted average calculation and upserting grades."""
    student1 = data_service.add_student("Student", "One")
    student2 = data_service.add_student("Student", "Two")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class", course.id)
    data_service.add_student_to_class(student1.id, class_.id, 1)
    data_service.add_student_to_class(student2.id, class_.id, 2)
    assess1 = data_service.add_assessment(class_.id, "Test 1", 1.0)
    assess2 = data_service.add_assessment(class_.id, "Test 2", 2.0)
    assessments = [assess1, assess2]
    data_service.add_grade(student1.id, assess1.id, 8.0)
    db_session.flush()
    grades = data_service.get_grades_for_class(class_.id)
    avg1 = data_service.calculate_weighted_average(student1.id, grades, assessments)
    assert round(avg1, 2) == 2.67
    avg2 = data_service.calculate_weighted_average(student2.id, grades, assessments)
    assert avg2 == 0.0
    grades_to_upsert = [
        {'student_id': student1.id, 'assessment_id': assess1.id, 'score': 9.0},
        {'student_id': student1.id, 'assessment_id': assess2.id, 'score': 7.0},
        {'student_id': student2.id, 'assessment_id': assess1.id, 'score': 10.0}
    ]
    data_service.upsert_grades_for_class(class_.id, grades_to_upsert)
    db_session.flush()
    final_grades = data_service.get_grades_for_class(class_.id)
    assert len(final_grades) == 3
    final_avg1 = data_service.calculate_weighted_average(student1.id, final_grades, assessments)
    assert round(final_avg1, 2) == 7.67
    final_avg2 = data_service.calculate_weighted_average(student2.id, final_grades, assessments)
    assert round(final_avg2, 2) == 3.33

def test_update_and_delete_class(data_service: DataService, db_session):
    """Test updating and deleting a class."""
    student = data_service.add_student("Student", "One")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Old Name", course.id)
    data_service.add_student_to_class(student.id, class_.id, 1)
    db_session.flush()
    data_service.update_class(class_.id, "New Name")
    db_session.flush()
    updated_class = data_service.get_class_by_id(class_.id)
    assert updated_class.name == "New Name"
    assert len(data_service.get_all_classes()) == 1
    assert len(data_service.get_enrollments_for_class(class_.id)) == 1
    data_service.delete_class(class_.id)
    db_session.flush()
    assert len(data_service.get_all_classes()) == 0
    assert len(data_service.get_enrollments_for_class(class_.id)) == 0

def test_get_all_grades_with_details(data_service: DataService):
    """Test retrieving all grades with their full relational details."""
    student = data_service.add_student("Student", "One")
    course = data_service.add_course("Course", "C101")
    class_ = data_service.create_class("Class", course.id)
    assessment = data_service.add_assessment(class_.id, "Final Exam", 1.0)
    data_service.add_student_to_class(student.id, class_.id, 1)
    grade = data_service.add_grade(student.id, assessment.id, 95.0)
    grades_with_details = data_service.get_all_grades_with_details()
    assert len(grades_with_details) == 1
    retrieved_grade = grades_with_details[0]
    assert retrieved_grade.id == grade.id
    assert retrieved_grade.student.first_name == "Student"
    assert retrieved_grade.assessment.name == "Final Exam"
    assert retrieved_grade.assessment.class_.name == "Class"
    assert retrieved_grade.assessment.class_.course.course_name == "Course"
