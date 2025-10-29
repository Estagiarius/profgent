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

    def add_student(self, first_name: str, last_name: str) -> Student | None:
        """Adds a new student to the database."""
        if not first_name or not last_name:
            return None

        today = date.today().isoformat()
        new_student = Student(first_name=first_name, last_name=last_name, enrollment_date=today)
        return self.student_repo.add(new_student)

    def add_course(self, course_name: str, course_code: str) -> Course | None:
        """Adds a new course to the database."""
        if not course_name or not course_code:
            return None

        new_course = Course(course_name=course_name, course_code=course_code)
        return self.course_repo.add(new_course)

    def add_grade(self, student_id: int, course_id: int, assignment_name: str, score: float) -> Grade | None:
        """Adds a new grade to the database."""
        if not all([student_id, course_id, assignment_name, score is not None]):
            return None

        today = date.today().isoformat()
        new_grade = Grade(
            student_id=student_id,
            course_id=course_id,
            assignment_name=assignment_name,
            score=score,
            date_recorded=today
        )
        return self.grade_repo.add(new_grade)

    def get_all_students(self) -> list[Student]:
        """Returns a list of all students."""
        return self.student_repo.get_all()

    def get_all_courses(self) -> list[Course]:
        """Returns a list of all courses."""
        return self.course_repo.get_all()

    def get_student_count(self) -> int:
        """Returns the total number of students."""
        return self.db_session.query(Student).count()

    def get_course_count(self) -> int:
        """Returns the total number of courses."""
        return self.db_session.query(Course).count()

    def __del__(self):
        """Closes the database session when the service is destroyed."""
        self.db_session.close()
