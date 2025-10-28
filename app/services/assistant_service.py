from app.core.llm.base import LLMProvider, AssistantResponse
from app.core.llm.openai_provider import OpenAIProvider
from app.core.security.credentials import get_api_key

class AssistantService:
    def __init__(self):
        self.provider: LLMProvider | None = None
        self.messages: list = []
        self._initialize_provider()

    def _initialize_provider(self):
        # For now, we are hardcoding the OpenAI provider.
        # In the future, this could be based on user settings.
        api_key = get_api_key("OpenAI")
        if api_key:
            self.provider = OpenAIProvider(api_key=api_key)
            # Add a system message to set the context for the assistant
            self.messages.append({"role": "system", "content": "You are a helpful academic assistant."})
        else:
            self.provider = None

    def get_response(self, user_input: str) -> AssistantResponse:
        if not self.provider:
            return AssistantResponse(content="The AI provider is not configured. Please set the API key in Settings.")

        # Add the user's message to the history
        self.messages.append({"role": "user", "content": user_input})

        # Get the response from the LLM provider
        response = self.provider.get_chat_response(self.messages)

        # Add the assistant's response to the history
        if response.content:
            self.messages.append({"role": "assistant", "content": response.content})

        return response
