# Importa os tipos de coluna necessários do SQLAlchemy.
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Lesson, que representa uma aula ou plano de aula.
class Lesson(Base):
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

    # Define a coluna 'class_id' como uma chave estrangeira para a tabela 'classes'. Não pode ser nula.
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    # Define o relacionamento com o modelo Class. 'back_populates' cria a referência inversa no modelo Class.
    class_ = relationship("Class", back_populates="lessons")

    # Define uma representação em string para o objeto Lesson, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com o id, título da aula e o ID da turma.
        return f"<Lesson(id={self.id}, title='{self.title}', class_id={self.class_id})>"
