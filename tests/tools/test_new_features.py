import json
from datetime import date
from app.tools.database_write_tools import add_new_student, add_new_lesson, register_incident
from app.tools.database_tools import get_class_roster

# Test add_new_student with optional parameters
def test_add_new_student_with_dob_and_enrollment(mocker):
    # Mock DataService methods
    mock_add_student = mocker.patch('app.tools.database_write_tools.data_service.add_student')
    mock_get_class_by_name = mocker.patch('app.tools.database_write_tools.data_service.get_class_by_name')
    mock_get_next_call_number = mocker.patch('app.tools.database_write_tools.data_service.get_next_call_number')
    mock_add_student_to_class = mocker.patch('app.tools.database_write_tools.data_service.add_student_to_class')

    # Setup return values
    mock_add_student.return_value = {'id': 1, 'first_name': 'João', 'last_name': 'Silva'}
    mock_get_class_by_name.return_value = {'id': 10, 'name': 'Turma A'}
    mock_get_next_call_number.return_value = 5
    mock_add_student_to_class.return_value = {'id': 100}

    # Execute tool
    result = add_new_student(first_name='João', last_name='Silva', date_of_birth='01/01/2010', enroll_in_class='Turma A')

    # Verify calls
    mock_add_student.assert_called_with('João', 'Silva', birth_date=date(2010, 1, 1))
    mock_get_class_by_name.assert_called_with('Turma A')
    mock_get_next_call_number.assert_called_with(10)
    mock_add_student_to_class.assert_called_with(1, 10, 5)

    # Verify result message
    assert "Novo aluno adicionado com sucesso" in result
    assert "Matriculado na turma 'Turma A'" in result

def test_add_new_student_invalid_date():
    result = add_new_student(first_name='João', last_name='Silva', date_of_birth='invalid-date')
    assert "Erro: Formato de data inválido" in result

# Test add_new_lesson
def test_add_new_lesson_success(mocker):
    # Mock DataService
    mock_get_class_by_name = mocker.patch('app.tools.database_write_tools.data_service.get_class_by_name')
    mock_create_lesson = mocker.patch('app.tools.database_write_tools.data_service.create_lesson')

    # Setup
    mock_get_class_by_name.return_value = {'id': 10, 'name': 'Turma A'}
    mock_create_lesson.return_value = {'id': 1, 'title': 'Math'}

    # Execute
    result = add_new_lesson(class_name='Turma A', topic='Math', content='Algebra basics', date_str='15/03/2024')

    # Verify
    mock_create_lesson.assert_called_with(10, 'Math', 'Algebra basics', date(2024, 3, 15))
    assert "Aula 'Math' registrada com sucesso" in result

def test_add_new_lesson_class_not_found(mocker):
    mock_get_class_by_name = mocker.patch('app.tools.database_write_tools.data_service.get_class_by_name')
    mock_get_class_by_name.return_value = None

    result = add_new_lesson(class_name='Turma X', topic='Math', content='...', date_str='15/03/2024')
    assert "Erro: Turma 'Turma X' não encontrada" in result

# Test register_incident
def test_register_incident_success(mocker):
    # Mock
    mock_get_student = mocker.patch('app.tools.database_write_tools.data_service.get_student_by_name')
    mock_get_class_by_name = mocker.patch('app.tools.database_write_tools.data_service.get_class_by_name')
    mock_create_incident = mocker.patch('app.tools.database_write_tools.data_service.create_incident')

    # Setup
    mock_get_student.return_value = {'id': 1, 'first_name': 'João'}
    mock_get_class_by_name.return_value = {'id': 10, 'name': 'Turma A'}
    mock_create_incident.return_value = {'id': 1}

    # Execute
    result = register_incident(student_name='João Silva', class_name='Turma A', description='Disruptive', date_str='10/05/2024')

    # Verify
    mock_create_incident.assert_called_with(10, 1, 'Disruptive', date(2024, 5, 10))
    assert "Incidente registrado para João Silva" in result

# Test get_class_roster
def test_get_class_roster_success(mocker):
    # Mock
    mock_get_all_classes = mocker.patch('app.tools.database_tools.data_service.get_all_classes')
    mock_get_enrollments = mocker.patch('app.tools.database_tools.data_service.get_enrollments_for_class')

    # Setup
    mock_get_all_classes.return_value = [{'id': 10, 'name': 'Turma A'}]
    mock_get_enrollments.return_value = [
        {'call_number': 1, 'student_first_name': 'João', 'student_last_name': 'Silva', 'status': 'Active'},
        {'call_number': 2, 'student_first_name': 'Maria', 'student_last_name': 'Santos', 'status': 'Active'}
    ]

    # Execute
    result = get_class_roster(class_name='Turma A')

    # Verify JSON structure
    data = json.loads(result)
    assert len(data) == 2
    assert data[0]['name'] == 'João Silva'
    assert data[1]['call_number'] == 2

def test_get_class_roster_empty(mocker):
    mock_get_all_classes = mocker.patch('app.tools.database_tools.data_service.get_all_classes')
    mock_get_enrollments = mocker.patch('app.tools.database_tools.data_service.get_enrollments_for_class')

    mock_get_all_classes.return_value = [{'id': 10, 'name': 'Turma A'}]
    mock_get_enrollments.return_value = []

    result = get_class_roster(class_name='Turma A')
    assert "não possui alunos matriculados" in result
