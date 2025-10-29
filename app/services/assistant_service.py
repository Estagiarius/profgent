from app.core.llm.base import LLMProvider, AssistantResponse
from app.core.llm.openai_provider import OpenAIProvider
from app.core.llm.maritaca_provider import MaritacaProvider
from app.core.security.credentials import get_api_key
from app.core.config import load_setting
from app.core.tools.tool_registry import ToolRegistry
from app.core.tools.tool_executor import ToolExecutor

# --- Tool Imports ---
from app.tools.database_tools import get_student_grade, list_courses_for_student, get_class_average
from app.tools.internet_tools import search_internet

class AssistantService:
    def __init__(self):
        self.provider: LLMProvider | None = None
        self.messages: list = []

        # --- Tool Setup ---
        self.tool_registry = ToolRegistry()
        self._register_tools()
        self.tool_executor = ToolExecutor(self.tool_registry)

        self._initialize_provider()

    def _register_tools(self):
        """Registers all available tools."""
        self.tool_registry.register(get_student_grade)
        self.tool_registry.register(list_courses_for_student)
        self.tool_registry.register(get_class_average)
        self.tool_registry.register(search_internet)

    def _initialize_provider(self):
        """Initializes the active LLM provider based on saved settings."""
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
            self.messages = [{"role": "system", "content": "You are a helpful academic assistant. You have access to tools to answer questions about students, courses, and grades, as well as to search the internet."}]

    def get_response(self, user_input: str) -> AssistantResponse:
        """
        Manages the agentic loop of getting a response from the LLM,
        executing tools if necessary, and returning a final answer.
        """
        self._initialize_provider()
        if not self.provider:
            return AssistantResponse(content="AI provider not configured. Please set the API key in Settings.")

        self.messages.append({"role": "user", "content": user_input})

        # --- Main Agent Loop ---
        while True:
            # Step 1: Send the conversation history and available tools to the model
            tool_schemas = self.tool_registry.get_all_schemas() if self.provider.name == "OpenAI" else None

            response = self.provider.get_chat_response(self.messages, tools=tool_schemas)

            # Step 2: Check if the model wants to call a tool
            if not response.tool_calls:
                # No tool call, so this is the final answer.
                if response.content:
                    self.messages.append({"role": "assistant", "content": response.content})
                return response

            # Step 3: Execute the tool calls
            self.messages.append({"role": "assistant", "tool_calls": response.tool_calls})

            tool_results = []
            for tool_call in response.tool_calls:
                result = self.tool_executor.execute_tool_call(tool_call)
                tool_results.append(result)

            # Step 4: Send the tool results back to the model
            self.messages.extend(tool_results)

            # The loop continues, and the model will now generate a response
            # based on the tool's output.
