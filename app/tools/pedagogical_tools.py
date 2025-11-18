# Importa o decorador 'tool' para registrar a função como uma ferramenta para a IA.
from app.core.tools.tool_decorator import tool

# Registra a função como uma ferramenta disponível para a IA.
@tool
def suggest_lesson_activities_tool(topic: str, student_level: str, num_suggestions: int = 3) -> str:
    """
    Generates a list of creative and relevant activity suggestions for a given lesson topic and student level.
    Use this tool when a teacher asks for ideas, activities, projects, or lesson plans on a specific subject.
    For example: "Suggest some activities about the water cycle for 5th graders."
    The tool's output is a direct response from the assistant to the user, not data to be interpreted.
    """
    # Esta ferramenta funciona como um "placeholder" (marcador de lugar) para as próprias capacidades geradoras do LLM.
    # O verdadeiro "trabalho" é feito pelo próprio LLM quando ele decide chamar esta ferramenta e formula a resposta final.
    # Ao fornecer uma docstring clara, nós guiamos o LLM sobre como usar seu próprio conhecimento para responder.
    # A string de retorno é, essencialmente, um prompt formatado que o LLM irá "responder" a si mesmo
    # na etapa seguinte do seu processo de pensamento, gerando uma resposta em linguagem natural para o usuário.
    return f"Please provide {num_suggestions} creative and engaging lesson activities about '{topic}' suitable for {student_level} students. For each activity, include a brief description and the required materials."
