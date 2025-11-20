# Importa os tipos de coluna necessários do SQLAlchemy.
from sqlalchemy import Column, Integer, Text, Date, ForeignKey
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Incident, que representa uma ocorrência ou incidente envolvendo um aluno.
class Incident(Base):
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'incidents'

    # Define a coluna 'id' como um inteiro e chave primária.
    id = Column(Integer, primary_key=True)
    # Define a coluna 'date' como do tipo Date (data), não podendo ser nula.
    date = Column(Date, nullable=False)
    # Define a coluna 'description' como do tipo Text (texto longo), não podendo ser nula.
    description = Column(Text, nullable=False)

    # Define a coluna 'class_id' como uma chave estrangeira para a tabela 'classes'. Não pode ser nula.
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    # Define a coluna 'student_id' como uma chave estrangeira para a tabela 'students'. Não pode ser nula.
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)

    # Define o relacionamento com o modelo Class. 'back_populates' cria a referência inversa no modelo Class.
    class_ = relationship("Class", back_populates="incidents")
    # Define o relacionamento com o modelo Student. 'back_populates' cria a referência inversa no modelo Student.
    student = relationship("Student", back_populates="incidents")

    # Define uma representação em string para o objeto Incident, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com o id do incidente e os IDs do aluno e da turma.
        return f"<Incident(id={self.id}, student_id={self.student_id}, class_id={self.class_id})>"
