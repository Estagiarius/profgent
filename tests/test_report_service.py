import pytest
import os
from unittest.mock import MagicMock, patch
from app.services.report_service import ReportService
import matplotlib
from datetime import date

# Ensure matplotlib uses Agg backend for tests
matplotlib.use('Agg')

@pytest.fixture
def mock_data_service():
    with patch('app.services.report_service.DataService') as mock_ds_class:
        mock_ds = mock_ds_class.return_value

        # Mock common returns
        mock_ds.get_class_by_id.return_value = {
            "id": 1,
            "name": "Turma Teste",
            "assessments": [
                {"id": 101, "name": "Prova 1", "weight": 1.0},
                {"id": 102, "name": "Prova 2", "weight": 1.0}
            ]
        }

        mock_ds.get_all_students.return_value = [
            {"id": 50, "first_name": "João", "last_name": "Silva"}
        ]

        mock_ds.get_grades_for_class.return_value = [
            {"student_id": 50, "assessment_id": 101, "score": 8.0, "assessment_name": "Prova 1"},
            {"student_id": 50, "assessment_id": 102, "score": 7.0, "assessment_name": "Prova 2"}
        ]

        mock_ds.get_enrollments_for_class.return_value = [
            {
                "student_id": 50, "call_number": 1,
                "student_first_name": "João", "student_last_name": "Silva",
                "status": "Active"
            }
        ]

        mock_ds.get_incidents_for_class.return_value = []
        mock_ds.calculate_weighted_average.return_value = 7.5

        yield mock_ds

@pytest.fixture
def report_service(mock_data_service):
    return ReportService()

def test_generate_student_grade_chart(report_service, mock_data_service):
    # Test chart generation
    filepath = report_service.generate_student_grade_chart(50, 1)
    assert os.path.exists(filepath)
    assert filepath.endswith(".png")
    # Clean up
    os.remove(filepath)

def test_generate_class_distribution(report_service, mock_data_service):
    # Test distribution chart
    filepath = report_service.generate_class_grade_distribution(1)
    assert os.path.exists(filepath)
    assert filepath.endswith(".png")
    os.remove(filepath)

def test_export_csv(report_service, mock_data_service):
    filepath = report_service.export_class_grades_csv(1)
    assert os.path.exists(filepath)
    assert filepath.endswith(".csv")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "João Silva" in content
        assert "Prova 1" in content

    os.remove(filepath)

def test_generate_report_card(report_service, mock_data_service):
    filepath = report_service.generate_student_report_card(50, 1)
    assert os.path.exists(filepath)
    assert filepath.endswith(".txt")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "BOLETIM ESCOLAR" in content
        assert "João Silva" in content
        assert "MÉDIA FINAL: 7.50" in content

    os.remove(filepath)
