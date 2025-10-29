from sqlalchemy.orm import Session
from app.data.base_repository import Repository
from app.models.grade import Grade
from app.models.student import Student
from app.models.course import Course

class GradeRepository(Repository[Grade]):
    def __init__(self, session: Session):
        super().__init__(session, Grade)

    def find_grade_for_student(self, student_name: str, course_name: str) -> Grade | None:
        return (
            self.session.query(Grade)
            .join(Student)
            .join(Course)
            .filter(Student.first_name + " " + Student.last_name == student_name)
            .filter(Course.course_name == course_name)
            .first()
        )
