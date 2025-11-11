from app.core.tools.tool_decorator import tool

@tool
def suggest_lesson_activities_tool(topic: str, student_level: str, num_suggestions: int = 3) -> str:
    """
    Generates a list of creative and relevant activity suggestions for a given lesson topic and student level.
    Use this tool when a teacher asks for ideas, activities, projects, or lesson plans on a specific subject.
    For example: "Suggest some activities about the water cycle for 5th graders."
    The tool's output is a direct response from the assistant to the user, not data to be interpreted.
    """
    # This tool is a placeholder for the LLM's own generative capabilities.
    # The real "work" is done by the LLM itself when it decides to call this tool and formulates a response.
    # By providing a clear docstring, we guide the LLM on how to use its own knowledge.
    # The return string is a formatted prompt that the LLM will essentially "answer".
    return f"Please provide {num_suggestions} creative and engaging lesson activities about '{topic}' suitable for {student_level} students. For each activity, include a brief description and the required materials."
