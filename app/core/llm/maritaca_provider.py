from openai import OpenAI
from app.core.llm.base import LLMProvider, AssistantResponse

class MaritacaProvider(LLMProvider):
    """
    An implementation of the LLMProvider for Maritaca's API,
    leveraging the OpenAI compatibility layer.
    """

    def __init__(self, api_key: str, model: str = "sabia-3"):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://chat.maritaca.ai/api",
        )
        self.model = model

    @property
    def name(self) -> str:
        return "Maritaca"

    def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        # NOTE: The Maritaca documentation does not mention tool/function calling support.
        # Therefore, we are not passing the 'tools' parameter to the client.
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=512,
            )

            message = response.choices[0].message
            content = message.content or ""

            # Since we are not expecting tool calls, this will be None.
            tool_calls = message.tool_calls

            return AssistantResponse(content=content, tool_calls=tool_calls)

        except Exception as e:
            print(f"An error occurred with the Maritaca API: {e}")
            return AssistantResponse(content=f"Error: {e}")
