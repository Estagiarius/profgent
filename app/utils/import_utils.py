import csv
import asyncio
from datetime import datetime

def import_students_from_csv(filepath, class_id, data_service, assistant_service):
    """
    Core logic for importing students from a CSV file.
    This function is UI-independent and can be tested separately.

    Args:
        filepath (str): The path to the CSV file.
        class_id (int): The ID of the class to enroll students into.
        data_service (DataService): The data service instance.
        assistant_service (AssistantService): The assistant service instance.

    Returns:
        tuple[int, list[str]]: A tuple containing the number of successful imports
                               and a list of error messages.
    """
    success_count = 0
    errors = []

    try:
        with open(filepath, mode='r', encoding='utf-8', errors='ignore') as file:
            header = None
            lines = file.readlines()
            for i, line in enumerate(lines):
                if 'Nome do Aluno' in line and 'Situação do Aluno' in line:
                    header = [h.strip() for h in line.strip().split(';')]
                    csv_data = lines[i+1:]
                    break

            if not header:
                errors.append("Cabeçalho não encontrado no arquivo CSV.")
                return 0, errors

            reader = csv.reader(csv_data, delimiter=';')

            header_map = {
                'Nº de chamada': 'call_number',
                'Nome do Aluno': 'student_name',
                'Data de Nascimento': 'birth_date',
                'Situação do Aluno': 'status'
            }

            try:
                col_indices = {header_map[col]: i for i, col in enumerate(header) if col in header_map}
                if 'student_name' not in col_indices or 'status' not in col_indices:
                    errors.append("Colunas essenciais ('Nome do Aluno', 'Situação do Aluno') não encontradas.")
                    return 0, errors
            except KeyError as e:
                errors.append(f"Coluna de cabeçalho desconhecida encontrada: {e}")
                return 0, errors

            for row_num, row in enumerate(reader, start=1):
                if not row or not any(field.strip() for field in row):
                    continue

                try:
                    full_name_str = row[col_indices['student_name']]
                    if not full_name_str.strip():
                        continue

                    try:
                        first_name, last_name = asyncio.run(assistant_service.split_full_name(full_name_str))
                    except Exception as e:
                        errors.append(f"Linha {row_num}: Falha na divisão do nome '{full_name_str}', usando fallback. Erro: {e}")
                        name_parts = full_name_str.split()
                        first_name = name_parts[0]
                        last_name = " ".join(name_parts[1:])

                    birth_date_str = row[col_indices.get('birth_date')] if 'birth_date' in col_indices else None
                    birth_date = None
                    if birth_date_str:
                        try:
                            birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y").date()
                        except ValueError:
                            errors.append(f"Linha {row_num}: Formato de data inválido para '{full_name_str}'. Usando data nula.")

                    student = data_service.get_student_by_name(full_name_str)
                    if not student:
                        student = data_service.add_student(first_name, last_name, birth_date)

                    status_from_file = row[col_indices['status']]
                    status = "Active"
                    status_detail = None
                    if status_from_file != 'Ativo':
                        status = "Inactive"
                        status_detail = status_from_file

                    next_call_number = data_service.get_next_call_number(class_id)
                    data_service.add_student_to_class(student.id, class_id, next_call_number, status, status_detail)
                    success_count += 1

                except IndexError:
                    errors.append(f"Linha {row_num}: A linha está mal formatada ou faltando colunas.")
                except Exception as e:
                    errors.append(f"Linha {row_num}: Erro inesperado ao processar o aluno '{full_name_str}': {e}")

        return success_count, errors

    except Exception as e:
        errors.append(f"Erro fatal ao processar o arquivo: {e}")
        return 0, errors
