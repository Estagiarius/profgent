from openai import AsyncOpenAI
from app.core.llm.base import LLMProvider, AssistantResponse
from typing import List

class OllamaProvider(LLMProvider):
    """
    An implementation of the LLMProvider for a local Ollama server,
    using an async client.
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
            error_message = f"Could not connect to Ollama server at {self.client.base_url}. Is Ollama running? Error: {e}"
            print(error_message)
            return AssistantResponse(content=error_message)

    async def list_models(self) -> List[str]:
        try:
            models = await self.client.models.list()
            # The ollama API returns model names in the 'id' field
            return sorted([model.id for model in models])
        except Exception as e:
            print(f"Error listing Ollama models: {e}")
            return ["Could not connect to Ollama"]
