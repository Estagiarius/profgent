# Importa o decorador 'tool' que registra a função como uma ferramenta para a IA.
from app.core.tools.tool_decorator import tool
# Importa a instância compartilhada do DataService criada no __init__.py do pacote 'services'.
from app.services import data_service

# O decorador '@tool' informa ao sistema que esta função é uma ferramenta que a IA pode chamar.
@tool
def get_student_grade(student_name: str, course_name: str) -> str:
    """
    Finds all grades of a specific student in a given course.
    Returns the grades as a string or a 'not found' message.
    """
    # Busca o aluno pelo nome usando o serviço de dados.
    student = data_service.get_student_by_name(student_name)
    # Se o aluno não for encontrado, retorna uma mensagem de erro.
    if not student:
        return f"Student '{student_name}' not found."

    # Busca o curso pelo nome.
    course = data_service.get_course_by_name(course_name)
    # Se o curso não for encontrado, retorna uma mensagem de erro.
    if not course:
        return f"Course '{course_name}' not found."

    # Lista para armazenar todas as notas do aluno encontradas no curso.
    student_grades_in_course = []
    # Itera sobre todas as turmas associadas ao curso.
    for class_data in course['classes']:
        # Obtém todas as notas da turma.
        grades_in_class = data_service.get_grades_for_class(class_data['id'])
        # Filtra as notas para encontrar apenas as do aluno específico.
        student_grades_in_class = [g for g in grades_in_class if g['student_id'] == student['id']]
        # Adiciona as notas encontradas à lista principal.
        student_grades_in_course.extend(student_grades_in_class)

    # Se nenhuma nota foi encontrada, retorna uma mensagem informativa.
    if not student_grades_in_course:
        return f"No grades found for {student_name} in {course_name}."

    # Formata a lista de notas em uma string legível.
    grade_list = "\n".join([f"- {g['assessment_name']}: {g['score']}" for g in student_grades_in_course])
    # Retorna a string final para o assistente de IA.
    return f"Grades for {student_name} in {course_name}:\n{grade_list}"

@tool
def list_courses_for_student(student_name: str) -> str:
    """
    Lists all the courses a specific student is enrolled in.
    """
    # Busca o aluno pelo nome.
    student = data_service.get_student_by_name(student_name)
    # Se não encontrar, retorna um erro.
    if not student:
        return f"Student '{student_name}' not found."

    # A lógica desta ferramenta requer uma consulta mais complexa, então busca todas as notas
    # com detalhes e depois filtra em memória.
    all_grades = data_service.get_all_grades_with_details()
    # Filtra para obter apenas as notas do aluno desejado.
    student_grades = [g for g in all_grades if g['student_id'] == student['id']]

    # Se o aluno não tiver notas, assume-se que não está matriculado em cursos.
    if not student_grades:
        return f"{student_name} is not enrolled in any courses with recorded grades."

    # Usa um conjunto (set) para obter uma lista de nomes de cursos únicos.
    course_names = {g['course_name'] for g in student_grades}
    # Formata a lista de cursos e a retorna.
    return f"Courses for {student_name}:\n" + "\n".join(f"- {name}" for name in sorted(list(course_names)))

@tool
def get_class_average(course_name: str) -> str:
    """
    Calculates the average grade for all students in a specific course.
    """
    # Busca o curso pelo nome.
    course = data_service.get_course_by_name(course_name)
    # Se não encontrar, retorna um erro.
    if not course:
        return f"Course '{course_name}' not found."

    # Lista para armazenar todas as notas de todas as turmas do curso.
    all_grades = []
    # Itera sobre as turmas do curso.
    for class_data in course['classes']:
        # Obtém as notas de cada turma e as adiciona à lista geral.
        grades_in_class = data_service.get_grades_for_class(class_data['id'])
        all_grades.extend(grades_in_class)

    # Se não houver notas no curso, retorna uma mensagem informativa.
    if not all_grades:
        return f"No grades found for the course {course_name}."

    # Calcula a média aritmética simples das notas.
    average = sum(g['score'] for g in all_grades) / len(all_grades)
    # Retorna a média formatada com duas casas decimais.
    return f"The class average for {course_name} is {average:.2f}."
