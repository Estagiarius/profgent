from typing import Generic, TypeVar, Type
from sqlalchemy.orm import Session
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class Repository(Generic[ModelType]):
    def __init__(self, session: Session, model: Type[ModelType]):
        self.session = session
        self.model = model

    def get(self, id: int) -> ModelType | None:
        return self.session.get(self.model, id)

    def get_all(self) -> list[ModelType]:
        return self.session.query(self.model).all()

    def add(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity: ModelType):
        self.session.delete(entity)
        self.session.commit()
