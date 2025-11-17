from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)

    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    class_ = relationship("Class", back_populates="lessons")

    def __repr__(self):
        return f"<Lesson(id={self.id}, title='{self.title}', class_id={self.class_id})>"
