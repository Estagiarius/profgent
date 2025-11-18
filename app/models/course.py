# Importa os tipos de coluna necessários do SQLAlchemy para definir o modelo.
from sqlalchemy import Column, Integer, String
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Course, que representa uma disciplina ou curso (ex: Matemática, História) no banco de dados.
class Course(Base):
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'courses'

    # Define a coluna 'id' como um inteiro, chave primária e com autoincremento.
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Define a coluna 'course_name' como uma string que não pode ser nula e deve ser única.
    course_name = Column(String, nullable=False, unique=True)
    # Define a coluna 'course_code' como uma string que deve ser única.
    course_code = Column(String, unique=True)

    # Define o relacionamento com o modelo Class. Um curso pode ter várias turmas.
    # 'back_populates' cria a referência inversa no modelo Class.
    classes = relationship("Class", back_populates="course")

    # Define uma representação em string para o objeto Course, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com o id e o nome do curso.
        return f"<Course(id={self.id}, course_name='{self.course_name}')>"
