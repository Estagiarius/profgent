from datetime import date
from app.data.database import SessionLocal
from app.data.student_repository import StudentRepository
from app.data.course_repository import CourseRepository
from app.data.grade_repository import GradeRepository
from app.models.student import Student
from app.models.course import Course
from app.models.grade import Grade

class DataService:
    def __init__(self):
        self.db_session = SessionLocal()
        self.student_repo = StudentRepository(self.db_session)
        self.course_repo = CourseRepository(self.db_session)
        self.grade_repo = GradeRepository(self.db_session)

    # --- Create ---
    def add_student(self, first_name: str, last_name: str) -> Student | None:
        if not first_name or not last_name: return None
        today = date.today().isoformat()
        new_student = Student(first_name=first_name, last_name=last_name, enrollment_date=today)
        return self.student_repo.add(new_student)

    def add_course(self, course_name: str, course_code: str) -> Course | None:
        if not course_name or not course_code: return None
        new_course = Course(course_name=course_name, course_code=course_code)
        return self.course_repo.add(new_course)

    def add_grade(self, student_id: int, course_id: int, assignment_name: str, score: float) -> Grade | None:
        if not all([student_id, course_id, assignment_name, score is not None]): return None
        today = date.today().isoformat()
        new_grade = Grade(student_id=student_id, course_id=course_id, assignment_name=assignment_name, score=score, date_recorded=today)
        return self.grade_repo.add(new_grade)

    # --- Read ---
    def get_all_students(self) -> list[Student]:
        return self.student_repo.get_all()

    def get_all_courses(self) -> list[Course]:
        return self.course_repo.get_all()

    def get_all_grades(self) -> list[Grade]:
        return self.grade_repo.get_all()

    def get_student_count(self) -> int:
        return self.db_session.query(Student).count()

    def get_course_count(self) -> int:
        return self.db_session.query(Course).count()

    # --- Update ---
    def update_student(self, student_id: int, first_name: str, last_name: str):
        student = self.student_repo.get(student_id)
        if student:
            student.first_name = first_name
            student.last_name = last_name
            self.db_session.commit()

    def update_course(self, course_id: int, course_name: str, course_code: str):
        course = self.course_repo.get(course_id)
        if course:
            course.course_name = course_name
            course.course_code = course_code
            self.db_session.commit()

    def update_grade(self, grade_id: int, assignment_name: str, score: float):
        grade = self.grade_repo.get(grade_id)
        if grade:
            grade.assignment_name = assignment_name
            grade.score = score
            self.db_session.commit()

    # --- Delete ---
    def delete_student(self, student_id: int):
        self.db_session.query(Grade).filter(Grade.student_id == student_id).delete()
        student = self.student_repo.get(student_id)
        if student: self.student_repo.delete(student)

    def delete_course(self, course_id: int):
        self.db_session.query(Grade).filter(Grade.course_id == course_id).delete()
        course = self.course_repo.get(course_id)
        if course: self.course_repo.delete(course)

    def delete_grade(self, grade_id: int):
        grade = self.grade_repo.get(grade_id)
        if grade: self.grade_repo.delete(grade)

    def __del__(self):
        self.db_session.close()
