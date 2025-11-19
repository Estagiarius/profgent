# Importa a biblioteca 'asyncio' para gerenciar operações assíncronas.
import asyncio

# Define uma função assíncrona que orquestra a importação de alunos.
async def async_import_students(filepath: str, class_id: int, data_service) -> tuple[int, list]:
    """
    Orquestra o processo de importação de alunos de forma assíncrona.

    Esta função primeiro lê o conteúdo do arquivo CSV em uma thread separada,
    depois passa o conteúdo para o método de importação do DataService, que também
    é executado em uma thread para lidar com a transação do banco de dados sem
    bloquear a UI. Este processo de duas etapas evita deadlocks (travamentos) do banco de dados.

    Args:
        filepath: O caminho do arquivo CSV a ser importado.
        class_id: O ID da turma para a qual os alunos serão matriculados.
        data_service: A instância do DataService.

    Returns:
        Uma tupla contendo o número de alunos importados e uma lista de erros.
    """
    # Bloco try/except para capturar erros durante a leitura do arquivo.
    try:
        # Passo 1: Ler o conteúdo do arquivo de forma assíncrona para não bloquear a UI.
        # Obtém o loop de eventos asyncio atualmente em execução.
        loop = asyncio.get_running_loop()
        # Abre o arquivo CSV. 'utf-8' é uma codificação comum, 'errors='ignore'' evita falhas com caracteres inválidos.
        with open(filepath, mode='r', encoding='utf-8', errors='ignore') as file:
            # `run_in_executor` executa uma função bloqueante (como file.read()) em uma thread separada
            # sem bloquear o loop de eventos principal, e retorna o resultado quando estiver pronto.
            file_content = await loop.run_in_executor(None, file.read)

    except Exception as e:
        # Se ocorrer um erro ao ler o arquivo, retorna 0 importados e a mensagem de erro.
        return 0, [f"Erro fatal ao ler o arquivo CSV: {e}"]

    # Bloco try/except para capturar erros durante a importação para o banco de dados.
    try:
        # Passo 2: Executar o método síncrono do DataService em uma thread.
        # Isso é crucial porque a operação do banco de dados pode ser demorada e bloquearia a UI.
        result_dict = await loop.run_in_executor(
            None,  # Usa o executor de thread padrão.
            data_service.import_students_from_csv, # A função a ser executada.
            class_id,                             # O primeiro argumento para a função.
            file_content                          # O segundo argumento para a função.
        )

        # Extrai os resultados do dicionário retornado pelo DataService.
        imported_count = result_dict.get("imported_count", 0)
        errors = result_dict.get("errors", [])
        # Retorna o resultado final.
        return imported_count, errors

    except Exception as e:
        # Se ocorrer um erro inesperado durante a chamada do DataService.
        return 0, [f"Ocorreu um erro inesperado durante a importação: {e}"]
