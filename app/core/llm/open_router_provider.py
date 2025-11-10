from openai import AsyncOpenAI
from app.core.llm.base import LLMProvider, AssistantResponse
from typing import List

class OpenRouterProvider(LLMProvider):
    """
    An implementation of the LLMProvider for OpenRouter's API,
    using an async client.
    """

    def __init__(self, api_key: str, model: str = "mistralai/mistral-7b-instruct:free"):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self.model = model

    @property
    def name(self) -> str:
        return "OpenRouter"

    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None,
            )

            message = response.choices[0].message
            content = message.content or ""
            tool_calls = message.tool_calls

            return AssistantResponse(content=content, tool_calls=tool_calls)

        except Exception as e:
            print(f"An error occurred with the OpenRouter API: {e}")
            return AssistantResponse(content=f"Error: {e}")

    async def list_models(self) -> List[str]:
        try:
            models = await self.client.models.list()
            return sorted([model.id for model in models])
        except Exception as e:
            print(f"Error listing OpenRouter models: {e}")
            return []

    async def close(self):
        await self.client.close()
