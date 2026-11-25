# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
import asyncio

def _read_text_with_fallback(filepath: str) -> str:
    """Lê o arquivo texto testando codificações comuns em sistemas brasileiros."""
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(filepath, mode="r", encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    with open(filepath, mode="r", encoding="utf-8", errors="replace") as file:
        return file.read()


async def async_import_students(filepath: str, class_id: int, data_service) -> tuple[int, list]:
    """
    Importa registros de estudantes para uma classe específica a partir de um
    arquivo CSV de forma assíncrona. O processo de leitura do arquivo é realizado
    em uma thread separada para evitar o bloqueio da interface ou outras operações
    assíncronas. Após a leitura, os dados são enviados para um serviço sincronizado
    (DataService) que realiza a lógica de importação.

    :param filepath: Caminho completo para o arquivo CSV que contém os dados dos
        estudantes a serem importados.
    :type filepath: str
    :param class_id: Identificador único da classe onde os estudantes serão
        importados.
    :type class_id: int
    :param data_service: Serviço responsável por processar e importar os dados de
        estudantes a partir do conteúdo do arquivo.
    :type data_service: objeto que implementa o método
        `import_students_from_csv(class_id, file_content) -> dict`
    :return: Tupla contendo a quantidade de estudantes importados e uma lista de
        mensagens de erro (se houver).
    :rtype: tuple[int, list]
    """
    try:
        # Passo 1: Lê o arquivo em thread separada com fallback de codificação para não bloquear a UI.
        loop = asyncio.get_running_loop()
        file_content = await loop.run_in_executor(None, _read_text_with_fallback, filepath)

    except Exception as e:
        return 0, [f"Erro fatal ao ler o arquivo CSV: {e}"]

    try:
        # Step 2: Run the synchronous DataService method in a thread.
        result_dict = await loop.run_in_executor(
            None,
            data_service.import_students_from_csv,
            class_id,
            file_content
        )

        imported_count = result_dict.get("imported_count", 0)
        errors = result_dict.get("errors", [])
        return imported_count, errors

    except Exception as e:
        return 0, [f"Ocorreu um erro inesperado durante a importação: {e}"]
