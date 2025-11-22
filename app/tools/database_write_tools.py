# Importa datetime para manipulação de datas.
from datetime import datetime
# Importa a exceção específica do SQLAlchemy para um tratamento de erro mais preciso.
from sqlalchemy.exc import SQLAlchemyError
# Importa o decorador 'tool' para registrar as funções como ferramentas de IA.
from app.core.tools.tool_decorator import tool
# Importa a instância compartilhada do DataService.
from app.services import data_service

# Registra a função como uma ferramenta disponível para a IA.
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
    # Validação básica dos parâmetros de entrada.
    if not first_name or not last_name:
        return "Erro: O nome e o sobrenome são obrigatórios."

    # Parse da data de nascimento, se fornecida
    birth_date_obj = None
    if date_of_birth:
        try:
            birth_date_obj = datetime.strptime(date_of_birth, "%d/%m/%Y").date()
        except ValueError:
            return f"Erro: Formato de data inválido '{date_of_birth}'. Use DD/MM/AAAA."

    # Bloco try/except para capturar erros durante a operação de banco de dados.
    try:
        # Chama o método do DataService para adicionar o aluno.
        student = data_service.add_student(first_name, last_name, birth_date=birth_date_obj)

        # Se o aluno for criado com sucesso (o método retorna os dados do aluno).
        if student:
            response_msg = f"Novo aluno adicionado com sucesso: {first_name} {last_name} com ID {student['id']}."

            # Lógica de matrícula opcional
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
        # Caso o método do serviço retorne None ou falhe silenciosamente.
        else:
            return f"Erro: Ocorreu um erro desconhecido ao adicionar o aluno {first_name} {last_name}."
    # Captura erros específicos do SQLAlchemy.
    except SQLAlchemyError as e:
        return f"Erro: Ocorreu um erro de banco de dados ao adicionar o aluno: {e}"
    # Captura qualquer outro erro inesperado.
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
        # Busca a turma
        target_class = data_service.get_class_by_name(class_name)

        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        # Parse da data
        try:
            lesson_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            return f"Erro: Formato de data inválido '{date_str}'. Use DD/MM/AAAA."

        # Cria a aula
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
        # Busca o aluno
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Erro: Aluno '{student_name}' não encontrado."

        # Busca a turma
        target_class = data_service.get_class_by_name(class_name)
        if not target_class:
            return f"Erro: Turma '{class_name}' não encontrada."

        # Parse da data
        try:
            incident_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            return f"Erro: Formato de data inválido '{date_str}'. Use DD/MM/AAAA."

        # Registra o incidente
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
    # Validação dos parâmetros de entrada.
    if not course_name or not course_code:
        return "Erro: O nome e o código da disciplina são obrigatórios."

    try:
        # Chama o método do DataService para adicionar o curso.
        course = data_service.add_course(course_name, course_code)
        # Se o curso for criado com sucesso.
        if course:
            # Retorna uma mensagem de sucesso.
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
        # Passo 1: Encontrar o aluno pelo nome.
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Erro: Aluno '{student_name}' não encontrado."

        # Passo 2: Encontrar a turma pelo nome.
        target_class_data = data_service.get_class_by_name(class_name)
        if not target_class_data:
            return f"Erro: Turma '{class_name}' não encontrada."

        # Passo 3: Obter detalhes completos da turma para encontrar a avaliação.
        full_class_details = data_service.get_class_by_id(target_class_data["id"])
        if not full_class_details:
             return f"Erro: Não foi possível obter os detalhes da turma '{class_name}'."

        # Passo 4: Encontrar a avaliação pelo nome dentro dos detalhes da turma.
        assessment = next((a for a in full_class_details['assessments'] if a['name'].lower() == assessment_name.lower()), None)
        if not assessment:
            return f"Erro: Avaliação '{assessment_name}' não encontrada na turma '{class_name}'."

        # Passo 5: Adicionar a nota usando os IDs encontrados.
        grade = data_service.add_grade(student['id'], assessment['id'], score)
        if grade:
            # Retorna uma mensagem de sucesso.
            return f"Nota adicionada com sucesso para {student_name} em {full_class_details['course_name']}."
        else:
            return "Erro: Não foi possível adicionar a nota."
    except Exception as e:
        return f"Erro: Ocorreu um erro inesperado: {e}"
