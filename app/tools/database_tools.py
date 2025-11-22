import json
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.core.tools.tool_decorator import tool
from app.services import data_service

# --- READ TOOLS ---

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
    student = data_service.get_student_by_name(student_name)
    if not student:
        return f"Aluno '{student_name}' não encontrado."

    course = data_service.get_course_by_name(course_name)
    if not course:
        return f"Disciplina '{course_name}' não encontrada."

    student_grades_in_course = []
    for class_data in course['classes']:
        grades_in_class = data_service.get_grades_for_class(class_data['id'])
        student_grades_in_class = [g for g in grades_in_class if g['student_id'] == student['id']]
        student_grades_in_course.extend(student_grades_in_class)

    if not student_grades_in_course:
        return f"Nenhuma nota encontrada para {student_name} em {course_name}."

    grade_list = "\n".join([f"- {g['assessment_name']}: {g['score']}" for g in student_grades_in_course])
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
    student = data_service.get_student_by_name(student_name)
    if not student:
        return f"Aluno '{student_name}' não encontrado."

    all_grades = data_service.get_all_grades_with_details()
    student_grades = [g for g in all_grades if g['student_id'] == student['id']]

    if not student_grades:
        return f"{student_name} não está matriculado(a) em nenhuma disciplina com notas registradas."

    course_names = {g['course_name'] for g in student_grades}
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
    course = data_service.get_course_by_name(course_name)
    if not course:
        return f"Disciplina '{course_name}' não encontrada."

    all_grades = []
    for class_data in course['classes']:
        grades_in_class = data_service.get_grades_for_class(class_data['id'])
        all_grades.extend(grades_in_class)

    if not all_grades:
        return f"Nenhuma nota encontrada para a disciplina {course_name}."

    average = sum(g['score'] for g in all_grades) / len(all_grades)
    return f"A média da turma para {course_name} é {average:.2f}."

@tool
def list_all_classes() -> str:
    """
    Lista todas as turmas cadastradas no sistema, incluindo o nome da disciplina
    associada e a quantidade de alunos matriculados em cada turma.

    Esta ferramenta é útil para fornecer uma visão geral da estrutura escolar
    ou ajudar o usuário a encontrar o nome correto de uma turma.

    :return: Uma string contendo a lista de turmas ou uma mensagem informando que não há turmas.
    """
    try:
        classes = data_service.get_all_classes()
        if not classes:
            return "Não há turmas cadastradas no sistema."

        # Format the output for better readability by the LLM
        result = []
        for cls in classes:
            result.append(f"Turma: {cls['name']} | Disciplina: {cls['course_name']} | Alunos: {cls['student_count']}")

        return "\n".join(result)
    except Exception as e:
        return f"Erro ao listar turmas: {e}"

@tool
def get_class_roster(class_name: str) -> str:
    """
    Obtém a lista de chamada (roster) de uma turma específica, listando todos os alunos
    matriculados, seus números de chamada e status atual.

    :param class_name: O nome da turma para a qual se deseja obter a lista de alunos.
    :return: Uma string com a lista de alunos formatada ou uma mensagem de erro.
    """
    try:
        target_class = data_service.get_class_by_name(class_name)
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        enrollments = data_service.get_enrollments_for_class(target_class['id'])

        if not enrollments:
            return f"A turma '{class_name}' não possui alunos matriculados."

        result = [f"Lista de Chamada para a Turma: {class_name}"]
        for env in enrollments:
            line = f"#{env['call_number']} - {env['student_first_name']} {env['student_last_name']} ({env['status']})"
            result.append(line)

        return "\n".join(result)
    except Exception as e:
        return f"Erro ao obter lista de alunos: {e}"

# --- WRITE TOOLS ---

@tool
def add_new_student(first_name: str, last_name: str, date_of_birth: str = None, enroll_in_class: str = None) -> str:
    """
    Adiciona um novo aluno ao sistema, com opção de matrícula em uma turma específica,
    realizando validações nos dados fornecidos e comunicando-se com o serviço de dados
    para persistência da informação.

    Se uma data de nascimento for fornecida, ela será validada para o formato "DD/MM/AAAA".
    Opcionalmente, o aluno pode ser matriculado em uma turma existente no sistema.

    :param first_name: Nome do aluno.
    :param last_name: Sobrenome do aluno.
    :param date_of_birth: Data de nascimento do aluno, no formato "DD/MM/AAAA" (opcional).
    :param enroll_in_class: Nome da turma onde o aluno será matriculado (opcional).
    :return: Mensagem com o resultado da operação, seja ela um sucesso ou mensagem de erro.
    """
    if not first_name or not last_name:
        return "Erro: O nome e o sobrenome são obrigatórios."

    birth_date_obj = None
    if date_of_birth:
        try:
            birth_date_obj = datetime.strptime(date_of_birth, "%d/%m/%Y").date()
        except ValueError:
            return f"Erro: Formato de data inválido '{date_of_birth}'. Use DD/MM/AAAA."

    try:
        student = data_service.add_student(first_name, last_name, birth_date=birth_date_obj)

        if student:
            response_msg = f"Novo aluno adicionado com sucesso: {first_name} {last_name} com ID {student['id']}."

            if enroll_in_class:
                target_class = data_service.get_class_by_name(enroll_in_class)

                if target_class:
                    next_call_number = data_service.get_next_call_number(target_class['id'])
                    enrollment = data_service.add_student_to_class(student['id'], target_class['id'], next_call_number)
                    if enrollment:
                        response_msg += f" Matriculado na turma '{target_class['name']}'."
                    else:
                        response_msg += f" Falha ao matricular na turma '{target_class['name']}'."
                else:
                    response_msg += f" Turma '{enroll_in_class}' não encontrada para matrícula."

            return response_msg
        else:
            return f"Erro: Ocorreu um erro desconhecido ao adicionar o aluno {first_name} {last_name}."
    except SQLAlchemyError as e:
        return f"Erro: Ocorreu um erro de banco de dados ao adicionar o aluno: {e}"
    except Exception as e:
        return f"Erro: Ocorreu um erro inesperado: {e}"

@tool
def add_new_lesson(class_name: str, topic: str, content: str, date_str: str) -> str:
    """
    Adiciona uma nova aula a uma turma específica, baseada no nome da turma,
    tópico, conteúdo e data fornecidos. Retorna uma mensagem de sucesso
    ou erro, dependendo da operação.

    :param class_name: Nome da turma onde a aula será adicionada.
    :type class_name: str
    :param topic: Tópico da aula a ser registrada.
    :type topic: str
    :param content: Conteúdo da aula a ser registrada.
    :type content: str
    :param date_str: Data da aula no formato DD/MM/AAAA.
    :type date_str: str
    :return: Mensagem de confirmação ou erro relacionado ao registro da aula.
    :rtype: str
    """
    try:
        target_class = data_service.get_class_by_name(class_name)

        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        try:
            lesson_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            return f"Erro: Formato de data inválido '{date_str}'. Use DD/MM/AAAA."

        lesson = data_service.create_lesson(target_class['id'], topic, content, lesson_date)

        if lesson:
            return f"Aula '{topic}' registrada com sucesso para a turma '{class_name}' em {date_str}."
        else:
            return "Erro: Falha ao criar o registro da aula."

    except Exception as e:
        return f"Erro: Ocorreu um erro inesperado: {e}"

@tool
def register_incident(student_name: str, class_name: str, description: str, date_str: str) -> str:
    """
    Registra um incidente relacionado a um aluno em uma turma específica em uma data fornecida.

    Este método realiza o registro de um incidente ao conectar-se a serviços de dados para localizar o aluno e a turma
    especificados. Em caso de sucesso, o incidente é registrado com os detalhes fornecidos, incluindo uma
    descrição e uma data formatada corretamente no padrão DD/MM/AAAA.

    :param student_name: Nome do aluno relacionado ao incidente.
    :type student_name: str
    :param class_name: Nome da turma onde ocorreu o incidente.
    :type class_name: str
    :param description: Descrição detalhada do incidente ocorrido.
    :type description: str
    :param date_str: Data do incidente no formato DD/MM/AAAA.
    :type date_str: str
    :return: Mensagem detalhando o status do registro do incidente, seja sucesso ou erro.
    :rtype: str
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Erro: Aluno '{student_name}' não encontrado."

        target_class = data_service.get_class_by_name(class_name)
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        try:
            incident_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            return f"Erro: Formato de data inválido '{date_str}'. Use DD/MM/AAAA."

        incident = data_service.create_incident(target_class['id'], student['id'], description, incident_date)

        if incident:
            return f"Incidente registrado para {student_name} na turma {class_name} em {date_str}."
        else:
            return "Erro: Falha ao registrar o incidente."

    except Exception as e:
        return f"Erro: Ocorreu um erro inesperado: {e}"

@tool
def add_new_course(course_name: str, course_code: str) -> str:
    """
    Adiciona uma nova disciplina ao sistema utilizando as informações fornecidas pelo usuário. Esta função valida
    os parâmetros de entrada e interage com o serviço responsável pelos dados para criar um novo registro de
    disciplina. Retorna uma mensagem indicando o sucesso ou falha da operação.

    :param course_name: Nome completo da disciplina a ser adicionada.
    :type course_name: str
    :param course_code: Código identificador único da disciplina.
    :type course_code: str
    :return: Uma mensagem indicando o status da operação de adição, incluindo erros caso necessário.
    :rtype: str
    """
    if not course_name or not course_code:
        return "Erro: O nome e o código da disciplina são obrigatórios."

    try:
        course = data_service.add_course(course_name, course_code)
        if course:
            return f"Nova disciplina adicionada com sucesso: {course_name} ({course_code}) com ID {course['id']}."
        else:
            return f"Erro: Ocorreu um erro desconhecido ao adicionar a disciplina {course_name}."
    except SQLAlchemyError as e:
        return f"Erro: Ocorreu um erro de banco de dados ao adicionar a disciplina: {e}"
    except Exception as e:
        return f"Erro: Ocorreu um erro inesperado: {e}"

@tool
def add_new_grade(student_name: str, class_name: str, assessment_name: str, score: float) -> str:
    """
    Adiciona uma nova nota para um aluno em uma avaliação específica dentro de uma turma.

    Essa função realiza uma série de etapas para adicionar a nota:
    - Localiza o aluno pelo nome fornecido.
    - Localiza a turma correspondente ao nome fornecido.
    - Obtém os detalhes completos da turma para validar a avaliação.
    - Localiza a avaliação pelo nome.
    - Adiciona a nota do aluno para a avaliação identificada.

    :param student_name: Nome do aluno para o qual a nota será adicionada.
    :type student_name: str
    :param class_name: Nome da turma onde a avaliação está cadastrada.
    :type class_name: str
    :param assessment_name: Nome da avaliação na qual a nota será registrada.
    :type assessment_name: str
    :param score: Nota atribuída ao aluno para a avaliação especificada.
    :type score: float
    :return: Mensagem indicando o sucesso ou erro na operação.
    :rtype: str
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Erro: Aluno '{student_name}' não encontrado."

        target_class_data = data_service.get_class_by_name(class_name)
        if not target_class_data:
            return f"Erro: Turma '{class_name}' não encontrada."

        full_class_details = data_service.get_class_by_id(target_class_data["id"])
        if not full_class_details:
             return f"Erro: Não foi possível obter os detalhes da turma '{class_name}'."

        assessment = next((a for a in full_class_details['assessments'] if a['name'].lower() == assessment_name.lower()), None)
        if not assessment:
            return f"Erro: Avaliação '{assessment_name}' não encontrada na turma '{class_name}'."

        grade = data_service.add_grade(student['id'], assessment['id'], score)
        if grade:
            return f"Nota adicionada com sucesso para {student_name} em {full_class_details['course_name']}."
        else:
            return "Erro: Não foi possível adicionar a nota."
    except Exception as e:
        return f"Erro: Ocorreu um erro inesperado: {e}"

@tool
def create_new_class(course_name: str, class_name: str) -> str:
    """
    Cria uma nova turma (Classe) associada a uma disciplina (Curso) existente.

    Esta função verifica se a disciplina existe e se a turma já não foi criada.

    :param course_name: O nome da disciplina (Curso) à qual a turma pertencerá.
    :param class_name: O nome da nova turma a ser criada (ex: "Turma A - 2024").
    :return: Uma mensagem de sucesso ou erro.
    """
    if not course_name or not class_name:
        return "Erro: Nome da disciplina e nome da turma são obrigatórios."

    try:
        course = data_service.get_course_by_name(course_name)
        if not course:
            return f"Erro: Disciplina '{course_name}' não encontrada."

        existing_class = data_service.get_class_by_name(class_name)
        if existing_class:
            return f"Erro: Já existe uma turma com o nome '{class_name}'."

        new_class = data_service.create_class(class_name, course['id'])
        if new_class:
            return f"Turma '{class_name}' criada com sucesso para a disciplina '{course_name}'."
        else:
            return "Erro: Falha ao criar a turma."
    except Exception as e:
        return f"Erro inesperado ao criar turma: {e}"

@tool
def create_new_assessment(class_name: str, assessment_name: str, weight: float) -> str:
    """
    Cria uma nova avaliação para uma turma específica.

    Esta função permite definir o nome da avaliação (ex: "Prova 1") e seu peso
    na nota final (ex: 1.0, 0.5).

    :param class_name: O nome da turma para a qual a avaliação será criada.
    :param assessment_name: O nome da avaliação.
    :param weight: O peso da avaliação (número flutuante).
    :return: Uma mensagem de sucesso ou erro.
    """
    if not class_name or not assessment_name or weight is None:
        return "Erro: Nome da turma, nome da avaliação e peso são obrigatórios."

    try:
        target_class = data_service.get_class_by_name(class_name)
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        assessment = data_service.add_assessment(target_class['id'], assessment_name, weight)
        if assessment:
            return f"Avaliação '{assessment_name}' (Peso: {weight}) criada com sucesso para a turma '{class_name}'."
        else:
            return "Erro: Falha ao criar a avaliação."
    except Exception as e:
        return f"Erro inesperado ao criar avaliação: {e}"

# --- MAINTENANCE TOOLS (Group 2) ---

@tool
def update_student_name(current_name: str, new_first_name: str, new_last_name: str) -> str:
    """
    Atualiza o nome e sobrenome de um aluno existente.

    :param current_name: O nome completo atual do aluno para busca.
    :param new_first_name: O novo primeiro nome.
    :param new_last_name: O novo sobrenome.
    """
    try:
        student = data_service.get_student_by_name(current_name)
        if not student:
            return f"Erro: Aluno '{current_name}' não encontrado."

        data_service.update_student(student['id'], new_first_name, new_last_name)
        return f"Nome do aluno atualizado para {new_first_name} {new_last_name}."
    except Exception as e:
        return f"Erro ao atualizar aluno: {e}"

@tool
def update_class_name(current_name: str, new_name: str) -> str:
    """
    Atualiza o nome de uma turma existente.

    :param current_name: O nome atual da turma.
    :param new_name: O novo nome da turma.
    """
    try:
        target_class = data_service.get_class_by_name(current_name)
        if not target_class:
            return f"Erro: Turma '{current_name}' não encontrada."

        data_service.update_class(target_class['id'], new_name)
        return f"Nome da turma atualizado para '{new_name}'."
    except Exception as e:
        return f"Erro ao atualizar turma: {e}"

@tool
def delete_student_record(student_name: str) -> str:
    """
    Remove permanentemente o registro de um aluno do sistema, incluindo suas notas e histórico.
    Use com cautela.

    :param student_name: Nome completo do aluno a ser removido.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Erro: Aluno '{student_name}' não encontrado."

        data_service.delete_student(student['id'])
        return f"Registro do aluno {student_name} foi removido com sucesso."
    except Exception as e:
        return f"Erro ao remover aluno: {e}"

@tool
def delete_class_record(class_name: str) -> str:
    """
    Remove permanentemente uma turma e todos os registros associados (matrículas, aulas).

    :param class_name: Nome da turma a ser removida.
    """
    try:
        target_class = data_service.get_class_by_name(class_name)
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        data_service.delete_class(target_class['id'])
        return f"Turma '{class_name}' foi removida com sucesso."
    except Exception as e:
        return f"Erro ao remover turma: {e}"

# --- ENROLLMENT TOOLS (Group 3) ---

@tool
def enroll_existing_student(student_name: str, class_name: str) -> str:
    """
    Matricula um aluno JÁ EXISTENTE no sistema em uma nova turma.
    Se o aluno não existir, use 'add_new_student' em vez disso.

    :param student_name: Nome completo do aluno.
    :param class_name: Nome da turma onde será matriculado.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Erro: Aluno '{student_name}' não encontrado. Se for um aluno novo, use a função para adicionar aluno."

        target_class = data_service.get_class_by_name(class_name)
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        next_call_number = data_service.get_next_call_number(target_class['id'])
        enrollment = data_service.add_student_to_class(student['id'], target_class['id'], next_call_number)

        if enrollment:
            return f"Aluno {student_name} matriculado com sucesso na turma '{class_name}' (Nº {next_call_number})."
        else:
            return f"Erro ao matricular aluno na turma '{class_name}'."
    except Exception as e:
        return f"Erro inesperado na matrícula: {e}"

@tool
def change_student_status(student_name: str, class_name: str, new_status: str) -> str:
    """
    Altera o status de matrícula de um aluno em uma turma específica (ex: "Active", "Inactive", "Transferred").

    :param student_name: Nome do aluno.
    :param class_name: Nome da turma.
    :param new_status: Novo status (em inglês, ex: 'Active', 'Inactive').
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Erro: Aluno '{student_name}' não encontrado."

        target_class = data_service.get_class_by_name(class_name)
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        enrollments = data_service.get_enrollments_for_class(target_class['id'])
        # Find the specific enrollment for this student
        target_enrollment = next((e for e in enrollments if e['student_id'] == student['id']), None)

        if not target_enrollment:
            return f"Erro: Aluno {student_name} não está matriculado na turma '{class_name}'."

        data_service.update_enrollment_status(target_enrollment['id'], new_status)
        return f"Status de {student_name} na turma '{class_name}' alterado para '{new_status}'."
    except Exception as e:
        return f"Erro ao alterar status: {e}"
