
import pytest
from unittest.mock import MagicMock, patch
from app.tools.database_tools import (
    update_student_name, update_class_name, delete_student_record,
    delete_class_record, enroll_existing_student, change_student_status
)

# Mock DataService
@pytest.fixture
def mock_data_service():
    with patch('app.tools.database_tools.data_service') as mock_ds:
        yield mock_ds

# --- Maintenance Tools Tests ---

def test_update_student_name_success(mock_data_service):
    mock_data_service.get_student_by_name.return_value = {"id": 1, "first_name": "John", "last_name": "Doe"}

    result = update_student_name(current_name="John Doe", new_first_name="Johnny", new_last_name="Depp")

    mock_data_service.update_student.assert_called_once_with(1, "Johnny", "Depp")
    assert "Nome do aluno atualizado para Johnny Depp" in result

def test_update_student_name_not_found(mock_data_service):
    mock_data_service.get_student_by_name.return_value = None

    result = update_student_name(current_name="Missing Person", new_first_name="A", new_last_name="B")
    assert "Erro: Aluno 'Missing Person' não encontrado" in result

def test_delete_student_record_success(mock_data_service):
    mock_data_service.get_student_by_name.return_value = {"id": 1, "first_name": "John", "last_name": "Doe"}

    result = delete_student_record(student_name="John Doe")

    mock_data_service.delete_student.assert_called_once_with(1)
    assert "foi removido com sucesso" in result

def test_delete_class_record_success(mock_data_service):
    mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "Class A"}

    result = delete_class_record(class_name="Class A")

    mock_data_service.delete_class.assert_called_once_with(1)
    assert "foi removida com sucesso" in result

# --- Enrollment Tools Tests ---

def test_enroll_existing_student_success(mock_data_service):
    mock_data_service.get_student_by_name.return_value = {"id": 1, "name": "John"}
    mock_data_service.get_class_by_name.return_value = {"id": 2, "name": "Class A"}
    mock_data_service.get_next_call_number.return_value = 5
    mock_data_service.add_student_to_class.return_value = {"id": 10}

    result = enroll_existing_student(student_name="John", class_name="Class A")

    mock_data_service.add_student_to_class.assert_called_once_with(1, 2, 5)
    assert "matriculado com sucesso" in result

def test_enroll_existing_student_class_not_found(mock_data_service):
    mock_data_service.get_student_by_name.return_value = {"id": 1}
    mock_data_service.get_class_by_name.return_value = None

    result = enroll_existing_student(student_name="John", class_name="Missing Class")
    assert "Erro: Turma 'Missing Class' não encontrada" in result

def test_change_student_status_success(mock_data_service):
    mock_data_service.get_student_by_name.return_value = {"id": 1, "name": "John"}
    mock_data_service.get_class_by_name.return_value = {"id": 2, "name": "Class A"}
    mock_data_service.get_enrollments_for_class.return_value = [
        {"id": 100, "student_id": 1, "status": "Active"}, # Target
        {"id": 101, "student_id": 99, "status": "Active"}
    ]

    result = change_student_status(student_name="John", class_name="Class A", new_status="Inactive")

    mock_data_service.update_enrollment_status.assert_called_once_with(100, "Inactive")
    assert "Status de John na turma 'Class A' alterado para 'Inactive'" in result

def test_change_student_status_not_enrolled(mock_data_service):
    mock_data_service.get_student_by_name.return_value = {"id": 1, "name": "John"}
    mock_data_service.get_class_by_name.return_value = {"id": 2, "name": "Class A"}
    mock_data_service.get_enrollments_for_class.return_value = [] # Empty

    result = change_student_status(student_name="John", class_name="Class A", new_status="Inactive")
    assert "não está matriculado na turma" in result
