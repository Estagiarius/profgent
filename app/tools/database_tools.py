from app.core.tools.tool_decorator import tool
from app.services import data_service

@tool
def get_student_grade(student_name: str, course_name: str) -> str:
    """
    Finds all grades of a specific student in a given course.
    Returns the grades as a string or a 'not found' message.
    """
    student = data_service.get_student_by_name(student_name)
    if not student:
        return f"Student '{student_name}' not found."

    course = data_service.get_course_by_name(course_name)
    if not course:
        return f"Course '{course_name}' not found."

    grades = data_service.get_grades_for_course(course.id)
    student_grades = [g for g in grades if g.student_id == student.id]

    if student_grades:
        grade_list = [f"'{grade.assignment_name}': {grade.score}" for grade in student_grades]
        return f"Grades for {student_name} in {course_name}: {', '.join(grade_list)}."
    else:
        return f"Could not find any grades for '{student_name}' in '{course_name}'."

@tool
def list_courses_for_student(student_name: str) -> str:
    """
    Lists all the courses a specific student is enrolled in.
    """
    student = data_service.get_student_by_name(student_name)
    if not student:
        return f"Student '{student_name}' not found."

    all_grades = data_service.get_all_grades()
    student_grades = [g for g in all_grades if g.student_id == student.id]

    if not student_grades:
        return f"{student_name} is not enrolled in any courses with recorded grades."

    course_ids = {grade.course_id for grade in student_grades}

    all_courses = data_service.get_all_courses()
    enrolled_courses = [c for c in all_courses if c.id in course_ids]

    course_names = [course.course_name for course in enrolled_courses]
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
