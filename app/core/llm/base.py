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
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any
import logging
import httpx
from openai import APIConnectionError, APIStatusError


@dataclass
class AssistantResponse:
    """
    Representa uma resposta de um assistente, contendo o conteúdo textual
    da resposta gerada, além de possíveis chamadas de ferramentas realizadas
    pelo assistente.

    :ivar content: Conteúdo textual da resposta gerada pelo assistente.
    :type content: str
    :ivar tool_calls: Lista de dicionários representando chamadas de ferramentas ou None.
    :type tool_calls: List[Dict[str, Any]] | None
    """
    content: str
    tool_calls: List[Dict[str, Any]] | None = None


class LLMProvider(ABC):
    """
    Representa uma abstração de um provedor de modelos de linguagem.

    :ivar client: Cliente utilizado para realizar interações com o provedor.
    :type client: Any
    :ivar model: Modelo atualmente selecionado para geração de respostas.
    :type model: str
    """
    client: Any = None
    model: str = ""

    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna o nome do provedor (ex: 'OpenAI')."""
        pass

    async def _create_chat_completion(self, messages: list, tools: list | None = None) -> AssistantResponse:
        """Método auxiliar para criar uma conclusão de chat e tratar exceções comuns."""
        try:
            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = await self.client.chat.completions.create(**kwargs)

            message = response.choices[0].message
            content = message.content or ""

            # Converte objetos tool_calls (modelos Pydantic) para dicionários
            tool_calls = None
            if message.tool_calls:
                tool_calls = []
                for tc in message.tool_calls:
                    if hasattr(tc, 'model_dump'):
                        tool_calls.append(tc.model_dump())
                    elif hasattr(tc, 'dict'):
                        tool_calls.append(tc.dict())
                    else:
                        tool_calls.append(tc)

            return AssistantResponse(content=content, tool_calls=tool_calls)

        except (httpx.ConnectError, APIConnectionError):
            error_message = (
                f"Não foi possível conectar ao servidor {self.name} em "
                f"{getattr(self.client, 'base_url', 'URL desconhecida')}. "
                f"Verifique se o serviço está ativo e sua conexão com a internet."
            )
            logging.error(error_message)
            return AssistantResponse(content=error_message)
        except APIStatusError as e:
            error_message = f"Erro de API no provedor {self.name} (HTTP {e.status_code}): {e.message}"
            logging.error(error_message)
            return AssistantResponse(content=error_message)
        except Exception as e:
            error_message = f"Ocorreu um erro ao comunicar com a API {self.name}: {e}"
            logging.error(error_message)
            return AssistantResponse(content=error_message)

    @abstractmethod
    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        """
        Asynchronously obtains a chat response from the model.
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """
        Asynchronously retrieves a list of available model names from the provider.
        """
        pass

    async def close(self):
        """
        Asynchronously closes any open resources, like network clients.
        """
        pass
