# Importa tipos para anotações de tipo.
from typing import List, Dict, Any, Callable

# Define a classe para o registro de ferramentas.
class ToolRegistry:
    """
    Um registro central para todas as ferramentas disponíveis para o assistente de IA.
    """
    # O método construtor.
    def __init__(self):
        # Um dicionário para mapear nomes de ferramentas para suas funções Python correspondentes.
        self.tools: Dict[str, Callable] = {}
        # Uma lista para armazenar os esquemas JSON de todas as ferramentas registradas.
        self.schemas: List[Dict[str, Any]] = []

    # Método para registrar uma nova função de ferramenta.
    def register(self, tool_func: Callable):
        """
        Registra uma função de ferramenta.

        A função deve ser decorada com o decorador @tool para ter um esquema.
        """
        # Verifica se a função possui o atributo '.schema', que é anexado pelo decorador @tool.
        # Se não tiver, a função não é uma ferramenta válida.
        if not hasattr(tool_func, 'schema'):
            raise ValueError(f"A função {tool_func.__name__} não é uma ferramenta válida. Você esqueceu o decorador @tool?")

        # Obtém o nome da ferramenta a partir do seu esquema.
        tool_name = tool_func.schema["function"]["name"]
        # Adiciona a função ao dicionário de ferramentas.
        self.tools[tool_name] = tool_func
        # Adiciona o esquema da ferramenta à lista de esquemas.
        self.schemas.append(tool_func.schema)
        print(f"Ferramenta registrada: {tool_name}")

    # Método para obter uma função de ferramenta pelo seu nome.
    def get_tool(self, name: str) -> Callable | None:
        """Recupera uma função de ferramenta pelo seu nome."""
        # Usa o método `.get()` do dicionário para retornar a função ou None se não for encontrada.
        return self.tools.get(name)

    # Método para obter os esquemas de todas as ferramentas registradas.
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Retorna os esquemas JSON de todas as ferramentas registradas."""
        return self.schemas
