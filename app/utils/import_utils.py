import csv
import asyncio
from datetime import datetime

async def import_students_from_csv(filepath, class_id, data_service, assistant_service):
    """
    Core logic for importing students from a CSV file.
    This function is UI-independent, asynchronous, and performs AI and DB operations in batches.
    """
    errors = []
    students_to_process = []

    # --- Step 1: Read and parse the CSV file ---
    try:
        with open(filepath, mode='r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            header_row_index = -1
            header = []
            for i, line in enumerate(lines):
                if 'Nome do Aluno' in line and 'Situação do Aluno' in line:
                    header = [h.strip() for h in line.strip().split(';')]
                    header_row_index = i
                    break

            if header_row_index == -1:
                return 0, ["Cabeçalho não encontrado no arquivo CSV."]

            # Map header names to indices
            try:
                name_idx = header.index('Nome do Aluno')
                status_idx = header.index('Situação do Aluno')
                birth_date_idx = header.index('Data de Nascimento') if 'Data de Nascimento' in header else -1
            except ValueError as e:
                return 0, [f"Coluna de cabeçalho essencial não encontrada: {e}"]

            csv_data = lines[header_row_index + 1:]
            reader = csv.reader(csv_data, delimiter=';')

            for row_num, row in enumerate(reader, start=1):
                if not row or len(row) <= max(name_idx, status_idx):
                    continue

                full_name = row[name_idx].strip()
                if not full_name:
                    continue

                students_to_process.append({
                    'full_name': full_name,
                    'status_str': row[status_idx].strip(),
                    'birth_date_str': row[birth_date_idx].strip() if birth_date_idx != -1 and birth_date_idx < len(row) else None,
                    'row_num': row_num
                })

    except Exception as e:
        return 0, [f"Erro fatal ao ler o arquivo CSV: {e}"]

    # --- Step 2: Perform AI name splitting in parallel ---
    if not students_to_process:
        return 0, ["Nenhum aluno válido encontrado no arquivo."]

    name_splitting_tasks = [assistant_service.split_full_name(s['full_name']) for s in students_to_process]
    try:
        split_name_results = await asyncio.gather(*name_splitting_tasks)
    except Exception as e:
        return 0, [f"Erro crítico ao contatar o serviço de IA: {e}. A importação foi cancelada."]

    # --- Step 3: Prepare the data for batch processing ---
    student_data_for_batch = []
    for i, student_data in enumerate(students_to_process):
        try:
            first_name, last_name = split_name_results[i]

            birth_date = None
            if student_data['birth_date_str']:
                try:
                    birth_date = datetime.strptime(student_data['birth_date_str'], "%d/%m/%Y").date()
                except ValueError:
                    errors.append(f"Linha {student_data['row_num']}: Formato de data inválido para '{student_data['full_name']}'. Data não será salva.")

            status = "Active" if student_data['status_str'] == 'Ativo' else "Inactive"
            status_detail = None if status == "Active" else student_data['status_str']

            student_data_for_batch.append({
                'full_name': student_data['full_name'],
                'first_name': first_name,
                'last_name': last_name,
                'birth_date': birth_date,
                'status': status,
                'status_detail': status_detail,
            })
        except Exception as e:
            errors.append(f"Linha {student_data['row_num']}: Erro inesperado ao preparar dados para '{student_data['full_name']}': {e}")

    # --- Step 4: Execute the batch database operation ---
    if student_data_for_batch:
        try:
            data_service.batch_upsert_students_and_enroll(class_id, student_data_for_batch)
        except Exception as e:
            errors.append(f"Erro crítico ao salvar os dados no banco de dados: {e}")
            return 0, errors

    return len(student_data_for_batch), errors
