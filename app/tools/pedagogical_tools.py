# Importa o decorador 'tool' para registrar a função como uma ferramenta para a IA.
from app.core.tools.tool_decorator import tool

# Registra a função como uma ferramenta disponível para a IA.
@tool
def suggest_lesson_activities_tool(topic: str, student_level: str, num_suggestions: int = 3) -> str:
    """
    Gera uma lista de sugestões de atividades criativas e relevantes para um determinado tópico de aula e nível de aluno.
    Use esta ferramenta quando um professor pedir ideias, atividades, projetos ou planos de aula sobre um assunto específico.
    Por exemplo: "Sugira algumas atividades sobre o ciclo da água para alunos da 5ª série."
    A saída da ferramenta é uma resposta direta do assistente ao usuário, não dados a serem interpretados.
    """
    # Esta ferramenta funciona como um "placeholder" (marcador de lugar) para as próprias capacidades geradoras do LLM.
    # O verdadeiro "trabalho" é feito pelo próprio LLM quando ele decide chamar esta ferramenta e formula a resposta final.
    # Ao fornecer uma docstring clara, nós guiamos o LLM sobre como usar seu próprio conhecimento para responder.
    # A string de retorno é, essencialmente, um prompt formatado que o LLM irá "responder" a si mesmo
    # na etapa seguinte do seu processo de pensamento, gerando uma resposta em linguagem natural para o usuário.
    return f"Por favor, forneça {num_suggestions} atividades de aula criativas e envolventes sobre '{topic}' adequadas para alunos de {student_level}. Para cada atividade, inclua uma breve descrição e os materiais necessários."
