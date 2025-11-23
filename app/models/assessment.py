# Importa os tipos de coluna necessários do SQLAlchemy para definir o modelo.
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Assessment, que representa uma avaliação (prova, trabalho, etc.) no banco de dados.
class Assessment(Base):
    """
    Representa a classe de modelo Assessment.

    A classe Assessment é utilizada para modelar uma entidade de avaliação, responsável
    por armazenar informações como nome, peso e associação com uma determinada disciplina de uma turma.
    Esse modelo é utilizado no contexto de persistência de dados em um banco relacional
    e é definido no formato de uma tabela SQL.

    :ivar id: Identificador único para cada avaliação.
    :type id: int
    :ivar name: Nome da avaliação, obrigatório.
    :type name: str
    :ivar weight: Peso atribuído à avaliação, obrigatório, com valor padrão de 1.0.
    :type weight: float
    :ivar class_subject_id: Identificador da disciplina da turma, referenciando uma chave estrangeira.
    :type class_subject_id: int
    """
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'assessments'

    # Define a coluna 'id' como um inteiro, chave primária e com autoincremento.
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Define a coluna 'name' como uma string que não pode ser nula (obrigatória).
    name = Column(String, nullable=False)
    # Define a coluna 'weight' como um número de ponto flutuante (decimal), obrigatório, com valor padrão 1.0.
    weight = Column(Float, nullable=False, default=1.0)
    # Define a coluna 'class_subject_id' como um inteiro que é uma chave estrangeira.
    class_subject_id = Column(Integer, ForeignKey('class_subjects.id'), nullable=False)

    # Relacionamento com ClassSubject
    class_subject = relationship("ClassSubject", back_populates="assessments")

    # Define uma representação em string para o objeto Assessment, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com o id, nome e peso da avaliação.
        return f"<Assessment(id={self.id}, name='{self.name}', weight={self.weight})>"
