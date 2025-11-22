# Importa as classes e funções necessárias para o teste.
from app.services.data_service import DataService
from app.tools import database_write_tools
from app.tools.database_write_tools import add_new_student, add_new_course, add_new_grade
import pytest

# Define uma fixture com `autouse=True`. Isso significa que esta fixture será
# executada automaticamente para cada teste neste arquivo, sem precisar ser
# passada como um argumento para a função de teste.
@pytest.fixture(autouse=True)
def patch_tool_data_service(data_service: DataService):
    """Faz o monkeypatch da instância compartilhada do DataService no pacote de serviços."""
    # Substitui a instância do DataService no módulo da ferramenta pela
    # instância de teste fornecida pela fixture `data_service`.
    database_write_tools.data_service = data_service

# Define uma função de teste para a ferramenta `add_new_student`.
def test_add_new_student(data_service: DataService):
    """Testa a ferramenta add_new_student."""
    # --- AÇÃO ---
    # Chama a função da ferramenta para adicionar um novo aluno.
    result = add_new_student("Test", "Student")

    # --- VERIFICAÇÃO ---
    # 1. Verifica a resposta da ferramenta: Garante que a mensagem de sucesso foi retornada.
    assert "adicionado com sucesso" in result

    # 2. Verifica o estado do banco: Confirma que o aluno foi realmente criado no banco de dados de teste.
    student = data_service.get_student_by_name("Test Student")
    assert student is not None
    assert student['first_name'] == "Test"

# Define uma função de teste para a ferramenta `add_new_course`.
def test_add_new_course(data_service: DataService):
    """Testa a ferramenta add_new_course."""
    # --- AÇÃO ---
    result = add_new_course("Test Course", "TC101")

    # --- VERIFICAÇÃO ---
    # 1. Verifica a resposta da ferramenta.
    assert "adicionada com sucesso" in result

    # 2. Verifica o estado do banco.
    course = data_service.get_course_by_name("Test Course")
    assert course is not None
    assert course['course_code'] == "TC101"

# Define uma função de teste para a ferramenta `add_new_grade`.
def test_add_new_grade(data_service: DataService):
    """Testa a ferramenta add_new_grade."""
    # --- PREPARAÇÃO ---
    # Cria toda a estrutura de dados necessária para que uma nota possa ser adicionada.
    student = data_service.add_student("Grade", "Student")
    course = data_service.add_course("Grading", "G101")
    class_ = data_service.create_class("1A", course['id'])
    data_service.add_assessment(class_['id'], "Final Project", 1.0)
    data_service.add_student_to_class(student['id'], class_['id'], 1) # Matricula o aluno

    # --- AÇÃO ---
    # Chama a ferramenta para adicionar a nota.
    result = add_new_grade("Grade Student", "1A", "Final Project", 99.9)

    # --- VERIFICAÇÃO ---
    # 1. Verifica a resposta da ferramenta.
    assert "Nota adicionada com sucesso" in result

    # 2. Verifica o estado do banco, buscando a nota que acabou de ser criada.
    grades = data_service.get_grades_for_class(class_['id'])
    assert len(grades) == 1
    assert grades[0]['score'] == 99.9
    assert grades[0]['assessment_name'] == "Final Project"
