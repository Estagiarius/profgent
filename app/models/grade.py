# Importa os tipos de coluna necessários e a restrição de verificação (CheckConstraint) do SQLAlchemy.
from sqlalchemy import Column, Integer, String, Float, ForeignKey, CheckConstraint
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Grade, que representa a nota de um aluno em uma avaliação.
class Grade(Base):
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'grades'

    # Define a coluna 'id' como um inteiro, chave primária e com autoincremento.
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Define a coluna 'student_id' como uma chave estrangeira para a tabela 'students'. Não pode ser nula.
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    # Define a coluna 'assessment_id' como uma chave estrangeira para a tabela 'assessments'. Não pode ser nula.
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False)
    # Define a coluna 'score' (nota) como um número de ponto flutuante. Não pode ser nula.
    score = Column(Float, nullable=False)
    # Define a coluna 'date_recorded' (data de registro) como uma string. Não pode ser nula.
    # Observação no código original: Em uma aplicação real, isso deveria ser do tipo DateTime.
    date_recorded = Column(String, nullable=False)

    # Define o relacionamento com o modelo Student. 'back_populates' cria a referência inversa no modelo Student.
    student = relationship("Student", back_populates="grades")
    # Define o relacionamento com o modelo Assessment. Permite acessar os dados da avaliação a partir da nota.
    assessment = relationship("Assessment")

    # Define restrições a nível de tabela.
    __table_args__ = (
        # Garante que o valor da coluna 'score' seja sempre maior ou igual a 0.
        CheckConstraint('score >= 0', name='check_score_positive'),
    )

    # Define uma representação em string para o objeto Grade, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com o id, ids do aluno e da avaliação, e a nota.
        return f"<Grade(id={self.id}, student_id={self.student_id}, assessment_id={self.assessment_id}, score={self.score})>"
