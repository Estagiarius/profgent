from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base

class Class(Base):
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    calculation_method = Column(Enum('arithmetic', 'weighted', name='calculation_methods'), nullable=False, default='arithmetic')

    course = relationship("Course", back_populates="classes")
    enrollments = relationship("ClassEnrollment", back_populates="class_")
    assessments = relationship("Assessment", backref="class_", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Class(id={self.id}, name='{self.name}')>"
