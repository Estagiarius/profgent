
import pytest
from unittest.mock import MagicMock, patch
from app.tools.database_tools import list_all_classes, get_class_roster, create_new_class, create_new_assessment

# Mock DataService
@pytest.fixture
def mock_data_service():
    with patch('app.tools.database_tools.data_service') as mock_ds:
        yield mock_ds

# --- Tests for database_read_tools functionality ---

def test_list_all_classes_success(mock_data_service):
    mock_data_service.get_all_classes.return_value = [
        {"name": "Class A", "course_name": "Math", "student_count": 10},
        {"name": "Class B", "course_name": "Science", "student_count": 15}
    ]

    result = list_all_classes()
    assert "Turma: Class A | Disciplina: Math | Alunos: 10" in result
    assert "Turma: Class B | Disciplina: Science | Alunos: 15" in result

def test_list_all_classes_empty(mock_data_service):
    mock_data_service.get_all_classes.return_value = []
    result = list_all_classes()
    assert "Não há turmas cadastradas" in result

def test_get_class_roster_success(mock_data_service):
    mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "Class A"}
    mock_data_service.get_enrollments_for_class.return_value = [
        {"call_number": 1, "student_first_name": "John", "student_last_name": "Doe", "status": "Active"},
        {"call_number": 2, "student_first_name": "Jane", "student_last_name": "Smith", "status": "Inactive"}
    ]

    result = get_class_roster(class_name="Class A")
    assert "Lista de Chamada para a Turma: Class A" in result
    assert "#1 - John Doe (Active)" in result
    assert "#2 - Jane Smith (Inactive)" in result

def test_get_class_roster_class_not_found(mock_data_service):
    mock_data_service.get_class_by_name.return_value = None
    result = get_class_roster(class_name="NonExistent")
    assert "Erro: Turma 'NonExistent' não encontrada" in result

def test_get_class_roster_no_students(mock_data_service):
    mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "Class A"}
    mock_data_service.get_enrollments_for_class.return_value = []
    result = get_class_roster(class_name="Class A")
    assert "não possui alunos matriculados" in result

# --- Tests for database_write_tools functionality ---

def test_create_new_class_success(mock_data_service):
    mock_data_service.get_course_by_name.return_value = {"id": 1, "course_name": "Math"}
    mock_data_service.get_class_by_name.return_value = None
    mock_data_service.create_class.return_value = {"id": 1, "name": "Class A"}

    result = create_new_class(course_name="Math", class_name="Class A")
    assert "Turma 'Class A' criada com sucesso" in result

def test_create_new_class_course_not_found(mock_data_service):
    mock_data_service.get_course_by_name.return_value = None
    result = create_new_class(course_name="Math", class_name="Class A")
    assert "Erro: Disciplina 'Math' não encontrada" in result

def test_create_new_class_already_exists(mock_data_service):
    mock_data_service.get_course_by_name.return_value = {"id": 1, "course_name": "Math"}
    mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "Class A"}
    result = create_new_class(course_name="Math", class_name="Class A")
    assert "Erro: Já existe uma turma com o nome 'Class A'" in result

def test_create_new_assessment_success(mock_data_service):
    mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "Class A"}
    mock_data_service.add_assessment.return_value = {"id": 1, "name": "Test 1", "weight": 1.0}

    result = create_new_assessment(class_name="Class A", assessment_name="Test 1", weight=1.0)
    assert "Avaliação 'Test 1' (Peso: 1.0) criada com sucesso" in result

def test_create_new_assessment_class_not_found(mock_data_service):
    mock_data_service.get_class_by_name.return_value = None
    result = create_new_assessment(class_name="Class A", assessment_name="Test 1", weight=1.0)
    assert "Erro: Turma 'Class A' não encontrada" in result
