import asyncio
from datetime import datetime

async def import_students_from_csv(filepath, class_id, data_service, assistant_service):
    """
    Parses and imports student data from a CSV file using a single AI call.
    """
    # --- Step 1: Read the entire file content ---
    try:
        with open(filepath, mode='r', encoding='utf-8', errors='ignore') as file:
            csv_content = file.read()
    except Exception as e:
        return 0, [f"Erro fatal ao ler o arquivo CSV: {e}"]

    # --- Step 2: Use the AI to parse the entire file in one go ---
    try:
        parsed_students = await assistant_service.parse_student_csv_with_ai(csv_content)
        if not parsed_students:
            return 0, ["A IA não conseguiu extrair nenhum aluno do arquivo."]
    except Exception as e:
        return 0, [f"Erro ao processar o arquivo com a IA: {e}"]

    # --- Step 3: Prepare the data for batch database insertion ---
    student_data_for_batch = []
    errors = []
    for i, student_data in enumerate(parsed_students, start=1):
        try:
            # Convert date string from AI to date object
            birth_date = None
            date_str = student_data.get('birth_date')
            if date_str:
                try:
                    # Strip whitespace from the date string before parsing
                    birth_date = datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
                except (ValueError, TypeError):
                    errors.append(f"Aluno '{student_data.get('full_name', 'N/A')}': Formato de data inválido ('{date_str}'). Data não será salva.")

            # Map status from AI to system status, ignoring case and whitespace
            status_str = student_data.get('status', '').strip().lower()
            status = "Active" if status_str == 'ativo' else "Inactive"
            status_detail = None if status == "Active" else student_data.get('status', '').strip()

            student_data_for_batch.append({
                'full_name': student_data.get('full_name'),
                'first_name': student_data.get('first_name'),
                'last_name': student_data.get('last_name'),
                'birth_date': birth_date,
                'status': status,
                'status_detail': status_detail,
            })
        except KeyError as e:
            errors.append(f"Item {i}: A resposta da IA não continha a chave esperada: {e}")

    if not student_data_for_batch:
        return 0, errors

    # --- Step 4: Execute the batch database operation ---
    try:
        data_service.batch_upsert_students_and_enroll(class_id, student_data_for_batch)
    except Exception as e:
        errors.append(f"Erro crítico ao salvar os dados no banco de dados: {e}")
        return 0, errors

    return len(student_data_for_batch), errors
