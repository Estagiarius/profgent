from openai import OpenAI
from app.core.llm.base import LLMProvider, AssistantResponse

class OllamaProvider(LLMProvider):
    """
    An implementation of the LLMProvider for a local Ollama server,
    leveraging the OpenAI compatibility endpoint.
    """

    def __init__(self, base_url: str = "http://localhost:11434/v1", model: str = "llama3.1"):
        self.client = OpenAI(
            base_url=base_url,
            api_key="ollama",  # Required by the library, but ignored by Ollama
        )
        self.model = model

    @property
    def name(self) -> str:
        return "Ollama"

    def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        """
        Gets a chat response from the local Ollama model.
        It should support tool calling if the local model is capable.
        """
        try:
            response = self.client.chat.completions.create(
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
            # Handle connection errors gracefully
            error_message = f"Could not connect to Ollama server at {self.client.base_url}. Is Ollama running? Error: {e}"
            print(error_message)
            return AssistantResponse(content=error_message)
