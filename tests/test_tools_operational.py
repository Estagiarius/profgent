
import pytest
from unittest.mock import MagicMock, patch
from app.tools.database_tools import (
    list_lessons, update_lesson, delete_lesson_record, list_incidents
)

# Mock DataService
@pytest.fixture
def mock_data_service():
    with patch('app.tools.database_tools.data_service') as mock_ds:
        yield mock_ds

# --- Lesson Tools Tests ---

def test_list_lessons_success(mock_data_service):
    mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "Class A"}
    mock_data_service.get_lessons_for_class.return_value = [
        {"date": "2023-10-01", "title": "Math Basics"},
        {"date": "2023-10-02", "title": "Algebra"}
    ]

    result = list_lessons(class_name="Class A")
    assert "Math Basics" in result
    assert "Algebra" in result

def test_list_lessons_none_found(mock_data_service):
    mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "Class A"}
    mock_data_service.get_lessons_for_class.return_value = []

    result = list_lessons(class_name="Class A")
    assert "Nenhuma aula registrada" in result

def test_update_lesson_success(mock_data_service):
    mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "Class A"}
    mock_data_service.get_lessons_for_class.return_value = [
        {"id": 10, "date": "2023-10-01", "title": "Old Title", "content": "Old Content"}
    ]

    result = update_lesson(class_name="Class A", date_str="01/10/2023", new_topic="New Title")

    # Check if update was called with new title and OLD content (since it wasn't provided)
    # Note: The date object passed to update_lesson is constructed inside the tool, we check call args loosely or specific types
    mock_data_service.update_lesson.assert_called_once()
    call_args = mock_data_service.update_lesson.call_args
    assert call_args[0][0] == 10 # ID
    assert call_args[0][1] == "New Title" # New Title
    assert call_args[0][2] == "Old Content" # Kept Content

def test_delete_lesson_record_success(mock_data_service):
    mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "Class A"}
    mock_data_service.get_lessons_for_class.return_value = [
        {"id": 10, "date": "2023-10-01", "title": "Math Basics"}
    ]

    result = delete_lesson_record(class_name="Class A", date_str="01/10/2023")

    mock_data_service.delete_lesson.assert_called_once_with(10)
    assert "removida com sucesso" in result

# --- Incident Tools Tests ---

def test_list_incidents_success(mock_data_service):
    mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "Class A"}
    mock_data_service.get_incidents_for_class.return_value = [
        {"date": "2023-10-01", "student_first_name": "John", "student_last_name": "Doe", "description": "Talkative"}
    ]

    result = list_incidents(class_name="Class A")
    assert "John Doe" in result
    assert "Talkative" in result

def test_list_incidents_empty(mock_data_service):
    mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "Class A"}
    mock_data_service.get_incidents_for_class.return_value = []

    result = list_incidents(class_name="Class A")
    assert "Nenhum incidente registrado" in result
