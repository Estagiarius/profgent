import inspect
import json
from functools import wraps

def tool(func):
    """
    A decorator that inspects a function and generates a JSON schema
    for use with OpenAI's function calling API.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # --- Schema Generation ---
    func_sig = inspect.signature(func)
    docstring = inspect.getdoc(func)

    # Basic function info
    schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }

    # Extract description from docstring (if available)
    if docstring:
        schema["function"]["description"] = docstring.strip().split('\n')[0]

    # Type mapping from Python to JSON Schema
    type_mapping = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
    }

    # Extract parameters
    for name, param in func_sig.parameters.items():
        param_type = "string" # Default to string
        if param.annotation is not inspect.Parameter.empty and param.annotation.__name__ in type_mapping:
            param_type = type_mapping[param.annotation.__name__]

        schema["function"]["parameters"]["properties"][name] = {
            "type": param_type,
            # In a more advanced implementation, you could parse the docstring
            # for parameter descriptions.
            "description": f"The {name} for the function."
        }

        # Check if the parameter has a default value
        if param.default is inspect.Parameter.empty:
            schema["function"]["parameters"]["required"].append(name)

    wrapper.schema = schema
    return wrapper
