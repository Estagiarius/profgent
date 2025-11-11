import json
from app.core.tools.tool_decorator import tool
from app.services.data_service import DataService

data_service = DataService()

@tool
def get_student_performance_summary_tool(student_name: str, class_name: str) -> str:
    """
    Provides a detailed performance summary for a specific student in a specific class.
    Use this tool to answer questions about a student's grades, weighted average, incidents, and overall performance.
    """
    try:
        student = data_service.get_student_by_name(student_name)
        if not student:
            return f"Error: Student '{student_name}' not found."

        # This is a simplification. A real app might need a more robust way to find classes
        all_classes = data_service.get_all_classes()
        target_class = next((c for c in all_classes if c.name.lower() == class_name.lower()), None)

        if not target_class:
            return f"Error: Class '{class_name}' not found."

        summary = data_service.get_student_performance_summary(student.id, target_class.id)

        if not summary:
            return f"Error: Could not retrieve performance summary for {student_name} in {class_name}."

        # Return a JSON string for the LLM to easily parse and understand.
        return json.dumps(summary, indent=2)
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"

@tool
def get_students_at_risk_tool(class_name: str) -> str:
    """
    Identifies and lists students who are at risk in a specific class based on low grades or a high number of incidents.
    Use this tool to answer questions like "Which students need help?" or "Show me students with performance issues."
    """
    try:
        # This is a simplification. A real app might need a more robust way to find classes
        all_classes = data_service.get_all_classes()
        target_class = next((c for c in all_classes if c.name.lower() == class_name.lower()), None)

        if not target_class:
            return f"Error: Class '{class_name}' not found."

        students_at_risk = data_service.get_students_at_risk(target_class.id)

        if not students_at_risk:
            return f"No students were identified as being at risk in {class_name}."

        return json.dumps(students_at_risk, indent=2)
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"
