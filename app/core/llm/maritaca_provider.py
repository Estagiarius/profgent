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
        # Maritaca's OpenAI-compatible endpoint does not seem to support listing models.
        # We will return the known models manually.
        return ["sabia-3", "sabia-2-small"]

    async def close(self):
        await self.client.close()
