# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
import logging
from openai import AsyncOpenAI, APIConnectionError
from app.core.llm.base import LLMProvider, AssistantResponse
from typing import List
import httpx


class OllamaProvider(LLMProvider):
    """
    Representa um provedor de LLM (Large Language Model) utilizando a API Ollama.

    :ivar client: Instância do cliente assíncrono para comunicação com a API Ollama.
    :type client: AsyncOpenAI
    :ivar model: Nome do modelo padrão utilizado pelo provedor.
    :type model: str
    """

    def __init__(self, base_url: str = "http://localhost:11434/v1", model: str = "llama3.1"):
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="ollama",
        )
        self.model = model

    @property
    def name(self) -> str:
        return "Ollama"

    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        return await self._create_chat_completion(messages=messages, tools=tools)

    async def list_models(self) -> List[str]:
        try:
            models_response = await self.client.models.list()
            if models_response and hasattr(models_response, 'data'):
                return sorted([model.id for model in models_response.data])
            return []
        except (httpx.ConnectError, APIConnectionError):
            logging.warning(f"Não foi possível conectar ao servidor Ollama em {self.client.base_url} para listar modelos.")
            return []
        except Exception as e:
            logging.warning(f"Erro ao listar modelos Ollama: {e}")
            return []

    async def close(self):
        await self.client.close()
