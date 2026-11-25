# Author: Victor Hugo Garcia de Oliveira
# Date: 2026-11-25
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
import json
from app.core.tools.tool_decorator import tool
from app.services import data_service
from app.services.bncc_service import BNCCService

DAYS_OF_WEEK = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo",
}


@tool
def get_weekly_schedule_tool() -> str:
    """
    Obtém a grade horária semanal completa do professor com dias, horários e turmas/disciplinas alocadas.
    """
    try:
        grid = data_service.get_full_schedule_grid()
        if not grid:
            return "Nenhum horário configurado na grade semanal."

        formatted = {}
        for day_code in sorted(grid.keys()):
            day_name = DAYS_OF_WEEK.get(day_code, f"Dia {day_code}")
            formatted[day_name] = grid[day_code]
        return json.dumps(formatted, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Erro ao consultar grade horária: {e}"


@tool
def list_seating_charts_tool(class_name: str) -> str:
    """
    Lista os mapas de sala cadastrados para uma turma específica.

    :param class_name: Nome da turma.
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls:
            return f"Turma '{class_name}' não encontrada."

        charts = data_service.get_seating_charts_for_class(cls["id"])
        if not charts:
            return f"Nenhum mapa de sala cadastrado para a turma '{class_name}'."

        payload = [
            {"id": c["id"], "name": c["name"], "rows": c["rows"], "columns": c["columns"]}
            for c in charts
        ]
        return json.dumps(payload, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Erro ao listar mapas de sala: {e}"


@tool
def search_bncc_skills_tool(query: str, limit: int = 10) -> str:
    """
    Pesquisa habilidades da Base Nacional Comum Curricular (BNCC) por código, disciplina ou palavra-chave.

    :param query: Termo de busca ou código BNCC (ex: 'EF01MA01' ou 'frações').
    :param limit: Quantidade máxima de resultados retornados (padrão 10).
    """
    try:
        safe_limit = max(1, min(int(limit), 30))
        results = BNCCService.search_skills(query)
        if not results:
            return f"Nenhuma habilidade BNCC encontrada para '{query}'."

        return json.dumps(results[:safe_limit], indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Erro ao pesquisar habilidades BNCC: {e}"


@tool
def get_bncc_coverage_tool(class_name: str, subject_name: str) -> str:
    """
    Obtém o relatório de cobertura curricular da BNCC para uma disciplina em uma turma.

    :param class_name: Nome da turma.
    :param subject_name: Nome da disciplina.
    """
    try:
        cls = data_service.get_class_by_name(class_name)
        if not cls:
            return f"Turma '{class_name}' não encontrada."

        subjects = data_service.get_subjects_for_class(cls["id"])
        target_subject = next((s for s in subjects if s["course_name"].lower() == subject_name.lower()), None)
        if not target_subject:
            return f"Disciplina '{subject_name}' não encontrada na turma '{class_name}'."

        coverage = data_service.get_bncc_coverage(target_subject["id"])
        return json.dumps(coverage, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Erro ao obter cobertura BNCC: {e}"


@tool
def get_student_period_averages_tool(student_name: str, class_name: str, subject_name: str) -> str:
    """
    Consulta as médias bimestrais (1º ao 4º bimestre), média final calculada e nota final manual de um aluno em uma disciplina.

    :param student_name: Nome completo do aluno.
    :param class_name: Nome da turma.
    :param subject_name: Nome da disciplina.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Aluno '{student_name}' não encontrado."

        cls = data_service.get_class_by_name(class_name)
        if not cls:
            return f"Turma '{class_name}' não encontrada."

        subjects = data_service.get_subjects_for_class(cls["id"])
        target_subject = next((s for s in subjects if s["course_name"].lower() == subject_name.lower()), None)
        if not target_subject:
            return f"Disciplina '{subject_name}' não encontrada na turma '{class_name}'."

        averages = data_service.get_student_period_averages(student["id"], target_subject["id"])
        if not averages:
            return f"Nenhuma avaliação cadastrada para {subject_name} na turma {class_name}."

        return json.dumps(averages, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Erro ao consultar médias bimestrais: {e}"
