from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Class(Base):
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)

    course = relationship("Course")
    enrollments = relationship("ClassEnrollment", back_populates="class_")

    def __repr__(self):
        return f"<Class(id={self.id}, name='{self.name}')>"
