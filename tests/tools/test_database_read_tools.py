# Importa as classes e funções necessárias para o teste.
from app.services.data_service import DataService
from app.tools import database_tools
from app.tools.database_tools import get_student_grade, list_courses_for_student, get_class_average

# Define uma função de teste para a ferramenta get_student_grade quando a nota é encontrada.
def test_get_student_grade_found(data_service: DataService):
    """Testa get_student_grade quando a nota é encontrada."""
    # Monkeypatching: Substitui a instância do data_service no módulo da ferramenta
    # pela instância de teste (conectada ao banco em memória) fornecida pela fixture.
    # Isso garante que a ferramenta use o banco de dados de teste.
    database_tools.data_service = data_service

    # --- PREPARAÇÃO ---
    # Cria os dados necessários (aluno, curso, turma, etc.) para o teste.
    student = data_service.add_student("John", "Doe")
    course = data_service.add_course("Math 101", "M101")
    class_ = data_service.create_class("1A", course['id'])
    assessment = data_service.add_assessment(class_['id'], "Final Exam", 1.0)
    data_service.add_student_to_class(student['id'], class_['id'], 1) # Matricula o aluno
    data_service.add_grade(student['id'], assessment['id'], 95.5)

    # --- AÇÃO ---
    # Chama a função da ferramenta diretamente.
    result = get_student_grade("John Doe", "Math 101")

    # --- VERIFICAÇÃO ---
    # Garante que a string de resultado contenha as informações esperadas.
    assert "95.5" in result
    assert "John Doe" in result
    assert "Math 101" in result

# Define um teste para o caso de o aluno ou curso não ser encontrado.
def test_get_student_grade_not_found(data_service: DataService):
    """Testa get_student_grade quando o aluno ou curso não é encontrado."""
    database_tools.data_service = data_service
    # Ação: Chama a ferramenta com dados que não existem.
    result = get_student_grade("Jane Doe", "Nonexistent Course")
    # Verificação: Garante que a mensagem de erro correta é retornada.
    # O teste verifica primeiro o aluno, então o erro do aluno deve ser retornado.
    assert "Aluno 'Jane Doe' não encontrado." in result

# Define um teste para a ferramenta que lista os cursos de um aluno.
def test_list_courses_for_student(data_service: DataService):
    """Testa a listagem de cursos para um aluno."""
    database_tools.data_service = data_service

    # --- PREPARAÇÃO ---
    # Cria um aluno e o matricula em dois cursos diferentes, com uma nota em cada.
    student = data_service.add_student("Alice", "Smith")
    course1 = data_service.add_course("History 202", "H202")
    course2 = data_service.add_course("Art 101", "A101")
    class1 = data_service.create_class("1A", course1['id'])
    class2 = data_service.create_class("1B", course2['id'])
    assessment1 = data_service.add_assessment(class1['id'], "Essay", 1.0)
    assessment2 = data_service.add_assessment(class2['id'], "Project", 1.0)
    data_service.add_grade(student['id'], assessment1['id'], 88.0)
    data_service.add_grade(student['id'], assessment2['id'], 92.0)

    # --- AÇÃO ---
    # Chama a ferramenta para listar os cursos do aluno.
    result = list_courses_for_student("Alice Smith")

    # --- VERIFICAÇÃO ---
    # Garante que os nomes dos dois cursos aparecem no resultado.
    assert "History 202" in result
    assert "Art 101" in result

# Define um teste para a ferramenta que calcula a média da turma.
def test_get_class_average(data_service: DataService):
    """Testa o cálculo da média da turma para um curso."""
    database_tools.data_service = data_service

    # --- PREPARAÇÃO ---
    # Cria dois alunos, um curso, uma turma, e adiciona uma nota para cada aluno.
    student1 = data_service.add_student("Bob", "Ray")
    student2 = data_service.add_student("Charlie", "Day")
    course = data_service.add_course("Physics 303", "P303")
    class_ = data_service.create_class("1A", course['id'])
    assessment = data_service.add_assessment(class_['id'], "Lab 1", 1.0)
    data_service.add_student_to_class(student1['id'], class_['id'], 1)
    data_service.add_student_to_class(student2['id'], class_['id'], 2)
    data_service.add_grade(student1['id'], assessment['id'], 70)
    data_service.add_grade(student2['id'], assessment['id'], 90)

    # --- AÇÃO ---
    # Chama a ferramenta para calcular a média.
    result = get_class_average("Physics 303")

    # --- VERIFICAÇÃO ---
    # Garante que a média calculada ((70 + 90) / 2 = 80) está no resultado.
    assert "80.00" in result
