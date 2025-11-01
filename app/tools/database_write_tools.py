from sqlalchemy.exc import SQLAlchemyError
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

    try:
        student = data_service.add_student(first_name, last_name)
        if student:
            return f"Successfully added new student: {first_name} {last_name} with ID {student.id}."
        else:
            # This case might be redundant if add_student raises an exception on failure
            return f"Error: An unknown error occurred while adding student {first_name} {last_name}."
    except SQLAlchemyError as e:
        return f"Error: A database error occurred while adding the student: {e}"
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"

@tool
def add_new_course(course_name: str, course_code: str) -> str:
    """
    Adds a new course to the database.
    Use this tool when a user explicitly asks to add or create a new course.
    Returns a confirmation message.
    """
    if not course_name or not course_code:
        return "Error: Both course_name and course_code are required."

    try:
        course = data_service.add_course(course_name, course_code)
        if course:
            return f"Successfully added new course: {course_name} ({course_code}) with ID {course.id}."
        else:
            return f"Error: An unknown error occurred while adding course {course_name}."
    except SQLAlchemyError as e:
        return f"Error: A database error occurred while adding the course: {e}"
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"

@tool
def add_new_grade(student_name: str, class_name: str, assessment_name: str, score: float) -> str:
    """
    Adds a new grade for a student for a specific assessment in a class.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Error: Student '{student_name}' not found."

        # This is a simplification. A real app might need a more robust way to find classes
        all_classes = data_service.get_all_classes()
        target_class = next((c for c in all_classes if c.name.lower() == class_name.lower()), None)
        if not target_class:
            return f"Error: Class '{class_name}' not found."

        assessment = next((a for a in target_class.assessments if a.name.lower() == assessment_name.lower()), None)
        if not assessment:
            return f"Error: Assessment '{assessment_name}' not found in class '{class_name}'."

        grade = data_service.add_grade(student.id, assessment.id, score)
        if grade:
            return f"Successfully added grade for {student_name} in {target_class.course.course_name}."
        else:
            return "Error: Could not add grade."
    except Exception as e:
        # Log the error e
        return f"Error: An unexpected error occurred: {e}"
