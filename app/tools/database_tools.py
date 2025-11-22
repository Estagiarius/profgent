import json
# Importa o decorador 'tool' que registra a função como uma ferramenta para a IA.
from app.core.tools.tool_decorator import tool
# Importa a instância compartilhada do DataService criada no __init__.py do pacote 'services'.
from app.services import data_service

# O decorador '@tool' informa ao sistema que esta função é uma ferramenta que a IA pode chamar.
@tool
def get_student_grade(student_name: str, course_name: str) -> str:
    """
    Obtém as notas de um aluno específico em um curso (disciplina) específico.
    O método realiza múltiplas verificações, incluindo a existência de aluno e
    curso, além de agregar as notas em todas as turmas associadas à disciplina
    informada.

    :param student_name: Nome do aluno cujo desempenho será analisado.
    :type student_name: str
    :param course_name: Nome do curso (disciplina) em que se deseja obter as notas.
    :type course_name: str
    :return: String formatada contendo todas as notas encontradas para o aluno no
        curso especificado. Retorna mensagens de erro claras se o aluno, curso ou
        notas não forem encontrados.
    :rtype: str
    """
    # Busca o aluno pelo nome usando o serviço de dados.
    student = data_service.get_student_by_name(student_name)
    # Se o aluno não for encontrado, retorna uma mensagem de erro.
    if not student:
        return f"Aluno '{student_name}' não encontrado."

    # Busca o curso (disciplina) pelo nome.
    course = data_service.get_course_by_name(course_name)
    # Se a disciplina não for encontrada, retorna uma mensagem de erro.
    if not course:
        return f"Disciplina '{course_name}' não encontrada."

    # Lista para armazenar todas as notas do aluno encontradas na disciplina.
    student_grades_in_course = []
    # Itera sobre todas as turmas associadas à disciplina.
    for class_data in course['classes']:
        # Obtém todas as notas da turma.
        grades_in_class = data_service.get_grades_for_class(class_data['id'])
        # Filtra as notas para encontrar apenas as do aluno específico.
        student_grades_in_class = [g for g in grades_in_class if g['student_id'] == student['id']]
        # Adiciona as notas encontradas à lista principal.
        student_grades_in_course.extend(student_grades_in_class)

    # Se nenhuma nota foi encontrada, retorna uma mensagem informativa.
    if not student_grades_in_course:
        return f"Nenhuma nota encontrada para {student_name} em {course_name}."

    # Formata a lista de notas em uma string legível.
    grade_list = "\n".join([f"- {g['assessment_name']}: {g['score']}" for g in student_grades_in_course])
    # Retorna a string final para o assistente de IA.
    return f"Notas de {student_name} em {course_name}:\n{grade_list}"

@tool
def list_courses_for_student(student_name: str) -> str:
    """
    Lista as disciplinas nas quais o aluno com o nome especificado está matriculado,
    baseando-se nos dados de notas registradas. Caso o aluno não seja encontrado ou não
    haja registros de disciplinas, uma mensagem apropriada será retornada.

    :param student_name: O nome do aluno cujo histórico de disciplinas será consultado.
    :type student_name: str
    :return: Uma string contendo a lista de disciplinas do aluno ou uma mensagem indicando
             que o aluno não foi encontrado ou que não há disciplinas registradas.
    :rtype: str
    """
    # Busca o aluno pelo nome.
    student = data_service.get_student_by_name(student_name)
    # Se não encontrar, retorna um erro.
    if not student:
        return f"Aluno '{student_name}' não encontrado."

    # A lógica desta ferramenta requer uma consulta mais complexa, então busca todas as notas
    # com detalhes e depois filtra em memória.
    all_grades = data_service.get_all_grades_with_details()
    # Filtra para obter apenas as notas do aluno desejado.
    student_grades = [g for g in all_grades if g['student_id'] == student['id']]

    # Se o aluno não tiver notas, assume-se que não está matriculado em disciplinas.
    if not student_grades:
        return f"{student_name} não está matriculado(a) em nenhuma disciplina com notas registradas."

    # Usa um conjunto (set) para obter uma lista de nomes de disciplinas únicos.
    course_names = {g['course_name'] for g in student_grades}
    # Formata a lista de disciplinas e a retorna.
    return f"Disciplinas de {student_name}:\n" + "\n".join(f"- {name}" for name in sorted(list(course_names)))

@tool
def get_class_average(course_name: str) -> str:
    """
    Calcula a média aritmética simples de todas as notas de todas as turmas de uma
    determinada disciplina.

    Busca a disciplina pelo nome fornecido, acessa as informações relevantes de cada
    turma associada e coleta as notas dos estudantes. Após compilar todas as notas,
    o algoritmo calcula a média simples e retorna o resultado. Caso não encontre a
    disciplina ou notas associadas, retornará mensagens informativas para cada
    situação.

    :param course_name: Nome da disciplina para a qual a média será calculada.
    :type course_name: str
    :return: String com a média formatada ou mensagem de erro/informação caso
             a disciplina ou notas não sejam encontradas.
    :rtype: str
    """
    # Busca a disciplina pelo nome.
    course = data_service.get_course_by_name(course_name)
    # Se não encontrar, retorna um erro.
    if not course:
        return f"Disciplina '{course_name}' não encontrada."

    # Lista para armazenar todas as notas de todas as turmas da disciplina.
    all_grades = []
    # Itera sobre as turmas da disciplina.
    for class_data in course['classes']:
        # Obtém as notas de cada turma e as adiciona à lista geral.
        grades_in_class = data_service.get_grades_for_class(class_data['id'])
        all_grades.extend(grades_in_class)

    # Se não houver notas na disciplina, retorna uma mensagem informativa.
    if not all_grades:
        return f"Nenhuma nota encontrada para a disciplina {course_name}."

    # Calcula a média aritmética simples das notas.
    average = sum(g['score'] for g in all_grades) / len(all_grades)
    # Retorna a média formatada com duas casas decimais.
    return f"A média da turma para {course_name} é {average:.2f}."

@tool
def get_class_roster(class_name: str) -> str:
    """
    Obtém a lista dos alunos matriculados em uma determinada turma.

    Esta função acessa um serviço de dados para buscar todas as turmas disponíveis,
    encontra a turma especificada pelo nome e recupera as matrículas associadas a
    essa turma. Se a turma não for encontrada ou estiver vazia, mensagens de erro
    ou informação relevante serão retornadas.

    :param class_name: Nome da turma em formato string. O nome não diferencia
        maiúsculas de minúsculas.
    :type class_name: str
    :return: Retorna um JSON formatado contendo a lista de alunos da turma
        com os atributos "call_number", "name" e "status". Caso a turma
        não seja encontrada ou não tenha alunos matriculados,
        retorna uma mensagem correspondente.
    :rtype: str
    """
    try:
        # Busca todas as turmas para encontrar o ID da turma solicitada.
        all_classes = data_service.get_all_classes()
        target_class = next((c for c in all_classes if c['name'].lower() == class_name.lower()), None)

        # Se a turma não for encontrada, retorna um erro.
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        # Busca as matrículas da turma.
        enrollments = data_service.get_enrollments_for_class(target_class['id'])

        # Se não houver alunos matriculados.
        if not enrollments:
            return f"A turma {class_name} não possui alunos matriculados."

        # Formata a lista de alunos para retorno.
        roster = []
        for enrollment in enrollments:
            roster.append({
                "call_number": enrollment['call_number'],
                "name": f"{enrollment['student_first_name']} {enrollment['student_last_name']}",
                "status": enrollment['status']
            })

        # Retorna a lista como JSON.
        return json.dumps(roster, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Erro: Ocorreu um erro inesperado: {e}"
