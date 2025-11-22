
import pytest
from unittest.mock import MagicMock, patch
from app.tools.database_tools import (
    list_all_courses, update_course_name, delete_course_record,
    update_assessment, delete_assessment_record
)

# Mock DataService
@pytest.fixture
def mock_data_service():
    with patch('app.tools.database_tools.data_service') as mock_ds:
        yield mock_ds

# --- Course Tools Tests ---

def test_list_all_courses_success(mock_data_service):
    mock_data_service.get_all_courses.return_value = [
        {"course_name": "Math", "course_code": "MAT101"},
        {"course_name": "History", "course_code": "HIS101"}
    ]

    result = list_all_courses()
    assert "Math (Código: MAT101)" in result
    assert "History (Código: HIS101)" in result

def test_list_all_courses_empty(mock_data_service):
    mock_data_service.get_all_courses.return_value = []

    result = list_all_courses()
    assert "Nenhuma disciplina cadastrada" in result

def test_update_course_name_success(mock_data_service):
    mock_data_service.get_course_by_name.return_value = {"id": 1, "course_name": "Math", "course_code": "MAT101"}

    result = update_course_name(current_name="Math", new_name="Mathematics")

    # Should call update with new name and OLD code (since code wasn't provided)
    mock_data_service.update_course.assert_called_once_with(1, "Mathematics", "MAT101")
    assert "Disciplina atualizada para 'Mathematics'" in result

def test_delete_course_record_success(mock_data_service):
    # Mock a course with NO classes
    mock_data_service.get_course_by_name.return_value = {"id": 1, "course_name": "Math", "classes": []}

    result = delete_course_record(course_name="Math")

    mock_data_service.delete_course.assert_called_once_with(1)
    assert "removida com sucesso" in result

def test_delete_course_record_with_classes_fails(mock_data_service):
    # Mock a course WITH classes
    mock_data_service.get_course_by_name.return_value = {"id": 1, "course_name": "Math", "classes": [{"id": 1, "name": "Class A"}]}

    result = delete_course_record(course_name="Math")

    mock_data_service.delete_course.assert_not_called()
    assert "Erro: Não é possível remover" in result

# --- Assessment Tools Tests ---

def test_update_assessment_success(mock_data_service):
    mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "Class A"}
    # Mock class details with assessments
    mock_data_service.get_class_by_id.return_value = {
        "id": 1,
        "name": "Class A",
        "assessments": [{"id": 10, "name": "Test 1", "weight": 1.0}]
    }

    result = update_assessment(class_name="Class A", current_assessment_name="Test 1", new_weight=2.0)

    # Should call with OLD name and NEW weight
    mock_data_service.update_assessment.assert_called_once_with(10, "Test 1", 2.0)
    assert "Avaliação atualizada" in result

def test_delete_assessment_record_success(mock_data_service):
    mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "Class A"}
    mock_data_service.get_class_by_id.return_value = {
        "id": 1,
        "name": "Class A",
        "assessments": [{"id": 10, "name": "Test 1", "weight": 1.0}]
    }

    result = delete_assessment_record(class_name="Class A", assessment_name="Test 1")

    mock_data_service.delete_assessment.assert_called_once_with(10)
    assert "removida com sucesso" in result
