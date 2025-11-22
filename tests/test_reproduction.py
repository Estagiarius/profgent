
import pytest
from unittest.mock import MagicMock
from app.core.tools.tool_executor import ToolExecutor

# Mock the ChatCompletionMessageToolCall object structure
class MockToolCall:
    def __init__(self, id, name, arguments):
        self.id = id
        self.function = MagicMock()
        self.function.name = name
        self.function.arguments = arguments

    # Simulate it NOT being subscriptable
    def __getitem__(self, key):
        raise TypeError("'MockToolCall' object is not subscriptable")

def test_execute_tool_call_with_object_fails():
    registry = MagicMock()
    executor = ToolExecutor(registry)

    # Create a tool call that mimics the OpenAI object
    tool_call_object = MockToolCall(id="call_123", name="test_tool", arguments='{}')

    # Expect failure because ToolExecutor expects a dict
    with pytest.raises(TypeError, match="'MockToolCall' object is not subscriptable"):
        # We need to cast to Any or ignore type hint because we are intentionally passing the wrong type
        executor.execute_tool_call(tool_call_object)

def test_execute_tool_call_with_dict_succeeds():
    registry = MagicMock()
    tool_func = MagicMock(return_value="Success")
    registry.get_tool.return_value = tool_func

    executor = ToolExecutor(registry)

    tool_call_dict = {
        "id": "call_123",
        "function": {
            "name": "test_tool",
            "arguments": '{}'
        },
        "type": "function"
    }

    result = executor.execute_tool_call(tool_call_dict)
    assert result["content"] == "Success"
