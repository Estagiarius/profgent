from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any

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

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the provider (e.g., 'OpenAI').
        """
        pass

    @abstractmethod
    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        """
        Asynchronously obtains a chat response from the model.

        Args:
            messages: A list representing the conversation history.
            tools: An optional list of tools the model can use.

        Returns:
            An AssistantResponse object containing the model's reply.
        """
        pass
