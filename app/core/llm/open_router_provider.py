# Importa a classe AsyncOpenAI para interagir com a API compatível.
from openai import AsyncOpenAI
# Importa a classe base e a estrutura de resposta.
from app.core.llm.base import LLMProvider, AssistantResponse
# Importa tipos para anotações.
from typing import List

# Define a classe do provedor OpenRouter.
class OpenRouterProvider(LLMProvider):
    """
    An implementation of the LLMProvider for OpenRouter's API,
    using an async client.
    """

    # O método construtor.
    def __init__(self, api_key: str, model: str = "mistralai/mistral-7b-instruct:free"):
        # Cria uma instância do cliente AsyncOpenAI, configurada para a URL da API do OpenRouter.
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        # Armazena o nome do modelo a ser usado (ex: "mistralai/mistral-7b-instruct:free").
        self.model = model

    # Implementação da propriedade 'name'.
    @property
    def name(self) -> str:
        return "OpenRouter"

    # Implementação do método para obter uma resposta do chat.
    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        try:
            # Faz a chamada para a API de chat, incluindo as ferramentas se disponíveis.
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

        # Captura qualquer exceção durante a chamada da API.
        except Exception as e:
            print(f"An error occurred with the OpenRouter API: {e}")
            return AssistantResponse(content=f"Error: {e}")

    # Implementação do método para listar os modelos disponíveis.
    async def list_models(self) -> List[str]:
        try:
            # Faz a chamada para o endpoint que lista os modelos.
            models = await self.client.models.list()
            # Extrai o ID de cada modelo e retorna a lista ordenada.
            return sorted([model.id for model in models])
        except Exception as e:
            print(f"Error listing OpenRouter models: {e}")
            return []

    # Implementação do método 'close'.
    async def close(self):
        # Fecha a sessão do cliente http assíncrono.
        await self.client.close()
