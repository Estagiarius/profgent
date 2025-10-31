from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class ClassEnrollment(Base):
    __tablename__ = 'class_enrollments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    call_number = Column(Integer, nullable=False)

    student = relationship("Student")
    class_ = relationship("Class", back_populates="enrollments")

    __table_args__ = (
        UniqueConstraint('class_id', 'student_id', name='_class_student_uc'),
        UniqueConstraint('class_id', 'call_number', name='_class_call_number_uc'),
    )

    def __repr__(self):
        return f"<ClassEnrollment(class_id={self.class_id}, student_id={self.student_id}, call_number={self.call_number})>"
