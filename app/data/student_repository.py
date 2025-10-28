from sqlalchemy.orm import Session
from app.data.base_repository import Repository
from app.models.student import Student

class StudentRepository(Repository[Student]):
    def __init__(self, session: Session):
        super().__init__(session, Student)
