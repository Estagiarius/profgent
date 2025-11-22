from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any
import httpx


@dataclass
class AssistantResponse:
    """
    A standardized data structure for responses from the assistant.
    """
    content: str
    tool_calls: List[Dict[str, Any]] | None = None


class LLMProvider(ABC):
    """
    An abstract base class that defines the contract for all LLM providers.
    """
    client: Any = None
    model: str = ""

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the provider (e.g., 'OpenAI').
        """
        pass

    async def _create_chat_completion(self, messages: list, tools: list | None = None) -> AssistantResponse:
        """
        A helper method to create a chat completion and handle common exceptions.
        """
        # Note: self.client and self.model are expected to be set by subclasses.
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

        except httpx.ConnectError:
            error_message = (
                f"Could not connect to {self.name} server at {getattr(self.client, 'base_url', 'unknown URL')}. "
                f"Is the service running?"
            )
            print(error_message)
            return AssistantResponse(content=error_message)
        except Exception as e:
            error_message = f"An error occurred with the {self.name} API: {e}"
            print(error_message)
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
