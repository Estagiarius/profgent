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
    Analisa o conteúdo de um arquivo CSV de alunos.

    A função é projetada para lidar com um formato específico que inclui:
    - Linhas de metadados no início do arquivo.
    - Um cabeçalho que define as colunas de dados.
    - Dados delimitados por ponto e vírgula (';').

    Args:
        file_content (str): O conteúdo completo do arquivo CSV como uma string.

    Returns:
        List[Dict[str, Optional[str]]]: Uma lista de dicionários, onde cada
        dicionário representa um aluno com dados extraídos e normalizados.
        Retorna uma lista vazia se nenhum dado de aluno for encontrado.

    Raises:
        ValueError: Se o cabeçalho do CSV não for encontrado ou estiver malformado.
    """
    # Encontra a linha do cabeçalho
    header_line_str = None
    lines = file_content.splitlines()
    for line in lines:
        if "Nome do Aluno" in line and "Data de Nascimento" in line:
            header_line_str = line
            break

    if not header_line_str:
        raise ValueError("Cabeçalho do CSV não encontrado. Verifique o formato do arquivo.")

    # Extrai o bloco de dados CSV fatiando a string original
    # Isso é mais robusto do que reconstruir a partir de `splitlines()`
    try:
        header_pos = file_content.index(header_line_str)
        data_pos = file_content.index('\n', header_pos) + 1
        csv_data_block = file_content[data_pos:]
    except ValueError:
        # Se não houver nova linha após o cabeçalho, significa que não há dados
        csv_data_block = ""

    if not csv_data_block.strip():
        return []

    csv_file = StringIO(csv_data_block)

    # Mapeamento e processamento do CSV
    column_map = {
        "Nome do Aluno": "full_name",
        "Data de Nascimento": "birth_date",
        "Situação do Aluno": "status"
    }

    actual_headers = [h.strip() for h in header_line_str.split(';')]
    reader = csv.reader(csv_file, delimiter=';')

    students_data = []
    for row in reader:
        if not row or all(not cell.strip() for cell in row):
            continue

        student_info = {}
        for i, header in enumerate(actual_headers):
            if header in column_map:
                key = column_map[header]
                value = row[i].strip() if i < len(row) else None
                student_info[key] = value

        if not student_info.get("full_name"):
            continue

        first_name, last_name = split_full_name(student_info["full_name"])
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

        students_data.append(student_info)

    return students_data
