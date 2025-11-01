from datetime import date
from sqlalchemy import func
from app.data.database import get_db_session
from app.models.student import Student
from app.models.course import Course
from app.models.grade import Grade
from app.models.class_ import Class
from app.models.class_enrollment import ClassEnrollment
from app.models.assessment import Assessment

class DataService:
    # --- Student Methods ---
    def add_student(self, first_name: str, last_name: str, status: str = "Active") -> Student | None:
        if not first_name or not last_name: return None
        with get_db_session() as db:
            existing = db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == f"{first_name} {last_name}".lower()).first()
            if existing:
                return existing
            today = date.today().isoformat()
            new_student = Student(first_name=first_name, last_name=last_name, enrollment_date=today, status=status)
            db.add(new_student)
            db.commit()
            db.refresh(new_student)
            return new_student

    def get_all_students(self) -> list[Student]:
        with get_db_session() as db:
            return db.query(Student).order_by(Student.first_name).all()

    def get_student_by_name(self, name: str) -> Student | None:
        with get_db_session() as db:
            return db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == name.lower()).first()

    def update_student(self, student_id: int, first_name: str, last_name: str, status: str):
        with get_db_session() as db:
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                student.first_name = first_name
                student.last_name = last_name
                student.status = status
                db.commit()

    def delete_student(self, student_id: int):
        with get_db_session() as db:
            db.query(Grade).filter(Grade.student_id == student_id).delete()
            db.query(ClassEnrollment).filter(ClassEnrollment.student_id == student_id).delete()
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                db.delete(student)
                db.commit()

    def get_student_count(self) -> int:
        with get_db_session() as db:
            return db.query(Student).count()

    # --- Course Methods ---
    def add_course(self, course_name: str, course_code: str) -> Course | None:
        if not course_name or not course_code: return None
        new_course = Course(course_name=course_name, course_code=course_code)
        with get_db_session() as db:
            db.add(new_course)
            db.commit()
            db.refresh(new_course)
            return new_course

    def get_all_courses(self) -> list[Course]:
        with get_db_session() as db:
            return db.query(Course).order_by(Course.course_name).all()

    def get_course_by_name(self, name: str) -> Course | None:
        with get_db_session() as db:
            return db.query(Course).filter(func.lower(Course.course_name) == name.lower()).first()

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

    def get_course_by_id(self, course_id: int) -> Course | None:
        with get_db_session() as db:
            return db.query(Course).filter(Course.id == course_id).first()

    def update_course(self, course_id: int, course_name: str, course_code: str):
        with get_db_session() as db:
            course = db.query(Course).filter(Course.id == course_id).first()
            if course:
                course.course_name = course_name
                course.course_code = course_code
                db.commit()

    def delete_course(self, course_id: int):
        # This is more complex now. A course can have multiple classes.
        # The UI should probably handle this by deleting classes first.
        # For now, we'll just delete the course if it has no classes.
        with get_db_session() as db:
            course = db.query(Course).filter(Course.id == course_id).first()
            if course:
                if course.classes:
                    # Or raise an exception to be caught by the UI
                    return
                db.delete(course)
                db.commit()

    def get_course_count(self) -> int:
        with get_db_session() as db:
            return db.query(Course).count()

    # --- Class (Turma) Methods ---
    def create_class(self, name: str, course_id: int, calculation_method: str = 'arithmetic') -> Class | None:
        if not name or not course_id: return None
        new_class = Class(name=name, course_id=course_id, calculation_method=calculation_method)
        with get_db_session() as db:
            db.add(new_class)
            db.commit()
            db.refresh(new_class)
            return new_class

    def get_all_classes(self) -> list[Class]:
        with get_db_session() as db:
            return db.query(Class).order_by(Class.name).all()

    def get_class_by_id(self, class_id: int) -> Class | None:
        with get_db_session() as db:
            return db.query(Class).filter(Class.id == class_id).first()

    def add_student_to_class(self, student_id: int, class_id: int, call_number: int) -> ClassEnrollment | None:
        if not all([student_id, class_id, call_number is not None]): return None
        with get_db_session() as db:
            existing = db.query(ClassEnrollment).filter_by(student_id=student_id, class_id=class_id).first()
            if existing:
                existing.call_number = call_number
                db.commit()
                return existing
            enrollment = ClassEnrollment(student_id=student_id, class_id=class_id, call_number=call_number)
            db.add(enrollment)
            db.commit()
            db.refresh(enrollment)
            return enrollment

    def get_enrollments_for_class(self, class_id: int) -> list[ClassEnrollment]:
        with get_db_session() as db:
            return db.query(ClassEnrollment).filter(ClassEnrollment.class_id == class_id).order_by(ClassEnrollment.call_number).all()

    # --- Assessment Methods ---
    def add_assessment(self, class_id: int, name: str, weight: float) -> Assessment | None:
        if not all([class_id, name, weight is not None]): return None
        assessment = Assessment(class_id=class_id, name=name, weight=weight)
        with get_db_session() as db:
            db.add(assessment)
            db.commit()
            db.refresh(assessment)
            return assessment

    # --- Grade Methods ---
    def add_grade(self, student_id: int, assessment_id: int, score: float) -> Grade | None:
        if not all([student_id, assessment_id, score is not None]): return None
        today = date.today().isoformat()
        new_grade = Grade(student_id=student_id, assessment_id=assessment_id, score=score, date_recorded=today)
        with get_db_session() as db:
            db.add(new_grade)
            db.commit()
            db.refresh(new_grade)
            return new_grade

    def get_all_grades(self) -> list[Grade]:
        with get_db_session() as db:
            return db.query(Grade).all()

    def get_grades_for_class(self, class_id: int) -> list[Grade]:
        with get_db_session() as db:
            return db.query(Grade).join(Assessment).filter(Assessment.class_id == class_id).all()

    def delete_grade(self, grade_id: int):
        with get_db_session() as db:
            grade = db.query(Grade).filter(Grade.id == grade_id).first()
            if grade:
                db.delete(grade)
                db.commit()
