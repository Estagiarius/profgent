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
from datetime import date
from app.services.data_service import DataService


def test_seating_chart_service_crud_and_dict_return(data_service: DataService, db_session):
    """Valida criação, consulta, atualização e exclusão de mapas de sala sem quebrar isolamento de sessão."""
    cls = data_service.create_class("Turma Mapa 1A")
    s1 = data_service.add_student("Carlos", "Eduardo")
    data_service.add_student_to_class(s1["id"], cls["id"], 1)

    chart = data_service.create_seating_chart(cls["id"], "Layout Padrão", 4, 5)
    assert isinstance(chart, dict)
    assert chart["name"] == "Layout Padrão"
    assert chart["rows"] == 4 and chart["columns"] == 5

    charts = data_service.get_seating_charts_for_class(cls["id"])
    assert len(charts) == 1

    data_service.update_seating_chart_layout(chart["id"], '{"0,0": "teacher_desk"}')
    data_service.save_seat_assignments(chart["id"], [{"student_id": s1["id"], "row_index": 1, "col_index": 2}])

    details = data_service.get_seating_chart_details(chart["id"])
    assert details["layout_config"] == '{"0,0": "teacher_desk"}'
    assert len(details["assignments"]) == 1
    assert details["assignments"][0]["student_id"] == s1["id"]

    data_service.delete_seating_chart(chart["id"])
    assert data_service.get_seating_chart_details(chart["id"]) is None


def test_dashboard_students_at_risk_no_assessments_not_flagged(data_service: DataService):
    """Alunos de uma turma sem avaliações cadastradas não devem ser marcados em risco por nota."""
    cls = data_service.create_class("Turma Sem Provas")
    s1 = data_service.add_student("Maria", "Clara")
    data_service.add_student_to_class(s1["id"], cls["id"], 1)

    at_risk = data_service.get_students_at_risk(cls["id"])
    assert at_risk == []


def test_dashboard_respects_final_override_period_5(data_service: DataService):
    """Avaliação de grading_period == 5 atua como override final sem contaminar a média ponderada regular."""
    cls = data_service.create_class("Turma Override")
    course = data_service.add_course("Física", "FIS101")
    subj = data_service.add_subject_to_class(cls["id"], course["id"])
    s1 = data_service.add_student("Lucas", "Mendes")
    data_service.add_student_to_class(s1["id"], cls["id"], 1)

    a1 = data_service.add_assessment(subj["id"], "Prova 1", 1.0, grading_period=1)
    data_service.add_grade(s1["id"], a1["id"], 4.0)

    # Sem override: média 4.0 -> aluno em risco
    summary_before = data_service.get_student_performance_summary(s1["id"], cls["id"])
    assert summary_before["weighted_average"] == 4.0

    # Com override manual (período 5) = 7.5 -> média final deve ser 7.5 (não (4+7.5)/2)
    final_a = data_service.ensure_final_assessment(subj["id"])
    data_service.add_grade(s1["id"], final_a["id"], 7.5)

    summary_after = data_service.get_student_performance_summary(s1["id"], cls["id"])
    assert summary_after["weighted_average"] == 7.5
    assert data_service.get_students_at_risk(cls["id"]) == []


def test_copy_class_preserves_bncc_codes(data_service: DataService):
    """Valida que copy_class preserva bncc_codes nas avaliações copiadas."""
    cls = data_service.create_class("Turma Origem BNCC")
    course = data_service.add_course("História", "HIS101", bncc_expected="EF06HI01")
    subj = data_service.add_subject_to_class(cls["id"], course["id"])
    data_service.add_assessment(subj["id"], "Trabalho 1", 2.0, grading_period=2, bncc_codes="EF06HI01")

    copied = data_service.copy_class(cls["id"], "Turma Destino BNCC", copy_subjects=True, copy_assessments=True)
    copied_subjects = data_service.get_subjects_for_class(copied["id"])
    assert len(copied_subjects) == 1

    copied_assessments = data_service.get_assessments_for_subject(copied_subjects[0]["id"])
    assert len(copied_assessments) == 1
    assert copied_assessments[0]["grading_period"] == 2
    assert copied_assessments[0]["bncc_codes"] == "EF06HI01"


def test_delete_class_cleans_seating_charts_and_schedules(data_service: DataService):
    """Valida exclusão completa de turma com mapa de sala, horário e frequência sob FK ON."""
    cls = data_service.create_class("Turma Completa Delete")
    course = data_service.add_course("Geografia", "GEO101")
    subj = data_service.add_subject_to_class(cls["id"], course["id"])
    s1 = data_service.add_student("Beatriz", "Lima")
    data_service.add_student_to_class(s1["id"], cls["id"], 1)

    lesson = data_service.create_lesson(subj["id"], "Aula 1", "Conteúdo", date(2025, 3, 1))
    data_service.register_attendance(lesson["id"], [{"student_id": s1["id"], "status": "P"}])
    slot = data_service.create_time_slot(0, 1, "08:00", "08:50")
    data_service.create_schedule_assignment(slot["id"], subj["id"])
    chart = data_service.create_seating_chart(cls["id"], "Mapa", 3, 3)
    data_service.save_seat_assignments(chart["id"], [{"student_id": s1["id"], "row_index": 0, "col_index": 0}])

    data_service.delete_class(cls["id"])
    assert data_service.get_class_by_id(cls["id"]) is None
    assert data_service.get_seating_chart_details(chart["id"]) is None
