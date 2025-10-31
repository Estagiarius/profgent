from app.core.llm.base import LLMProvider, AssistantResponse
from app.core.llm.openai_provider import OpenAIProvider
from app.core.llm.maritaca_provider import MaritacaProvider
from app.core.llm.open_router_provider import OpenRouterProvider
from app.core.llm.ollama_provider import OllamaProvider
from app.core.security.credentials import get_api_key
from app.core.config import load_setting
from app.core.tools.tool_registry import ToolRegistry
from app.core.tools.tool_executor import ToolExecutor

# --- Tool Imports ---
from app.tools.database_tools import get_student_grade, list_courses_for_student, get_class_average
from app.tools.internet_tools import search_internet
from app.tools.database_write_tools import add_new_student, add_new_course, add_new_grade

class AssistantService:
    def __init__(self):
        self.provider: LLMProvider | None = None
        self.messages: list = []

        self.tool_registry = ToolRegistry()
        self._register_tools()
        self.tool_executor = ToolExecutor(self.tool_registry)

        self._initialize_provider()

    def _register_tools(self):
        # Read tools
        self.tool_registry.register(get_student_grade)
        self.tool_registry.register(list_courses_for_student)
        self.tool_registry.register(get_class_average)
        # Internet tools
        self.tool_registry.register(search_internet)
        # Write tools
        self.tool_registry.register(add_new_student)
        self.tool_registry.register(add_new_course)
        self.tool_registry.register(add_new_grade)

    def _initialize_provider(self):
        """Initializes the active LLM provider and model based on saved settings."""
        active_provider_name = load_setting("active_provider", "OpenAI")
        model_config_key = f"{active_provider_name.lower()}_model"

        if active_provider_name == "Ollama":
            ollama_url = load_setting("ollama_url", "http://localhost:11434/v1")
            selected_model = load_setting(model_config_key, "llama3.1")
            self.provider = OllamaProvider(base_url=ollama_url, model=selected_model)
        else:
            api_key = get_api_key(active_provider_name)
            if not api_key:
                self.provider = None; return

            if active_provider_name == "OpenAI":
                selected_model = load_setting(model_config_key, "gpt-4")
                self.provider = OpenAIProvider(api_key=api_key, model=selected_model)
            elif active_provider_name == "Maritaca":
                selected_model = load_setting(model_config_key, "sabia-3")
                self.provider = MaritacaProvider(api_key=api_key, model=selected_model)
            elif active_provider_name == "OpenRouter":
                selected_model = load_setting(model_config_key, "mistralai/mistral-7b-instruct:free")
                self.provider = OpenRouterProvider(api_key=api_key, model=selected_model)
            else:
                self.provider = None

        if self.provider:
            self.messages = [{"role": "system", "content": "You are a helpful academic assistant..."}]

    async def get_response(self, user_input: str) -> AssistantResponse:
        self._initialize_provider()
        if not self.provider:
            return AssistantResponse(content="AI provider not configured...")

        self.messages.append({"role": "user", "content": user_input})

        while True:
            tool_schemas = self.tool_registry.get_all_schemas() if self.provider.name in ["OpenAI", "OpenRouter", "Ollama"] else None

            response = await self.provider.get_chat_response(self.messages, tools=tool_schemas)

            if not response.tool_calls:
                if response.content:
                    self.messages.append({"role": "assistant", "content": response.content})
                return response

            tool_calls_list = response.tool_calls if isinstance(response.tool_calls, list) else [response.tool_calls]
            self.messages.append({"role": "assistant", "tool_calls": tool_calls_list})

            tool_results = []
            for tool_call in tool_calls_list:
                result = self.tool_executor.execute_tool_call(tool_call)
                tool_results.append(result)

            self.messages.extend(tool_results)
