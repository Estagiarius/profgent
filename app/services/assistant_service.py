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
from app.tools.analysis_tools import get_student_performance_summary_tool, get_students_at_risk_tool
from app.tools.pedagogical_tools import suggest_lesson_activities_tool

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
        # Analysis tools
        self.tool_registry.register(get_student_performance_summary_tool)
        self.tool_registry.register(get_students_at_risk_tool)
        # Pedagogical tools
        self.tool_registry.register(suggest_lesson_activities_tool)
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
            system_prompt = (
                "You are a specialized academic management assistant integrated into a desktop application. "
                "Your primary function is to help users manage student, course, and grade data by using a "
                "predefined set of tools. You must adhere to the following rules strictly:\n"
                "1.  **Use Tools Exclusively**: You MUST use the provided tools to answer questions and perform actions. "
                "Do not offer to perform actions that are not supported by the tools.\n"
                "2.  **No Code Generation**: You MUST NOT generate, write, or suggest any code (e.g., Python, SQL). "
                "Your role is to use the tools, not to be a programmer.\n"
                "3.  **Admit Limitations**: If you cannot perform a request with the available tools, clearly state that you "
                "cannot do it and explain the limitation. Do not invent tools or functionality.\n"
                "4.  **Clarity and Confirmation**: After executing a tool that modifies data (e.g., adding a student), "
                "always confirm the success of the action in a clear and friendly message based on the tool's output."
            )
            self.messages = [{"role": "system", "content": system_prompt}]

    async def get_response(self, user_input: str) -> AssistantResponse:
        self._initialize_provider()
        if not self.provider:
            return AssistantResponse(content="AI provider not configured...")

        self.messages.append({"role": "user", "content": user_input})

        # Step 1: Get the initial response from the model
        tool_schemas = self.tool_registry.get_all_schemas() if self.provider.name in ["OpenAI", "OpenRouter", "Ollama"] else None
        response = await self.provider.get_chat_response(self.messages, tools=tool_schemas)

        # Step 2: Check if the model wants to call a tool
        if not response.tool_calls:
            # No tool calls, we have our final answer.
            if response.content:
                self.messages.append({"role": "assistant", "content": response.content})
            return response

        # Step 3: Execute the tool and get the result
        tool_calls_list = response.tool_calls if isinstance(response.tool_calls, list) else [response.tool_calls]
        self.messages.append({"role": "assistant", "tool_calls": tool_calls_list})

        tool_results = []
        for tool_call in tool_calls_list:
            result = self.tool_executor.execute_tool_call(tool_call)
            tool_results.append(result)

        # Step 4: Append the tool results and get the final natural language response
        self.messages.extend(tool_results)

        final_response = await self.provider.get_chat_response(self.messages, tools=tool_schemas)
        if final_response.content:
            self.messages.append({"role": "assistant", "content": final_response.content})
        return final_response

    async def split_full_name(self, full_name: str) -> tuple[str, str]:
        """
        Splits a full name into first and last names using an AI model.
        Falls back to a simple split if the AI fails.
        """
        # Fallback function
        def simple_split(name):
            parts = name.split()
            return parts[0], " ".join(parts[1:])

        if not self.provider or not full_name:
            return simple_split(full_name)

        try:
            if not self.provider:
                # Attempt to initialize if it hasn't been already
                self._initialize_provider()
                if not self.provider:
                    return simple_split(full_name)

            prompt = (
                "You are a linguistic expert specializing in Brazilian names. "
                "Your task is to separate a full name into a first name and a last name. "
                "The first name may be composite (e.g., 'Ana Julia', 'Maria Clara'). "
                "Respond with only a JSON object with two keys: 'first_name' and 'last_name'.\n\n"
                f"Full name: \"{full_name}\""
            )

            messages = [{"role": "user", "content": prompt}]

            # Use a simpler, direct call that doesn't involve the main chat history
            response = await self.provider.get_chat_response(messages)

            if response.content:
                import json
                try:
                    name_parts = json.loads(response.content)
                    first_name = name_parts.get('first_name')
                    last_name = name_parts.get('last_name')
                    if first_name and last_name:
                        return first_name, last_name
                except (json.JSONDecodeError, KeyError):
                    print(f"AI response for name splitting was not valid JSON: {response.content}")

        except Exception as e:
            print(f"An error occurred during AI name splitting: {e}")

        # If anything fails, use the simple fallback
        return simple_split(full_name)

    async def close(self):
        """Closes the underlying LLM provider's resources."""
        if self.provider:
            await self.provider.close()

    async def parse_student_csv_with_ai(self, csv_content: str) -> list[dict]:
        """
        Uses a single AI call to parse the entire content of a student CSV.
        """
        if not self.provider:
            self._initialize_provider()
            if not self.provider:
                raise RuntimeError("AI provider is not configured.")

        prompt = (
            "You are an expert data extraction assistant. Analyze the following text, which is the content of a student CSV file. "
            "The file may contain header lines that should be ignored. The actual data columns are delimited by semicolons. "
            "For each valid student row, extract the following information:\n"
            "1.  The full name ('Nome do Aluno').\n"
            "2.  The birth date ('Data de Nascimento') in 'DD/MM/AAAA' format.\n"
            "3.  The student's status ('Situação do Aluno').\n\n"
            "From the full name, intelligently separate the first name (which can be composite, like 'Ana Julia') from the last name.\n\n"
            "Return ONLY a single JSON object. This object must be a list of dictionaries. Each dictionary must contain the following keys: "
            "'full_name', 'first_name', 'last_name', 'birth_date', 'status'. "
            "If a birth date is missing or malformed, the 'birth_date' value in the JSON should be null.\n\n"
            "Here is the CSV content:\n\n"
            f'"""{csv_content}"""'
        )

        messages = [{"role": "user", "content": prompt}]

        try:
            response = await self.provider.get_chat_response(messages)

            # --- DIAGNOSTIC LOG ---
            print("--- Raw AI Response for CSV Parsing ---")
            if response and response.content:
                print(response.content)
            else:
                print("Response object or its content is empty.")
            print("------------------------------------")

            if not response or not response.content:
                # Handle cases where the response is empty
                raise RuntimeError("AI provider returned an empty response.")

            # Check if the response content is an error message from the provider
            if response.content.strip().startswith("Error:"):
                raise RuntimeError(f"The AI provider reported an error: {response.content.strip()}")

            import json
            # The AI might wrap the JSON in markdown, so we need to clean it
            cleaned_json_str = response.content.strip().replace("```json", "").replace("```", "").strip()

            if not cleaned_json_str:
                # Handle cases where the cleaned response is empty
                raise RuntimeError("AI provider returned an empty JSON string.")

            return json.loads(cleaned_json_str)
        except json.JSONDecodeError as e:
            # Specifically catch JSON parsing errors
            raise RuntimeError(f"Failed to parse CSV with AI: Invalid JSON format. Error: {e}") from e
        except Exception as e:
            # Propagate other errors to be handled by the caller
            raise RuntimeError(f"An unexpected error occurred while parsing CSV with AI: {e}") from e
