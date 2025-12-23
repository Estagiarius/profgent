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
from openai import AsyncOpenAI
from app.core.llm.base import LLMProvider, AssistantResponse
from typing import List

class MaritacaProvider(LLMProvider):
    """
    An implementation of the LLMProvider for Maritaca's API,
    leveraging the async OpenAI compatibility layer.
    """

    def __init__(self, api_key: str, model: str = "sabia-3"):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://chat.maritaca.ai/api",
        )
        self.model = model

    @property
    def name(self) -> str:
        return "Maritaca"

    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=512,
            )

            message = response.choices[0].message
            content = message.content or ""

            # Convert tool_calls objects (Pydantic models) to dictionaries
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

        except Exception as e:
            print(f"An error occurred with the Maritaca API: {e}")
            return AssistantResponse(content=f"Error: {e}")

    async def list_models(self) -> List[str]:
        try:
            models = await self.client.models.list()
            # Cast model to Any to avoid linter errors about dynamic attributes
            return sorted([model.id for model in models])  # type: ignore
        except Exception as e:
            print(f"Error listing Maritaca models: {e}")
            return []
        # Antigo retorno, com a chamada forçada. return ["sabia-3", "sabia-2-small"]

    async def close(self):
        await self.client.close()
