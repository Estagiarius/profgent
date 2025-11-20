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
        return await self._create_chat_completion(messages=messages, tools=tools)

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
