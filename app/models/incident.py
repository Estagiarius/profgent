from datetime import date
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Incident(Base):
    __tablename__ = 'incidents'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)

    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)

    class_ = relationship("Class", back_populates="incidents")
    student = relationship("Student", back_populates="incidents")

    def __repr__(self):
        return f"<Incident(id={self.id}, student_id={self.student_id}, class_id={self.class_id})>"
