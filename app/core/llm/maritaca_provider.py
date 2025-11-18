# Importa a classe AsyncOpenAI, que permite fazer chamadas assíncronas
# para APIs compatíveis com o padrão da OpenAI.
from openai import AsyncOpenAI
# Importa a classe base LLMProvider e a estrutura de resposta AssistantResponse.
from app.core.llm.base import LLMProvider, AssistantResponse
# Importa o tipo List para anotações de tipo.
from typing import List

# Define a classe do provedor Maritaca, que herda da classe base LLMProvider.
class MaritacaProvider(LLMProvider):
    """
    An implementation of the LLMProvider for Maritaca's API,
    leveraging the async OpenAI compatibility layer.
    """

    # O método construtor.
    def __init__(self, api_key: str, model: str = "sabia-3"):
        # Cria uma instância do cliente AsyncOpenAI, mas configurado para a URL da Maritaca.
        # Isso funciona porque a API da Maritaca segue o mesmo padrão da API da OpenAI.
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://chat.maritaca.ai/api",
        )
        # Armazena o nome do modelo a ser usado.
        self.model = model

    # Implementação da propriedade 'name' exigida pela classe base.
    @property
    def name(self) -> str:
        return "Maritaca"

    # Implementação do método 'get_chat_response'.
    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        try:
            # Faz a chamada assíncrona para a API de chat.
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # Controla a criatividade da resposta.
                max_tokens=512,   # Limita o tamanho da resposta.
            )

            # Extrai a mensagem da primeira escolha na resposta.
            message = response.choices[0].message
            # Obtém o conteúdo de texto da mensagem.
            content = message.content or ""
            # Obtém as chamadas de ferramenta, se houver (a API da Maritaca pode não suportar isso).
            tool_calls = message.tool_calls

            # Retorna uma instância padronizada de AssistantResponse.
            return AssistantResponse(content=content, tool_calls=tool_calls)

        # Captura qualquer exceção que possa ocorrer durante a chamada da API.
        except Exception as e:
            print(f"An error occurred with the Maritaca API: {e}")
            # Retorna uma resposta de erro padronizada.
            return AssistantResponse(content=f"Error: {e}")

    # Implementação do método 'list_models'.
    async def list_models(self) -> List[str]:
        # O endpoint da Maritaca compatível com OpenAI parece não suportar a listagem de modelos.
        # Por isso, retornamos uma lista manual dos modelos conhecidos.
        return ["sabia-3", "sabia-2-small"]

    # Implementação do método 'close'.
    async def close(self):
        # Fecha a sessão do cliente http assíncrono para liberar recursos de rede.
        await self.client.close()
