from app.core.tools.tool_decorator import tool
from app.services import data_service

@tool
def get_student_grade(student_name: str, course_name: str) -> str:
    """
    Finds the grade of a specific student in a given course.
    Returns the grade as a string or a 'not found' message.
    """
    grade = data_service.grade_repo.find_grade_for_student(student_name, course_name)

    if grade:
        return f"The grade for {student_name} in {course_name} for the assignment '{grade.assignment_name}' is {grade.score}."
    else:
        return f"Could not find a grade for a student named '{student_name}' in the course '{course_name}'."

@tool
def list_courses_for_student(student_name: str) -> str:
    """
    Lists all the courses a specific student is enrolled in.
    """
    student = data_service.get_student_by_name(student_name)

    if not student:
        return f"Student '{student_name}' not found."

    grades = data_service.grade_repo.session.query(data_service.grade_repo.model).filter_by(student_id=student.id).all()
    if not grades:
        return f"{student_name} is not enrolled in any courses with recorded grades."

    course_ids = {grade.course_id for grade in grades}
    courses = data_service.course_repo.session.query(data_service.course_repo.model).filter(data_service.course_repo.model.id.in_(course_ids)).all()

    course_names = [course.course_name for course in courses]
    return f"{student_name} is enrolled in the following courses: {', '.join(course_names)}."

@tool
def get_class_average(course_name: str) -> str:
    """
    Calculates the average grade for all students in a specific course.
    """
    course = data_service.get_course_by_name(course_name)

    if not course:
        return f"Course '{course_name}' not found."

    grades = data_service.get_grades_for_course(course.id)
    if not grades:
        return f"There are no recorded grades for the course '{course_name}'."

    total_score = sum(grade.score for grade in grades)
    average = total_score / len(grades)

    return f"The class average for '{course_name}' is {average:.2f}."
