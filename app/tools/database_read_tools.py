import json
from app.core.tools.tool_decorator import tool
from app.services.data_service import DataService

data_service = DataService()

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
