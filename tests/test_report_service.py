# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
import pytest
import os
from app.services.report_service import ReportService

class TestReportService:
    @pytest.fixture
    def report_service(self, mocker, tmp_path):
        mock_ds = mocker.MagicMock()
        return ReportService(data_service=mock_ds, reports_dir=str(tmp_path))

    def test_generate_student_report_card(self, report_service):
        report_service.data_service.get_class_by_id.return_value = {"id": 1, "name": "Class A"}
        report_service.data_service.get_class_report_data.return_value = {
            "students": [{"student_id": 1, "name": "John Doe", "call_number": 1, "status": "Active"}],
            "subjects": [
                {
                    "id": 10,
                    "course_name": "Math",
                    "assessments": [{"id": 100, "name": "Test 1", "weight": 1.0, "grading_period": 1}]
                }
            ],
            "grades_map": {(1, 100): 9.0}
        }
        report_service.data_service.get_student_incidents.return_value = []
        report_service.data_service.get_student_attendance_stats.return_value = {
            "total_lessons": 10,
            "present_count": 9,
            "absent_count": 1,
            "percentage": 90.0
        }

        filepath = report_service.generate_student_report_card(1, 1)

        assert os.path.exists(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "BOLETIM ESCOLAR" in content
            assert "John Doe" in content
            assert "DISCIPLINA: MATH" in content
            assert "MÉDIA FINAL: 9.00" in content

    def test_generate_student_report_card_missing_class_raises(self, report_service):
        report_service.data_service.get_class_by_id.return_value = None
        with pytest.raises(ValueError, match="Turma não encontrada"):
            report_service.generate_student_report_card(1, 999)

    def test_generate_class_grade_distribution(self, report_service):
        report_service.data_service.get_class_by_id.return_value = {"id": 1, "name": "Class A"}
        report_service.data_service.get_class_report_data.return_value = {
            "students": [{"student_id": 1, "name": "John Doe", "call_number": 1, "status": "Active"}],
            "subjects": [
                {
                    "id": 10,
                    "course_name": "Math",
                    "assessments": [{"id": 100, "name": "Test 1", "weight": 1.0, "grading_period": 1}]
                }
            ],
            "grades_map": {(1, 100): 8.0}
        }

        filepath = report_service.generate_class_grade_distribution(1)
        assert os.path.exists(filepath)

    def test_export_class_grades_csv(self, report_service):
        report_service.data_service.get_class_by_id.return_value = {"id": 1, "name": "Class A"}
        report_service.data_service.get_class_report_data.return_value = {
            "students": [{"student_id": 1, "name": "John Doe", "call_number": 1, "status": "Active"}],
            "subjects": [
                {
                    "id": 10,
                    "course_name": "Math",
                    "assessments": [{"id": 100, "name": "Test 1", "weight": 1.0, "grading_period": 1}]
                }
            ],
            "grades_map": {(1, 100): 10.0}
        }

        filepath = report_service.export_class_grades_csv(1)
        assert os.path.exists(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "John Doe" in content
            assert "Math" in content
            assert "10.00" in content
