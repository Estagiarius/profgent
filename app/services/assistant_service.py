from app.core.llm.base import LLMProvider, AssistantResponse
from app.core.llm.openai_provider import OpenAIProvider
from app.core.llm.maritaca_provider import MaritacaProvider
from app.core.security.credentials import get_api_key
from app.core.config import load_setting

class AssistantService:
    def __init__(self):
        self.provider: LLMProvider | None = None
        self.messages: list = []
        self._initialize_provider()

    def _initialize_provider(self):
        active_provider_name = load_setting("active_provider", "OpenAI")
        api_key = get_api_key(active_provider_name)

        if not api_key:
            self.provider = None
            return

        if active_provider_name == "OpenAI":
            self.provider = OpenAIProvider(api_key=api_key)
        elif active_provider_name == "Maritaca":
            self.provider = MaritacaProvider(api_key=api_key)
        else:
            self.provider = None

        if self.provider:
            self.messages = [{"role": "system", "content": "You are a helpful academic assistant."}]

    def get_response(self, user_input: str) -> AssistantResponse:
        # Re-initialize the provider in case the settings have changed
        self._initialize_provider()

        if not self.provider:
            return AssistantResponse(content="The selected AI provider is not configured. Please set the API key in Settings.")

        self.messages.append({"role": "user", "content": user_input})
        response = self.provider.get_chat_response(self.messages)

        if response.content:
            self.messages.append({"role": "assistant", "content": response.content})

        return response
