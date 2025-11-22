# Importa os tipos de coluna necessários do SQLAlchemy.
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Lesson, que representa uma aula ou plano de aula.
class Lesson(Base):
    """
    Representa o modelo correspondente à entidade 'Lesson' (aula) no banco de dados.

    Esta classe mapeia a tabela 'lessons' no banco de dados e define os atributos e
    relacionamentos associados a uma aula. Cada instância desta classe representa
    uma linha na tabela de 'lessons'.

    :ivar id: Chave primária que identifica exclusivamente uma aula.
    :type id: int
    :ivar date: Data da realização da aula.
    :type date: datetime.date
    :ivar title: Título da aula.
    :type title: str
    :ivar content: Conteúdo descritivo da aula. Pode ser nulo.
    :type content: str | None
    :ivar class_subject_id: Chave estrangeira que associa a aula a uma disciplina de uma turma.
    :type class_subject_id: int
    :ivar class_subject: Relacionamento que conecta a aula com a respectiva instância de ClassSubject.
    :type class_subject: ClassSubject
    """
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'lessons'

    # Define a coluna 'id' como um inteiro e chave primária.
    id = Column(Integer, primary_key=True)
    # Define a coluna 'date' como do tipo Date (data), não podendo ser nula.
    date = Column(Date, nullable=False)
    # Define a coluna 'title' (título) como uma string, não podendo ser nula.
    title = Column(String, nullable=False)
    # Define a coluna 'content' (conteúdo) como do tipo Text (texto longo), podendo ser nula.
    content = Column(Text, nullable=True)

    # Define a coluna 'class_subject_id' como uma chave estrangeira para a tabela 'class_subjects'. Não pode ser nula.
    class_subject_id = Column(Integer, ForeignKey('class_subjects.id'), nullable=False)
    # Define o relacionamento com o modelo ClassSubject.
    class_subject = relationship("ClassSubject", back_populates="lessons")

    # Define uma representação em string para o objeto Lesson, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com o id, título da aula e o ID da disciplina da turma.
        return f"<Lesson(id={self.id}, title='{self.title}', class_subject_id={self.class_subject_id})>"
