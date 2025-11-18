# Importa a classe AsyncOpenAI para interagir com a API compatível.
from openai import AsyncOpenAI
# Importa a classe base e a estrutura de resposta.
from app.core.llm.base import LLMProvider, AssistantResponse
# Importa tipos para anotações.
from typing import List
# Importa a biblioteca httpx para capturar erros de conexão de rede.
import httpx

# Define a classe do provedor Ollama.
class OllamaProvider(LLMProvider):
    """
    An implementation of the LLMProvider for a local Ollama server,
    using an async client.
    """

    # O método construtor.
    def __init__(self, base_url: str = "http://localhost:11434/v1", model: str = "llama3.1"):
        # Cria uma instância do cliente AsyncOpenAI, apontando para a URL do servidor Ollama.
        # A chave de API é uma string fixa ("ollama"), conforme exigido pela biblioteca OpenAI para este caso.
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="ollama",
        )
        # Armazena o nome do modelo a ser usado.
        self.model = model

    # Implementação da propriedade 'name'.
    @property
    def name(self) -> str:
        return "Ollama"

    # Implementação do método para obter uma resposta do chat.
    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        try:
            # Faz a chamada para a API de chat.
            # `tools=tools` e `tool_choice="auto"` informam ao modelo que ele pode usar as ferramentas fornecidas.
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None,
            )

            # Extrai o conteúdo e as chamadas de ferramenta da resposta.
            message = response.choices[0].message
            content = message.content or ""
            tool_calls = message.tool_calls

            # Retorna a resposta no formato padronizado.
            return AssistantResponse(content=content, tool_calls=tool_calls)

        # Captura erros de conexão específicos (ex: o servidor Ollama não está rodando).
        except httpx.ConnectError as e:
            error_message = f"Could not connect to Ollama server at {self.client.base_url}. Is Ollama running?"
            print(error_message)
            return AssistantResponse(content=error_message)
        # Captura outras exceções que possam ocorrer.
        except Exception as e:
            error_message = f"An error occurred with the Ollama API: {e}"
            print(error_message)
            return AssistantResponse(content=error_message)

    # Implementação do método para listar os modelos disponíveis no servidor Ollama.
    async def list_models(self) -> List[str]:
        try:
            # Faz a chamada para o endpoint que lista os modelos.
            models_response = await self.client.models.list()
            # A API do Ollama retorna objetos de modelo; precisamos extrair o atributo 'id' de cada um.
            if models_response and hasattr(models_response, 'data'):
                return sorted([model.id for model in models_response.data])
            return []
        # Captura erros de conexão.
        except httpx.ConnectError:
            print(f"Could not connect to Ollama server at {self.client.base_url} to list models.")
            return []
        # Captura outros erros (ex: a versão do Ollama é antiga e não suporta o endpoint).
        except Exception as e:
            print(f"Error listing Ollama models (this might be normal for older versions): {e}")
            return []

    # Implementação do método 'close'.
    async def close(self):
        # Fecha a sessão do cliente http assíncrono.
        await self.client.close()
