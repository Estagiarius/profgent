# Importa o módulo 'json' para analisar os argumentos da ferramenta.
import json
# Importa tipos para anotações.
from typing import Dict, Any, Callable
# Importa a classe ToolRegistry para acessar as ferramentas registradas.
from app.core.tools.tool_registry import ToolRegistry

# Define a classe que executa as ferramentas.
class ToolExecutor:
    """
    Handles the secure execution of tools requested by the LLM.
    """
    # O método construtor.
    def __init__(self, registry: ToolRegistry):
        # Armazena a instância do registro de ferramentas.
        self.registry = registry

    # Método para executar uma única chamada de ferramenta.
    def execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a single tool call from the LLM's response.

        Args:
            tool_call: The tool call object from the LLM (e.g., from response.tool_calls).

        Returns:
            A dictionary representing the result to be sent back to the LLM.
        """
        # Obtém o nome da função da ferramenta a ser chamada.
        tool_name = tool_call.function.name
        # Busca a função Python real no registro de ferramentas.
        tool_function = self.registry.get_tool(tool_name)

        # Se a ferramenta solicitada não for encontrada no registro, retorna um erro.
        if not tool_function:
            return self._create_error_result(tool_call.id, f"Tool '{tool_name}' not found.")

        try:
            # Analisa (parse) de forma segura a string de argumentos JSON fornecida pelo LLM.
            arguments = json.loads(tool_call.function.arguments)

            # Executa a função da ferramenta, desempacotando o dicionário de argumentos
            # para passá-los como argumentos nomeados (ex: `func(arg1="valor1", arg2="valor2")`).
            result = tool_function(**arguments)

            # Se a execução for bem-sucedida, cria e retorna uma mensagem de resultado de sucesso.
            return self._create_success_result(tool_call.id, tool_name, result)

        # Captura erros se a string de argumentos do LLM não for um JSON válido.
        except json.JSONDecodeError:
            return self._create_error_result(tool_call.id, "Invalid arguments format. Expected a valid JSON string.")
        # Captura erros se os argumentos, mesmo sendo JSON válido, não corresponderem aos parâmetros da função.
        except TypeError as e:
            return self._create_error_result(tool_call.id, f"Invalid arguments for tool '{tool_name}': {e}")
        # Captura quaisquer outros erros inesperados durante a execução da ferramenta.
        except Exception as e:
            return self._create_error_result(tool_call.id, f"An unexpected error occurred: {e}")

    # Método auxiliar privado para criar uma mensagem de resultado de sucesso.
    def _create_success_result(self, tool_call_id: str, tool_name: str, result: Any) -> Dict[str, Any]:
        # Formata a resposta no padrão esperado pela API da OpenAI.
        return {
            "tool_call_id": tool_call_id, # O ID da chamada original, para o LLM saber a qual solicitação este resultado corresponde.
            "role": "tool",              # A 'role' (função) deve ser "tool".
            "name": tool_name,           # O nome da ferramenta que foi executada.
            "content": str(result),      # O resultado da execução da ferramenta, convertido para string.
        }

    # Método auxiliar privado para criar uma mensagem de resultado de erro.
    def _create_error_result(self, tool_call_id: str, error_message: str) -> Dict[str, Any]:
        # Mesmo em caso de erro, precisamos retornar uma mensagem de ferramenta válida
        # para que o modelo saiba que a chamada falhou e por quê.
        return {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "name": "error_handler", # Um nome genérico para erros.
            "content": f"Error: {error_message}",
        }
