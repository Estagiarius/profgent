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

    # A course can have multiple classes, so we need to check all of them
    student_grades_in_course = []
    for class_ in course.classes:
        grades_in_class = data_service.get_grades_for_class(class_.id)
        student_grades_in_class = [g for g in grades_in_class if g.student_id == student.id]
        student_grades_in_course.extend(student_grades_in_class)

    if not student_grades_in_course:
        return f"No grades found for {student_name} in {course_name}."

    grade_list = "\n".join([f"- {g.assessment.name}: {g.score}" for g in student_grades_in_course])
    return f"Grades for {student_name} in {course_name}:\n{grade_list}"

@tool
def list_courses_for_student(student_name: str) -> str:
    """
    Lists all the courses a specific student is enrolled in.
    """
    student = data_service.get_student_by_name(student_name)
    if not student:
        return f"Student '{student_name}' not found."

    if not student.grades:
        return f"{student_name} is not enrolled in any courses with recorded grades."

    course_names = {grade.assessment.class_.course.course_name for grade in student.grades}

    return f"Courses for {student_name}:\n" + "\n".join(f"- {name}" for name in sorted(list(course_names)))

@tool
def get_class_average(course_name: str) -> str:
    """
    Calculates the average grade for all students in a specific course.
    """
    course = data_service.get_course_by_name(course_name)
    if not course:
        return f"Course '{course_name}' not found."

    all_grades = []
    for class_ in course.classes:
        grades_in_class = data_service.get_grades_for_class(class_.id)
        all_grades.extend(grades_in_class)

    if not all_grades:
        return f"No grades found for the course {course_name}."

    average = sum(g.score for g in all_grades) / len(all_grades)
    return f"The class average for {course_name} is {average:.2f}."
