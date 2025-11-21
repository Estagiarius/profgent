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
    Adiciona um novo aluno ao banco de dados.
    Opcionalmente, inclui data de nascimento (DD/MM/AAAA) e matricula em uma turma existente.
    Use esta ferramenta quando um usuário pedir explicitamente para adicionar ou criar um novo aluno.
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
                all_classes = data_service.get_all_classes()
                target_class = next((c for c in all_classes if c['name'].lower() == enroll_in_class.lower()), None)

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
    Cria um novo registro de aula (Lesson) ou plano de aula para uma turma específica.
    Parâmetros:
    - class_name: Nome da turma.
    - topic: Título ou tópico da aula.
    - content: Conteúdo detalhado ou plano de aula.
    - date_str: Data da aula no formato DD/MM/AAAA.
    """
    try:
        # Busca a turma
        all_classes = data_service.get_all_classes()
        target_class = next((c for c in all_classes if c['name'].lower() == class_name.lower()), None)

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
    Registra um novo incidente ou ocorrência para um aluno em uma turma.
    Parâmetros:
    - student_name: Nome do aluno.
    - class_name: Nome da turma.
    - description: Descrição do incidente.
    - date_str: Data do ocorrido no formato DD/MM/AAAA.
    """
    try:
        # Busca o aluno
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Erro: Aluno '{student_name}' não encontrado."

        # Busca a turma
        all_classes = data_service.get_all_classes()
        target_class = next((c for c in all_classes if c['name'].lower() == class_name.lower()), None)
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
    Adiciona uma nova disciplina ao banco de dados.
    Use esta ferramenta quando um usuário pedir explicitamente para adicionar ou criar uma nova disciplina.
    Retorna uma mensagem de confirmação.
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
    Adiciona uma nova nota para um aluno em uma avaliação específica de uma turma.
    """
    try:
        # Passo 1: Encontrar o aluno pelo nome.
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Erro: Aluno '{student_name}' não encontrado."

        # Passo 2: Encontrar a turma pelo nome.
        all_classes_data = data_service.get_all_classes()
        target_class_data = next((c for c in all_classes_data if c["name"].lower() == class_name.lower()), None)
        if not target_class_data:
            return f"Erro: Turma '{class_name}' não encontrada."

        # Passo 3: Obter detalhes completos da turma para encontrar a avaliação.
        # A busca inicial (get_all_classes) pode não carregar dados aninhados como as avaliações.
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
