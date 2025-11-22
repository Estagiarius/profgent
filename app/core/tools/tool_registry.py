from typing import List, Dict, Any, Callable

class ToolRegistry:
    """
    A central registry for all the tools available to the AI assistant.
    """
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: List[Dict[str, Any]] = []

    def register(self, tool_func: Callable):
        """
        Registers a tool function.

        The function must be decorated with the @tool decorator to have a schema.
        """
        # Cast to Any to avoid linter errors about 'schema' attribute not existing on Callable
        func: Any = tool_func
        if not hasattr(func, 'schema'):
            raise ValueError(f"Function {func.__name__} is not a valid tool. Did you forget the @tool decorator?")

        tool_name = func.schema["function"]["name"]
        self.tools[tool_name] = func
        self.schemas.append(func.schema)
        print(f"Tool registered: {tool_name}")

    def get_tool(self, name: str) -> Callable | None:
        """Retrieves a tool function by its name."""
        return self.tools.get(name)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Returns the JSON schemas for all registered tools."""
        return self.schemas
