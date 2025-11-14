# -*- coding: utf-8 -*-

"""
Este módulo contém a função utilitária para orquestrar a importação de alunos
a partir de um arquivo CSV de forma assíncrona, sem bloquear a UI.
"""

import asyncio

async def import_students_from_csv(filepath: str, class_id: int, data_service) -> tuple[int, list]:
    """
    Lê um arquivo CSV e importa os dados dos alunos usando o DataService.

    A função lê o conteúdo do arquivo e, em seguida, chama o método síncrono
    `data_service.import_students_from_csv` em um executor de thread separado.
    Isso garante que a leitura do arquivo e o processamento do lado do servidor
    não bloqueiem o loop de eventos principal da aplicação (a UI).

    Args:
        filepath (str): O caminho para o arquivo CSV.
        class_id (int): O ID da turma para a qual os alunos serão matriculados.
        data_service: A instância do serviço de dados.

    Returns:
        tuple[int, list]: Uma tupla contendo o número de alunos importados
                          com sucesso e uma lista de mensagens de erro.
    """
    try:
        # Etapa 1: Ler o conteúdo do arquivo (I/O síncrono)
        # É rápido o suficiente para a maioria dos casos, mas poderia ser movido
        # para o executor se arquivos muito grandes fossem um problema.
        with open(filepath, mode='r', encoding='utf-8', errors='ignore') as file:
            file_content = file.read()
    except Exception as e:
        # Se a leitura falhar, retorna o erro imediatamente
        return 0, [f"Erro fatal ao ler o arquivo CSV: {e}"]

    try:
        # Etapa 2: Executa o método síncrono e bloqueante do DataService em um
        # executor de thread (ThreadPoolExecutor padrão).
        loop = asyncio.get_running_loop()

        result_dict = await loop.run_in_executor(
            None,  # Usa o executor padrão
            data_service.import_students_from_csv,
            class_id,
            file_content
        )

        # Etapa 3: Desempacota o dicionário retornado pelo DataService para a
        # tupla que a UI espera.
        imported_count = result_dict.get("imported_count", 0)
        errors = result_dict.get("errors", [])
        return imported_count, errors

    except Exception as e:
        # Captura quaisquer outros erros inesperados durante a execução
        return 0, [f"Ocorreu um erro inesperado durante a importação: {e}"]
