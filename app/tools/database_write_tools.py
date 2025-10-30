from app.core.tools.tool_decorator import tool
from app.services import data_service

@tool
def add_new_student(first_name: str, last_name: str) -> str:
    """
    Adds a new student to the database.
    Use this tool when a user explicitly asks to add or create a new student.
    Returns a confirmation message.
    """
    if not first_name or not last_name:
        return "Error: Both first_name and last_name are required."

    student = data_service.add_student(first_name, last_name)
    if student:
        return f"Successfully added new student: {first_name} {last_name} with ID {student.id}."
    else:
        return f"Error: Failed to add new student {first_name} {last_name}."

@tool
def add_new_course(course_name: str, course_code: str) -> str:
    """
    Adds a new course to the database.
    Use this tool when a user explicitly asks to add or create a new course.
    Returns a confirmation message.
    """
    if not course_name or not course_code:
        return "Error: Both course_name and course_code are required."

    course = data_service.add_course(course_name, course_code)
    if course:
        return f"Successfully added new course: {course_name} ({course_code}) with ID {course.id}."
    else:
        return f"Error: Failed to add new course {course_name}."

@tool
def add_new_grade(student_name: str, course_name: str, assignment_name: str, score: float) -> str:
    """
    Adds a new grade for a student in a specific course.
    Use this to record a score for an assignment, test, or exam.
    Returns a confirmation message.
    """
    student = data_service.get_student_by_name(student_name)
    if not student:
        return f"Error: Student '{student_name}' not found."

    course = data_service.get_course_by_name(course_name)
    if not course:
        return f"Error: Course '{course_name}' not found."

    grade = data_service.add_grade(student.id, course.id, assignment_name, score)
    if grade:
        return f"Successfully added grade for {student_name} in {course_name}: {assignment_name} - Score {score}."
    else:
        return "Error: Failed to add new grade."
