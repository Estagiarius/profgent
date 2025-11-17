# Importa os tipos de coluna necessários do SQLAlchemy para definir o modelo.
from sqlalchemy import Column, Integer, String, Float, ForeignKey
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Assessment, que representa uma avaliação (prova, trabalho, etc.) no banco de dados.
class Assessment(Base):
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'assessments'

    # Define a coluna 'id' como um inteiro, chave primária e com autoincremento.
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Define a coluna 'name' como uma string que não pode ser nula (obrigatória).
    name = Column(String, nullable=False)
    # Define a coluna 'weight' como um número de ponto flutuante (decimal), obrigatório, com valor padrão 1.0.
    weight = Column(Float, nullable=False, default=1.0)
    # Define a coluna 'class_id' como um inteiro que é uma chave estrangeira, referenciando a coluna 'id' da tabela 'classes'.
    # Este campo é obrigatório.
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)

    # Define uma representação em string para o objeto Assessment, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com o id, nome e peso da avaliação.
        return f"<Assessment(id={self.id}, name='{self.name}', weight={self.weight})>"
