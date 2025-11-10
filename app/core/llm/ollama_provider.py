from openai import AsyncOpenAI
from app.core.llm.base import LLMProvider, AssistantResponse
from typing import List
import httpx

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

        except httpx.ConnectError as e:
            error_message = f"Could not connect to Ollama server at {self.client.base_url}. Is Ollama running?"
            print(error_message)
            return AssistantResponse(content=error_message)
        except Exception as e:
            error_message = f"An error occurred with the Ollama API: {e}"
            print(error_message)
            return AssistantResponse(content=error_message)

    async def list_models(self) -> List[str]:
        try:
            models_response = await self.client.models.list()
            # The ollama API returns model objects, and we need the 'id' attribute
            if models_response and hasattr(models_response, 'data'):
                return sorted([model.id for model in models_response.data])
            return []
        except httpx.ConnectError:
            print(f"Could not connect to Ollama server at {self.client.base_url} to list models.")
            return []
        except Exception as e:
            # This can happen if the API exists but doesn't return a valid model list (e.g., 404)
            print(f"Error listing Ollama models (this might be normal for older versions): {e}")
            return []

    async def close(self):
        await self.client.close()
