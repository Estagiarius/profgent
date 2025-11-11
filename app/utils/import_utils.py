import csv
import asyncio
from datetime import datetime

async def import_students_from_csv(filepath, class_id, data_service, assistant_service):
    """
    Core logic for importing students from a CSV file.
    This function is UI-independent, asynchronous, and performs AI calls in parallel.
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
                errors.append("Cabeçalho não encontrado no arquivo CSV.")
                return 0, errors

            # Map header names to indices
            try:
                name_idx = header.index('Nome do Aluno')
                status_idx = header.index('Situação do Aluno')
                birth_date_idx = header.index('Data de Nascimento')
            except ValueError as e:
                errors.append(f"Coluna de cabeçalho essencial não encontrada: {e}")
                return 0, errors

            csv_data = lines[header_row_index + 1:]
            reader = csv.reader(csv_data, delimiter=';')

            for row_num, row in enumerate(reader, start=1):
                if not row or len(row) <= max(name_idx, status_idx):
                    continue

                full_name = row[name_idx].strip()
                if not full_name:
                    errors.append(f"Linha {row_num}: Ignorada por não conter nome do aluno.")
                    continue

                students_to_process.append({
                    'full_name': full_name,
                    'status': row[status_idx].strip(),
                    'birth_date_str': row[birth_date_idx].strip() if birth_date_idx < len(row) else None,
                    'row_num': row_num
                })

    except Exception as e:
        errors.append(f"Erro fatal ao ler o arquivo CSV: {e}")
        return 0, errors

    # --- Step 2: Perform AI name splitting in parallel ---
    if not students_to_process:
        return 0, errors

    name_splitting_tasks = [assistant_service.split_full_name(s['full_name']) for s in students_to_process]
    try:
        split_name_results = await asyncio.gather(*name_splitting_tasks)
    except Exception as e:
        errors.append(f"Erro crítico ao contatar o serviço de IA: {e}. A importação foi cancelada.")
        return 0, errors

    # --- Step 3: Process and save each student sequentially ---
    success_count = 0
    for i, student_data in enumerate(students_to_process):
        try:
            first_name, last_name = split_name_results[i]

            birth_date = None
            if student_data['birth_date_str']:
                try:
                    birth_date = datetime.strptime(student_data['birth_date_str'], "%d/%m/%Y").date()
                except ValueError:
                    errors.append(f"Linha {student_data['row_num']}: Formato de data inválido para '{student_data['full_name']}'. Usando data nula.")

            student = data_service.get_student_by_name(student_data['full_name'])
            if not student:
                student = data_service.add_student(first_name, last_name, birth_date)

            status_from_file = student_data['status']
            status = "Active" if status_from_file == 'Ativo' else "Inactive"
            status_detail = None if status == "Active" else status_from_file

            next_call_number = data_service.get_next_call_number(class_id)
            data_service.add_student_to_class(student.id, class_id, next_call_number, status, status_detail)
            success_count += 1

        except Exception as e:
            errors.append(f"Linha {student_data['row_num']}: Erro inesperado ao processar o aluno '{student_data['full_name']}': {e}")

    return success_count, errors
