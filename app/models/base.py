# Importa a função declarative_base do SQLAlchemy ORM.
# Esta função é usada para criar uma classe base da qual todos os modelos ORM (tabelas) irão herdar.
from sqlalchemy.orm import declarative_base

# Cria a instância da classe Base.
# Qualquer classe de modelo que herdar de 'Base' será automaticamente registrada
# nos metadados do SQLAlchemy, permitindo que o ORM mapeie a classe para uma tabela no banco de dados.
Base = declarative_base()
