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
def add_new_course(course_name: str, course_code: str = None) -> str:
    """
    Adds a new course to the database. If the course_code is not provided,
    it will be automatically generated from the course name.
    Use this tool when a user asks to add or create a new course.
    Returns a confirmation message.
    """
    if not course_name:
        return "Error: The course_name is required."

    if not course_code:
        # Generate a base code from the initials of the course name
        words = course_name.split()
        if len(words) > 1:
            base_code = "".join(word[0] for word in words).upper()
        else:
            base_code = course_name[:3].upper() # Use the first 3 letters for a single word

        # Ensure the generated code is unique
        unique_code = base_code
        counter = 1
        while data_service.get_course_by_code(unique_code):
            unique_code = f"{base_code}{counter}"
            counter += 1
        course_code = unique_code

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
