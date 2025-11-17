# Importa os tipos de coluna necessários do SQLAlchemy.
from sqlalchemy import Column, Integer, String, Date
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Student, que representa um aluno no banco de dados.
class Student(Base):
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'students'

    # Define a coluna 'id' como um inteiro, chave primária e com autoincremento.
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Define a coluna 'first_name' (primeiro nome) como uma string, não podendo ser nula.
    first_name = Column(String, nullable=False)
    # Define a coluna 'last_name' (sobrenome) como uma string, não podendo ser nula.
    last_name = Column(String, nullable=False)
    # Define a coluna 'birth_date' (data de nascimento) como do tipo Date, podendo ser nula.
    birth_date = Column(Date, nullable=True)
    # Define a coluna 'enrollment_date' (data de matrícula) como uma string, não podendo ser nula.
    enrollment_date = Column(String, nullable=False)

    # Define o relacionamento com o modelo Grade (notas). Um aluno pode ter várias notas.
    # 'back_populates' cria a referência inversa no modelo Grade.
    # 'cascade="all, delete-orphan"' garante que as notas de um aluno sejam excluídas se o aluno for excluído.
    grades = relationship("Grade", back_populates="student", cascade="all, delete-orphan")
    # Define o relacionamento com o modelo Incident (incidentes). Um aluno pode ter vários incidentes.
    incidents = relationship("Incident", back_populates="student")

    # Define uma representação em string para o objeto Student, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com id, nome, sobrenome e data de nascimento do aluno.
        return f"<Student(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', birth_date='{self.birth_date}')>"
