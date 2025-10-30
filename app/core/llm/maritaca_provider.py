from openai import AsyncOpenAI
from app.core.llm.base import LLMProvider, AssistantResponse

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
            tool_calls = message.tool_calls

            return AssistantResponse(content=content, tool_calls=tool_calls)

        except Exception as e:
            print(f"An error occurred with the Maritaca API: {e}")
            return AssistantResponse(content=f"Error: {e}")
