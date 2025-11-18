# Importa a exceção específica do SQLAlchemy para um tratamento de erro mais preciso.
from sqlalchemy.exc import SQLAlchemyError
# Importa o decorador 'tool' para registrar as funções como ferramentas de IA.
from app.core.tools.tool_decorator import tool
# Importa a instância compartilhada do DataService.
from app.services import data_service

# Registra a função como uma ferramenta disponível para a IA.
@tool
def add_new_student(first_name: str, last_name: str) -> str:
    """
    Adiciona um novo aluno ao banco de dados.
    Use esta ferramenta quando um usuário pedir explicitamente para adicionar ou criar um novo aluno.
    Retorna uma mensagem de confirmação.
    """
    # Validação básica dos parâmetros de entrada.
    if not first_name or not last_name:
        return "Erro: O nome e o sobrenome são obrigatórios."

    # Bloco try/except para capturar erros durante a operação de banco de dados.
    try:
        # Chama o método do DataService para adicionar o aluno.
        student = data_service.add_student(first_name, last_name)
        # Se o aluno for criado com sucesso (o método retorna os dados do aluno).
        if student:
            # Retorna uma mensagem de sucesso com o nome e o ID do novo aluno.
            return f"Novo aluno adicionado com sucesso: {first_name} {last_name} com ID {student['id']}."
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
def add_new_course(course_name: str, course_code: str) -> str:
    """
    Adiciona um novo curso ao banco de dados.
    Use esta ferramenta quando um usuário pedir explicitamente para adicionar ou criar um novo curso.
    Retorna uma mensagem de confirmação.
    """
    # Validação dos parâmetros de entrada.
    if not course_name or not course_code:
        return "Erro: O nome e o código do curso são obrigatórios."

    try:
        # Chama o método do DataService para adicionar o curso.
        course = data_service.add_course(course_name, course_code)
        # Se o curso for criado com sucesso.
        if course:
            # Retorna uma mensagem de sucesso.
            return f"Novo curso adicionado com sucesso: {course_name} ({course_code}) com ID {course['id']}."
        else:
            return f"Erro: Ocorreu um erro desconhecido ao adicionar o curso {course_name}."
    except SQLAlchemyError as e:
        return f"Erro: Ocorreu um erro de banco de dados ao adicionar o curso: {e}"
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
