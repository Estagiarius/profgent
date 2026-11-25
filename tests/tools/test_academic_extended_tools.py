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
from datetime import date
from app.tools import academic_extended_tools
from app.services.assistant_service import AssistantService


def test_extended_tools_end_to_end(data_service, monkeypatch):
    monkeypatch.setattr(academic_extended_tools, "data_service", data_service)

    cls = data_service.create_class("Turma 9A")
    course = data_service.add_course("Matemática", "MAT9", bncc_expected="EF01MA01,EF01MA02")
    subj = data_service.add_subject_to_class(cls["id"], course["id"])
    student = data_service.add_student("Sofia", "Almeida")
    data_service.add_student_to_class(student["id"], cls["id"], 1)

    # Horário
    slot = data_service.create_time_slot(0, 1, "07:30", "08:20")
    data_service.create_schedule_assignment(slot["id"], subj["id"])
    sched_out = academic_extended_tools.get_weekly_schedule_tool()
    assert "Segunda-feira" in sched_out
    assert "Turma 9A" in sched_out

    # Mapa de sala
    data_service.create_seating_chart(cls["id"], "Layout Prova", 4, 5)
    charts_out = academic_extended_tools.list_seating_charts_tool("Turma 9A")
    charts_json = json.loads(charts_out)
    assert len(charts_json) == 1
    assert charts_json[0]["name"] == "Layout Prova"

    # BNCC busca + cobertura
    bncc_search = academic_extended_tools.search_bncc_skills_tool("EF01MA01", limit=5)
    assert "EF01MA01" in bncc_search

    data_service.create_lesson(subj["id"], "Aula BNCC", "Conteúdo", date(2025, 4, 1), bncc_codes="EF01MA01")
    bncc_cov = json.loads(academic_extended_tools.get_bncc_coverage_tool("Turma 9A", "Matemática"))
    assert bncc_cov["coverage_percentage"] == 50.0

    # Médias bimestrais
    a1 = data_service.add_assessment(subj["id"], "P1", 1.0, grading_period=1)
    data_service.add_grade(student["id"], a1["id"], 8.0)
    avgs = json.loads(academic_extended_tools.get_student_period_averages_tool("Sofia Almeida", "Turma 9A", "Matemática"))
    assert avgs["1"] == 8.0
    assert avgs["final_calculated"] == 2.0


def test_assistant_registers_extended_tools(mocker):
    mocker.patch("app.services.assistant_service.AssistantService._initialize_provider")
    service = AssistantService()
    names = set(service.tool_registry.tools.keys())
    for expected in (
        "get_weekly_schedule_tool",
        "list_seating_charts_tool",
        "search_bncc_skills_tool",
        "get_bncc_coverage_tool",
        "get_student_period_averages_tool",
    ):
        assert expected in names
