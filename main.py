# Importa a classe principal da aplicação, MainApp, que gerencia a interface gráfica.
from app.ui.main_app import MainApp
# Importa o 'engine' e a 'Base' do SQLAlchemy para interagir com o banco de dados.
from app.data.database import engine, Base
# Importa todos os modelos para garantir que eles sejam registrados com os metadados do SQLAlchemy.
# Isso é crucial para que o `create_all` funcione corretamente.
from app.models import student, course, class_, class_enrollment, assessment, grade, lesson, incident
# Importa o módulo 'os' para interagir com o sistema operacional, como verificar a existência de arquivos.
import os

# Define a função que inicializa o banco de dados.
def initialize_database():
    """Cria o banco de dados e as tabelas caso ainda não existam."""
    # Obtém o caminho do arquivo do banco de dados a partir da URL do 'engine' do SQLAlchemy.
    db_path = engine.url.database
    # Verifica se o arquivo do banco de dados não existe no caminho especificado.
    if not os.path.exists(db_path):
        # Imprime uma mensagem informando que um novo banco de dados será criado.
        print("Banco de dados não encontrado. Criando um novo banco de dados e todas as tabelas...")
        # O objeto 'Base' contém os metadados de todas as nossas tabelas (modelos).
        # O método 'create_all' verifica a existência das tabelas antes de criá-las, então é seguro executá-lo.
        Base.metadata.create_all(bind=engine)
        # Imprime uma mensagem de sucesso após a inicialização.
        print("Banco de dados inicializado com sucesso.")
    # Caso o arquivo do banco de dados já exista.
    else:
        # Imprime uma mensagem informando que a criação foi pulada.
        print("O banco de dados já existe. A criação foi pulada.")


# Importa o DataService, responsável pela lógica de manipulação de dados.
from app.services.data_service import DataService
# Importa o AssistantService, responsável pela lógica do assistente de IA.
from app.services.assistant_service import AssistantService

# Define a função principal que executa a aplicação.
def main():
    # Chama a função para garantir que o banco de dados esteja pronto.
    initialize_database()

    # Cria uma instância dos serviços que serão usados pela aplicação.
    data_service = DataService()
    assistant_service = AssistantService()

    # Cria a instância principal da aplicação, injetando os serviços como dependências.
    app = MainApp(data_service=data_service, assistant_service=assistant_service)
    # Inicia o loop principal da interface gráfica, que a mantém em execução.
    app.mainloop()

# Verifica se o script está sendo executado diretamente (não importado como módulo).
if __name__ == "__main__":
    # Chama a função principal para iniciar a aplicação.
    main()
