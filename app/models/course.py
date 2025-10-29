from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_name = Column(String, nullable=False, unique=True)
    course_code = Column(String, unique=True)

    def __repr__(self):
        return f"<Course(id={self.id}, course_name='{self.course_name}')>"
