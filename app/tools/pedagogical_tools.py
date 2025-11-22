# Importa o decorador 'tool' para registrar a função como uma ferramenta para a IA.
from app.core.tools.tool_decorator import tool

# Registra a função como uma ferramenta disponível para a IA.
@tool
def suggest_lesson_activities_tool(topic: str, student_level: str, num_suggestions: int = 3) -> str:
    """
    Gera uma string de solicitação para criar sugestões de atividades educacionais criativas e
    envolventes, adaptadas ao tema e nível dos alunos fornecidos.

    Esta função constrói um prompt de consulta usado pelo modelo de linguagem para gerar uma
    resposta completa. O prompt é desenvolvido para incentivar a criação de recomendações que
    satisfazem o contexto e os parâmetros especificados.

    :param topic: O tema principal ou assunto das atividades de aula.
    :type topic: str
    :param student_level: O nível de ensino ou faixa etária dos alunos (por exemplo,
        "ensino fundamental", "ensino médio").
    :type student_level: str
    :param num_suggestions: O número desejado de sugestões de atividades a serem
        geradas (por padrão, 3 sugestões).
    :type num_suggestions: int
    :return: Um prompt formatado contendo uma solicitação para o modelo, descrevendo
        o tópico, o nível estudantil e o número de atividades solicitadas.
    :rtype: str
    """
    # Esta ferramenta funciona como um "placeholder" (marcador de lugar) para as próprias capacidades geradoras do LLM.
    # O verdadeiro "trabalho" é feito pelo próprio LLM quando ele decide chamar esta ferramenta e formula a resposta final.
    # Ao fornecer uma docstring clara, nós guiamos o LLM sobre como usar seu próprio conhecimento para responder.
    # A string de retorno é, essencialmente, um prompt formatado que o LLM irá "responder" a si mesmo
    # na etapa seguinte do seu processo de pensamento, gerando uma resposta em linguagem natural para o usuário.
    return f"Por favor, forneça {num_suggestions} atividades de aula criativas e envolventes sobre '{topic}' adequadas para alunos de {student_level}. Para cada atividade, inclua uma breve descrição e os materiais necessários."
