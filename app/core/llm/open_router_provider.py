from openai import OpenAI
from app.core.llm.base import LLMProvider, AssistantResponse

class OpenRouterProvider(LLMProvider):
    """
    An implementation of the LLMProvider for OpenRouter's API,
    which provides access to a wide variety of models through an
    OpenAI-compatible endpoint.
    """

    def __init__(self, api_key: str, model: str = "mistralai/mistral-7b-instruct:free"):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self.model = model

    @property
    def name(self) -> str:
        return "OpenRouter"

    def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        """
        Gets a chat response from the selected OpenRouter model.
        It supports tool calling, similar to OpenAI.
        """
        try:
            # OpenRouter is compatible with OpenAI's tool calling, so we pass the tools.
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
            print(f"An error occurred with the OpenRouter API: {e}")
            return AssistantResponse(content=f"Error: {e}")
