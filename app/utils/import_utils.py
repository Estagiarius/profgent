import asyncio

async def async_import_students(filepath: str, class_id: int, data_service) -> tuple[int, list]:
    """
    Orchestrates the student import process asynchronously.

    This function first reads the CSV file content in a separate thread,
    then passes the content to the DataService's import method, which is
    also run in a thread to handle the database transaction without
    blocking the UI. This two-step process prevents database deadlocks.
    """
    try:
        # Step 1: Read the file content asynchronously to not block the UI.
        loop = asyncio.get_running_loop()
        with open(filepath, mode='r', encoding='utf-8', errors='ignore') as file:
            file_content = await loop.run_in_executor(None, file.read, -1)

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
