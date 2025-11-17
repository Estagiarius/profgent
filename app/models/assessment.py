from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.models.base import Base

class Assessment(Base):
    __tablename__ = 'assessments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    weight = Column(Float, nullable=False, default=1.0)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)

    def __repr__(self):
        return f"<Assessment(id={self.id}, name='{self.name}', weight={self.weight})>"
