from openai import AsyncOpenAI
from app.core.llm.base import LLMProvider, AssistantResponse

class OpenAIProvider(LLMProvider):
    """
    An implementation of the LLMProvider for OpenAI's API, using an async client.
    """

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    @property
    def name(self) -> str:
        return "OpenAI"

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
            print(f"An error occurred with the OpenAI API: {e}")
            return AssistantResponse(content=f"Error: {e}")
