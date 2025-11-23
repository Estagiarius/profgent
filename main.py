import logging
import os
from sqlalchemy import inspect
from app.ui.main_app import MainApp
from app.data.database import engine, Base
# Importa o DataService singleton (instância compartilhada) para garantir consistência com as ferramentas da IA
from app.services import data_service
# Importa o AssistantService
from app.services.assistant_service import AssistantService

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()  # Também exibe no console para debug durante o desenvolvimento
    ]
)

def initialize_database():
    """
    Verifica e inicializa o banco de dados de forma robusta.
    Usa 'inspect' para verificar tabelas em vez de apenas a existência do arquivo.
    Isso previne erros quando o arquivo existe mas está vazio ou corrompido.
    """
    try:
        inspector = inspect(engine)
        # Obtém as tabelas existentes no banco
        existing_tables = inspector.get_table_names()

        if not existing_tables:
            logging.info("Banco de dados vazio ou inexistente. Criando nova estrutura de tabelas...")
            Base.metadata.create_all(bind=engine)
            logging.info("Banco de dados inicializado com sucesso.")
        else:
            logging.info(f"Banco de dados encontrado com as seguintes tabelas: {', '.join(existing_tables)}")
            # Executa create_all mesmo assim para garantir que qualquer nova tabela definida no código seja criada.
            # O create_all do SQLAlchemy é inteligente e ignora tabelas que já existem.
            Base.metadata.create_all(bind=engine)

    except Exception as e:
        logging.critical(f"Falha crítica na inicialização do banco de dados: {e}")
        # Relança a exceção para ser capturada no bloco principal e encerrar o programa
        raise

def main():
    try:
        logging.info("Iniciando aplicação Academic Management System...")

        # 1. Inicializa a camada de dados
        initialize_database()

        # 2. Inicializa os serviços
        # O data_service já foi importado como singleton.
        # Inicializa o serviço do assistente (que carrega configurações e ferramentas)
        assistant_service = AssistantService()

        # 3. Inicializa a Interface Gráfica
        logging.info("Inicializando interface gráfica...")
        app = MainApp(data_service=data_service, assistant_service=assistant_service)

        # 4. Inicia o loop principal
        app.mainloop()

        logging.info("Aplicação encerrada pelo usuário.")

    except Exception as e:
        logging.critical(f"A aplicação encontrou um erro fatal e não pôde iniciar: {e}", exc_info=True)
        print(f"\nERRO FATAL: A aplicação falhou. Verifique o arquivo 'app.log' para detalhes.\nErro: {e}")

if __name__ == "__main__":
    main()
