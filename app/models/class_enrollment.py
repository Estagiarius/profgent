# Importa os tipos de coluna necessários e a restrição de unicidade (UniqueConstraint) do SQLAlchemy.
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe ClassEnrollment, que representa a matrícula de um aluno em uma turma.
class ClassEnrollment(Base):
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'class_enrollments'

    # Define a coluna 'id' como um inteiro, chave primária e com autoincremento.
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Define a coluna 'class_id' como uma chave estrangeira para a tabela 'classes'. Não pode ser nula.
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    # Define a coluna 'student_id' como uma chave estrangeira para a tabela 'students'. Não pode ser nula.
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    # Define a coluna 'call_number' (número de chamada) como um inteiro. Não pode ser nula.
    call_number = Column(Integer, nullable=False)
    # Define a coluna 'status' como uma string, com valor padrão 'Active'. Ex: "Active", "Inactive".
    status = Column(String, nullable=False, default='Active')
    # Define a coluna 'status_detail' como uma string que pode ser nula. Ex: "Transferido".
    status_detail = Column(String, nullable=True)

    # Define o relacionamento com o modelo Student. Permite acessar os dados do aluno a partir da matrícula.
    student = relationship("Student")
    # Define o relacionamento com o modelo Class. 'back_populates' cria a referência inversa no modelo Class.
    class_ = relationship("Class", back_populates="enrollments")

    # Define restrições a nível de tabela.
    __table_args__ = (
        # Garante que a combinação de 'class_id' e 'student_id' seja única. Um aluno só pode se matricular uma vez na mesma turma.
        UniqueConstraint('class_id', 'student_id', name='_class_student_uc'),
        # Garante que a combinação de 'class_id' e 'call_number' seja única. Não pode haver dois números de chamada iguais na mesma turma.
        UniqueConstraint('class_id', 'call_number', name='_class_call_number_uc'),
    )

    # Define uma representação em string para o objeto ClassEnrollment, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com os IDs da turma, do aluno e o número de chamada.
        return f"<ClassEnrollment(class_id={self.class_id}, student_id={self.student_id}, call_number={self.call_number})>"
