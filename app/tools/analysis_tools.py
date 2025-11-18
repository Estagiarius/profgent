# Importa o módulo 'json' para converter os resultados em formato JSON.
import json
# Importa o decorador 'tool' que transforma uma função em uma ferramenta utilizável pela IA.
from app.core.tools.tool_decorator import tool
# Importa a classe DataService para interagir com o banco de dados.
from app.services.data_service import DataService

# Cria uma instância do DataService para ser usada pelas ferramentas neste módulo.
data_service = DataService()

# O decorador '@tool' registra esta função no ToolRegistry,
# gerando um esquema JSON a partir da docstring e das anotações de tipo.
# Este esquema é enviado para o LLM, permitindo que ele entenda como usar a função.
@tool
def get_student_performance_summary_tool(student_name: str, class_name: str) -> str:
    """
    Provides a detailed performance summary for a specific student in a specific class.
    Use this tool to answer questions about a student's grades, weighted average, incidents, and overall performance.
    """
    # Bloco try/except para capturar e tratar qualquer erro inesperado que possa ocorrer.
    try:
        # Busca o aluno pelo nome usando o DataService.
        student = data_service.get_student_by_name(student_name)
        # Se o aluno não for encontrado, retorna uma mensagem de erro clara.
        if not student:
            return f"Error: Student '{student_name}' not found."

        # Simplificação: Busca a turma pelo nome. Em uma aplicação real, isso poderia ser mais robusto.
        # Obtém todas as turmas.
        all_classes = data_service.get_all_classes()
        # Procura a turma cujo nome corresponde ao fornecido (ignorando maiúsculas/minúsculas).
        target_class = next((c for c in all_classes if c['name'].lower() == class_name.lower()), None)

        # Se a turma não for encontrada, retorna uma mensagem de erro.
        if not target_class:
            return f"Error: Class '{class_name}' not found."

        # Chama o DataService para obter o resumo de desempenho do aluno na turma.
        summary = data_service.get_student_performance_summary(student['id'], target_class['id'])

        # Se não for possível obter o resumo, retorna um erro.
        if not summary:
            return f"Error: Could not retrieve performance summary for {student_name} in {class_name}."

        # Retorna o resumo como uma string JSON formatada.
        # O LLM pode analisar (parse) esta string facilmente para usar os dados.
        return json.dumps(summary, indent=2)
    # Captura exceções genéricas.
    except Exception as e:
        # Retorna uma mensagem de erro informando sobre a falha inesperada.
        return f"Error: An unexpected error occurred: {e}"

@tool
def get_students_at_risk_tool(class_name: str) -> str:
    """
    Identifies and lists students who are at risk in a specific class based on low grades or a high number of incidents.
    Use this tool to answer questions like "Which students need help?" or "Show me students with performance issues."
    """
    try:
        # Busca a turma pelo nome.
        all_classes = data_service.get_all_classes()
        target_class = next((c for c in all_classes if c['name'].lower() == class_name.lower()), None)

        # Se a turma não for encontrada, retorna um erro.
        if not target_class:
            return f"Error: Class '{class_name}' not found."

        # Chama o DataService para obter a lista de alunos em risco.
        students_at_risk = data_service.get_students_at_risk(target_class['id'])

        # Se a lista estiver vazia, informa que nenhum aluno foi identificado como em risco.
        if not students_at_risk:
            return f"No students were identified as being at risk in {class_name}."

        # Retorna a lista de alunos em risco como uma string JSON formatada.
        return json.dumps(students_at_risk, indent=2)
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"
