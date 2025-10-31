from sqlalchemy import Column, Integer, String, Date
from app.models.base import Base

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    enrollment_date = Column(String, nullable=False)
    status = Column(String, nullable=True) # Ex: "Active", "Transferred", "Inactive"

    def __repr__(self):
        return f"<Student(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}')>"
