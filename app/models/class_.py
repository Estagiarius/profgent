# Importa os tipos de coluna necessários do SQLAlchemy para definir o modelo.
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Class, que representa uma turma no banco de dados.
# O nome do arquivo e da classe usa um underscore '_' para evitar conflito com a palavra-chave 'class' do Python.
class Class(Base):
    """
    Representa uma turma associada a um curso em um sistema educacional.

    Esta classe modela uma turma que pertence a um curso, com métodos de cálculo avaliativo e relacionadas
    a componentes como avaliações, aulas, matrículas e incidentes. A associação com outros modelos, como
    Course, Assessment ou Lesson, é feita por meio de relacionamentos SQLAlchemy.

    :ivar __tablename__: Nome da tabela no banco de dados.
    :type __tablename__: str
    :ivar id: Identificador único da turma, número inteiro, autoincrementável.
    :type id: int
    :ivar name: Nome único da turma, obrigatório.
    :type name: str
    :ivar course_id: Identificador do curso ao qual a turma pertence, obrigatório.
    :type course_id: int
    :ivar calculation_method: Método de cálculo aplicado na turma.
        Pode ser 'arithmetic' (média aritmética) ou 'weighted' (média ponderada).
    :type calculation_method: Enum('arithmetic', 'weighted')
    :ivar course: Relacionamento com o modelo Course via chave estrangeira.
        Representa o curso ao qual a turma pertence.
    :type course: Course
    :ivar enrollments: Relacionamento com o modelo ClassEnrollment.
        Representa as matrículas realizadas na turma.
    :type enrollments: list[ClassEnrollment]
    :ivar assessments: Relacionamento com o modelo Assessment.
        Representa as avaliações associadas à turma. Associadas com `cascade="all, delete-orphan"`.
    :type assessments: list[Assessment]
    :ivar lessons: Relacionamento com o modelo Lesson.
        Representa as aulas associadas à turma.
    :type lessons: list[Lesson]
    :ivar incidents: Relacionamento com o modelo Incident.
        Representa os incidentes registrados na turma.
    :type incidents: list[Incident]
    """
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'classes'

    # Define a coluna 'id' como um inteiro, chave primária e com autoincremento.
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Define a coluna 'name' como uma string que não pode ser nula e deve ser única.
    name = Column(String, nullable=False, unique=True)
    # Define a coluna 'course_id' como um inteiro que é uma chave estrangeira, referenciando a coluna 'id' da tabela 'courses'.
    # Este campo é obrigatório.
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    # Define a coluna 'calculation_method' usando o tipo Enum do SQLAlchemy.
    # Isso restringe os valores a 'arithmetic' (média aritmética) ou 'weighted' (média ponderada).
    # O campo é obrigatório e o valor padrão é 'arithmetic'.
    calculation_method = Column(Enum('arithmetic', 'weighted', name='calculation_methods'), nullable=False, default='arithmetic')

    # Define o relacionamento com o modelo Course. 'back_populates' cria a referência inversa no modelo Course.
    course = relationship("Course", back_populates="classes")
    # Define o relacionamento com ClassEnrollment (matrículas), criando a referência inversa.
    enrollments = relationship("ClassEnrollment", back_populates="class_", cascade="all, delete-orphan")
    # Define o relacionamento com Assessment (avaliações). 'backref' é uma forma mais simples de criar a referência inversa.
    # 'cascade="all, delete-orphan"' garante que as avaliações de uma turma sejam excluídas se a turma for excluída.
    assessments = relationship("Assessment", backref="class_", cascade="all, delete-orphan")
    # Define o relacionamento com Lesson (aulas).
    lessons = relationship("Lesson", back_populates="class_", cascade="all, delete-orphan")
    # Define o relacionamento com Incident (incidentes).
    incidents = relationship("Incident", back_populates="class_", cascade="all, delete-orphan")

    # Define uma representação em string para o objeto Class, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com o id e o nome da turma.
        return f"<Class(id={self.id}, name='{self.name}')>"
