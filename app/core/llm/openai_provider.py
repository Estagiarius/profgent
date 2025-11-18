# Importa a classe AsyncOpenAI para interagir com a API da OpenAI de forma assíncrona.
from openai import AsyncOpenAI
# Importa a classe base e a estrutura de resposta.
from app.core.llm.base import LLMProvider, AssistantResponse
# Importa tipos para anotações.
from typing import List

# Define a classe do provedor OpenAI.
class OpenAIProvider(LLMProvider):
    """
    An implementation of the LLMProvider for OpenAI's API, using an async client.
    """

    # O método construtor.
    def __init__(self, api_key: str, model: str = "gpt-4"):
        # Cria a instância do cliente assíncrono, passando a chave da API.
        # Como estamos usando a API oficial, não é necessário especificar uma `base_url`.
        self.client = AsyncOpenAI(api_key=api_key)
        # Armazena o nome do modelo a ser usado (ex: "gpt-4", "gpt-3.5-turbo").
        self.model = model

    # Implementação da propriedade 'name'.
    @property
    def name(self) -> str:
        return "OpenAI"

    # Implementação do método para obter uma resposta do chat.
    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        try:
            # Faz a chamada para a API de chat completions da OpenAI.
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools, # Passa as definições das ferramentas, se houver.
                tool_choice="auto" if tools else None, # Deixa o modelo decidir se usa uma ferramenta.
            )

            # Extrai a mensagem da resposta.
            message = response.choices[0].message
            # Obtém o conteúdo de texto da mensagem.
            content = message.content or ""
            # Obtém as chamadas de ferramenta solicitadas pelo modelo.
            tool_calls = message.tool_calls

            # Retorna a resposta no formato padronizado da aplicação.
            return AssistantResponse(content=content, tool_calls=tool_calls)

        # Captura qualquer exceção durante a chamada da API.
        except Exception as e:
            print(f"An error occurred with the OpenAI API: {e}")
            return AssistantResponse(content=f"Error: {e}")

    # Implementação do método para listar os modelos disponíveis.
    async def list_models(self) -> List[str]:
        try:
            # Faz a chamada para o endpoint que lista os modelos.
            models = await self.client.models.list()
            # Filtra a lista para incluir apenas modelos que contêm "gpt" no ID,
            # e retorna a lista ordenada.
            return sorted([model.id for model in models if "gpt" in model.id])
        except Exception as e:
            print(f"Error listing OpenAI models: {e}")
            return []

    # Implementação do método 'close'.
    async def close(self):
        # Fecha a sessão do cliente http assíncrono.
        await self.client.close()
