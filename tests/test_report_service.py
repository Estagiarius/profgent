import pytest
import os
from unittest.mock import MagicMock, patch
from app.services.report_service import ReportService

class TestReportService:
    @pytest.fixture
    def report_service(self, mocker):
        # Mock DataService within ReportService
        with patch('app.services.report_service.DataService') as MockDataService:
            service = ReportService()
            service.data_service = MockDataService.return_value
            return service

    def test_generate_student_report_card(self, report_service):
        # Mock data
        report_service.data_service.get_class_by_id.return_value = {"id": 1, "name": "Class A"}
        report_service.data_service.get_all_students.return_value = [{"id": 1, "first_name": "John", "last_name": "Doe"}]
        report_service.data_service.get_subjects_for_class.return_value = [
            {"id": 10, "course_name": "Math", "weight": 1.0}
        ]
        report_service.data_service.get_assessments_for_subject.return_value = [
            {"id": 100, "name": "Test 1", "weight": 1.0}
        ]
        report_service.data_service.get_grades_for_subject.return_value = [
            {"student_id": 1, "assessment_id": 100, "score": 9.0}
        ]
        report_service.data_service.get_incidents_for_class.return_value = []
        report_service.data_service.calculate_weighted_average.return_value = 9.0

        # Call method
        filepath = report_service.generate_student_report_card(1, 1)

        # Verify
        assert os.path.exists(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "BOLETIM ESCOLAR" in content
            assert "John Doe" in content
            assert "DISCIPLINA: MATH" in content
            assert "MÉDIA FINAL: 9.00" in content

        # Cleanup
        os.remove(filepath)

    def test_generate_class_grade_distribution(self, report_service):
        # Mock data
        report_service.data_service.get_class_by_id.return_value = {"id": 1, "name": "Class A"}
        report_service.data_service.get_enrollments_for_class.return_value = [{"student_id": 1}]
        report_service.data_service.get_subjects_for_class.return_value = [{"id": 10, "course_name": "Math"}]
        report_service.data_service.get_assessments_for_subject.return_value = [{"id": 100}]
        report_service.data_service.get_grades_for_subject.return_value = [{"student_id": 1, "assessment_id": 100, "score": 8.0}]
        report_service.data_service.calculate_weighted_average.return_value = 8.0

        filepath = report_service.generate_class_grade_distribution(1)
        assert os.path.exists(filepath)
        os.remove(filepath)

    def test_export_class_grades_csv(self, report_service):
        # Mock data
        report_service.data_service.get_class_by_id.return_value = {"id": 1, "name": "Class A"}
        report_service.data_service.get_enrollments_for_class.return_value = [
            {"student_id": 1, "call_number": 1, "student_first_name": "John", "student_last_name": "Doe"}
        ]
        report_service.data_service.get_subjects_for_class.return_value = [{"id": 10, "course_name": "Math"}]
        report_service.data_service.get_assessments_for_subject.return_value = [{"id": 100, "name": "Test"}]
        report_service.data_service.get_grades_for_subject.return_value = [{"student_id": 1, "assessment_id": 100, "score": 10.0}]
        report_service.data_service.calculate_weighted_average.return_value = 10.0

        filepath = report_service.export_class_grades_csv(1)
        assert os.path.exists(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "John Doe" in content
            assert "Math" in content # Header check
            assert "10.00" in content

        os.remove(filepath)
