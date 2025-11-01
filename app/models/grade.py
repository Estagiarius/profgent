from sqlalchemy import Column, Integer, String, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class Grade(Base):
    __tablename__ = 'grades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False)
    score = Column(Float, nullable=False)
    date_recorded = Column(String, nullable=False) # Should be a DateTime in a real app

    student = relationship("Student", back_populates="grades")
    assessment = relationship("Assessment")

    __table_args__ = (
        CheckConstraint('score >= 0', name='check_score_positive'),
    )

    def __repr__(self):
        return f"<Grade(id={self.id}, student_id={self.student_id}, assessment_id={self.assessment_id}, score={self.score})>"
