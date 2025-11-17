# -*- coding: utf-8 -*-

"""
Este módulo fornece um parser determinístico para arquivos CSV de alunos,
projetado especificamente para o formato exportado por sistemas de gestão
acadêmica brasileiros.
"""

import csv
from io import StringIO
from datetime import datetime
from typing import List, Dict, Optional

from app.utils.name_parser import split_full_name


def parse_student_csv(file_content: str) -> List[Dict[str, Optional[str]]]:
    """
    Analisa o conteúdo de um arquivo CSV de alunos, lidando com duplicatas.

    A função é projetada para lidar com um formato específico que inclui:
    - Linhas de metadados no início do arquivo.
    - Um cabeçalho que define as colunas de dados.
    - Dados delimitados por ponto e vírgula (';').
    - Potenciais linhas de alunos duplicadas.

    Se um aluno aparecer mais de uma vez, apenas a última ocorrência será
    considerada, garantindo que os dados mais recentes prevaleçam.

    Args:
        file_content (str): O conteúdo completo do arquivo CSV como uma string.

    Returns:
        List[Dict[str, Optional[str]]]: Uma lista de dicionários, onde cada
        dicionário representa um aluno único com dados extraídos e normalizados.

    Raises:
        ValueError: Se o cabeçalho do CSV não for encontrado.
    """
    header_line_str = None
    lines = file_content.splitlines()
    for line in lines:
        if "Nome do Aluno" in line and "Data de Nascimento" in line:
            header_line_str = line
            break

    if not header_line_str:
        raise ValueError("Cabeçalho do CSV não encontrado. Verifique o formato do arquivo.")

    try:
        header_pos = file_content.index(header_line_str)
        data_pos = file_content.index('\n', header_pos) + 1
        csv_data_block = file_content[data_pos:]
    except ValueError:
        csv_data_block = ""

    if not csv_data_block.strip():
        return []

    csv_file = StringIO(csv_data_block)

    column_map = {
        "Nome do Aluno": "full_name",
        "Data de Nascimento": "birth_date",
        "Situação do Aluno": "status"
    }

    actual_headers = [h.strip() for h in header_line_str.split(';')]
    reader = csv.reader(csv_file, delimiter=';')

    # Usa um dicionário para armazenar os alunos, onde a chave é o nome completo.
    # Isso garante que, se um aluno for encontrado novamente, seus dados serão
    # substituídos, mantendo apenas a última ocorrência.
    students_dict: Dict[str, Dict[str, Optional[str]]] = {}

    for row in reader:
        if not row or all(not cell.strip() for cell in row):
            continue

        student_info = {}
        for i, header in enumerate(actual_headers):
            if header in column_map:
                key = column_map[header]
                value = row[i].strip() if i < len(row) else None
                student_info[key] = value

        full_name = student_info.get("full_name")
        if not full_name:
            continue

        first_name, last_name = split_full_name(full_name)
        student_info["first_name"] = first_name
        student_info["last_name"] = last_name

        raw_status = student_info.get("status", "").upper()
        student_info["status"] = "Active" if raw_status == "ATIVO" else "Inactive"
        student_info["status_detail"] = student_info.get("status", "")

        raw_date = student_info.get("birth_date")
        if raw_date:
            try:
                datetime.strptime(raw_date, "%d/%m/%Y")
            except ValueError:
                student_info["birth_date"] = None

        # Adiciona ou atualiza o aluno no dicionário
        students_dict[full_name.lower()] = student_info

    # Retorna os valores do dicionário como uma lista.
    return list(students_dict.values())
