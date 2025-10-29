from sqlalchemy.orm import Session
from app.core.tools.tool_decorator import tool
from app.data.database import SessionLocal
from app.data.grade_repository import GradeRepository
from app.data.student_repository import StudentRepository
from app.data.course_repository import CourseRepository
from app.models.student import Student
from app.models.course import Course

# We create a single session for the tools to use.
# In a more complex app, you might manage sessions differently.
db_session: Session = SessionLocal()

@tool
def get_student_grade(student_name: str, course_name: str) -> str:
    """
    Finds the grade of a specific student in a given course.
    Returns the grade as a string or a 'not found' message.
    """
    grade_repo = GradeRepository(db_session)
    grade = grade_repo.find_grade_for_student(student_name, course_name)

    if grade:
        return f"The grade for {student_name} in {course_name} for the assignment '{grade.assignment_name}' is {grade.score}."
    else:
        return f"Could not find a grade for a student named '{student_name}' in the course '{course_name}'."

@tool
def list_courses_for_student(student_name: str) -> str:
    """
    Lists all the courses a specific student is enrolled in.
    """
    student_repo = StudentRepository(db_session)
    student = db_session.query(Student).filter(Student.first_name + " " + Student.last_name == student_name).first()

    if not student:
        return f"Student '{student_name}' not found."

    # This is a simplified query. A real implementation might involve a direct relationship.
    grades = GradeRepository(db_session).session.query(Grade).filter(Grade.student_id == student.id).all()
    if not grades:
        return f"{student_name} is not enrolled in any courses with recorded grades."

    course_ids = {grade.course_id for grade in grades}
    courses = CourseRepository(db_session).session.query(Course).filter(Course.id.in_(course_ids)).all()

    course_names = [course.course_name for course in courses]
    return f"{student_name} is enrolled in the following courses: {', '.join(course_names)}."

@tool
def get_class_average(course_name: str) -> str:
    """
    Calculates the average grade for all students in a specific course.
    """
    course_repo = CourseRepository(db_session)
    course = course_repo.session.query(Course).filter(Course.course_name == course_name).first()

    if not course:
        return f"Course '{course_name}' not found."

    grades = GradeRepository(db_session).session.query(Grade).filter(Grade.course_id == course.id).all()
    if not grades:
        return f"There are no recorded grades for the course '{course_name}'."

    total_score = sum(grade.score for grade in grades)
    average = total_score / len(grades)

    return f"The class average for '{course_name}' is {average:.2f}."
