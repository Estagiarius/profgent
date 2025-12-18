from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class Attendance(Base):
    """
    Representa o registro de frequência de um aluno em uma aula.

    :ivar id: Identificador único do registro de frequência.
    :ivar lesson_id: ID da aula (Lesson).
    :ivar student_id: ID do aluno (Student).
    :ivar status: Status da presença. 'P' (Presente), 'F' (Falta), 'J' (Justificada), 'A' (Atraso).
    """
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    status = Column(String, nullable=False, default='P')

    lesson = relationship("Lesson", back_populates="attendance_records")
    student = relationship("Student")

    __table_args__ = (
        UniqueConstraint('lesson_id', 'student_id', name='_lesson_student_attendance_uc'),
    )

    def __repr__(self):
        return f"<Attendance(lesson_id={self.lesson_id}, student_id={self.student_id}, status='{self.status}')>"
