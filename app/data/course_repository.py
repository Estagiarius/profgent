from sqlalchemy.orm import Session
from app.data.base_repository import Repository
from app.models.course import Course

class CourseRepository(Repository[Course]):
    def __init__(self, session: Session):
        super().__init__(session, Course)
