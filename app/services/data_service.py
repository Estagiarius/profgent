from datetime import date
from sqlalchemy import func
from app.data.database import get_db_session
from app.models.student import Student
from app.models.course import Course
from app.models.grade import Grade

class DataService:
    # --- Create ---
    def add_student(self, first_name: str, last_name: str) -> Student | None:
        if not first_name or not last_name: return None
        today = date.today().isoformat()
        new_student = Student(first_name=first_name, last_name=last_name, enrollment_date=today)
        with get_db_session() as db:
            db.add(new_student)
            db.commit()
            db.refresh(new_student)
            return new_student

    def add_course(self, course_name: str, course_code: str) -> Course | None:
        if not course_name or not course_code: return None
        new_course = Course(course_name=course_name, course_code=course_code)
        with get_db_session() as db:
            db.add(new_course)
            db.commit()
            db.refresh(new_course)
            return new_course

    def add_grade(self, student_id: int, course_id: int, assignment_name: str, score: float) -> Grade | None:
        if not all([student_id, course_id, assignment_name, score is not None]): return None
        today = date.today().isoformat()
        new_grade = Grade(student_id=student_id, course_id=course_id, assignment_name=assignment_name, score=score, date_recorded=today)
        with get_db_session() as db:
            db.add(new_grade)
            db.commit()
            db.refresh(new_grade)
            return new_grade

    # --- Read ---
    def get_all_students(self) -> list[Student]:
        with get_db_session() as db:
            return db.query(Student).all()

    def get_all_courses(self) -> list[Course]:
        with get_db_session() as db:
            return db.query(Course).all()

    def get_all_grades(self) -> list[Grade]:
        with get_db_session() as db:
            return db.query(Grade).all()

    def get_student_count(self) -> int:
        with get_db_session() as db:
            return db.query(Student).count()

    def get_course_count(self) -> int:
        with get_db_session() as db:
            return db.query(Course).count()

    def get_grades_for_course(self, course_id: int) -> list[Grade]:
        with get_db_session() as db:
            return db.query(Grade).filter(Grade.course_id == course_id).all()

    def get_student_by_name(self, name: str) -> Student | None:
        with get_db_session() as db:
            # Case-insensitive search for full name
            return db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == name.lower()).first()

    def get_course_by_name(self, name: str) -> Course | None:
        with get_db_session() as db:
            # Case-insensitive search for course name
            return db.query(Course).filter(func.lower(Course.course_name) == name.lower()).first()

    def get_course_by_code(self, code: str) -> Course | None:
        with get_db_session() as db:
            return db.query(Course).filter(func.lower(Course.course_code) == code.lower()).first()

    def get_student_by_id(self, student_id: int) -> Student | None:
        with get_db_session() as db:
            return db.query(Student).filter(Student.id == student_id).first()

    def get_course_by_id(self, course_id: int) -> Course | None:
        with get_db_session() as db:
            return db.query(Course).filter(Course.id == course_id).first()

    def get_grade_by_id(self, grade_id: int) -> Grade | None:
        with get_db_session() as db:
            return db.query(Grade).filter(Grade.id == grade_id).first()


    # --- Update ---
    def update_student(self, student_id: int, first_name: str, last_name: str):
        with get_db_session() as db:
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                student.first_name = first_name
                student.last_name = last_name
                db.commit()

    def update_course(self, course_id: int, course_name: str, course_code: str):
        with get_db_session() as db:
            course = db.query(Course).filter(Course.id == course_id).first()
            if course:
                course.course_name = course_name
                course.course_code = course_code
                db.commit()

    def update_grade(self, grade_id: int, assignment_name: str, score: float):
        with get_db_session() as db:
            grade = db.query(Grade).filter(Grade.id == grade_id).first()
            if grade:
                grade.assignment_name = assignment_name
                grade.score = score
                db.commit()

    # --- Delete ---
    def delete_student(self, student_id: int):
        with get_db_session() as db:
            db.query(Grade).filter(Grade.student_id == student_id).delete()
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                db.delete(student)
                db.commit()

    def delete_course(self, course_id: int):
        with get_db_session() as db:
            db.query(Grade).filter(Grade.course_id == course_id).delete()
            course = db.query(Course).filter(Course.id == course_id).first()
            if course:
                db.delete(course)
                db.commit()

    def delete_grade(self, grade_id: int):
        with get_db_session() as db:
            grade = db.query(Grade).filter(Grade.id == grade_id).first()
            if grade:
                db.delete(grade)
                db.commit()
