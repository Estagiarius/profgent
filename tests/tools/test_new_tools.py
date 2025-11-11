import json
import pytest
from unittest.mock import MagicMock
from app.tools.analysis_tools import get_student_performance_summary_tool, get_students_at_risk_tool
from app.tools.pedagogical_tools import suggest_lesson_activities_tool

@pytest.fixture
def mock_data_service():
    """Fixture to create a mock DataService."""
    mock = MagicMock()

    # Mock student data
    mock.get_student_by_name.return_value = MagicMock(id=1, first_name="John", last_name="Doe")

    # Mock class data with a real string for the name attribute
    mock_class = MagicMock()
    mock_class.id = 101
    mock_class.name = "Math Grade 5" # Use a real string here
    mock.get_all_classes.return_value = [mock_class]

    return mock

def test_get_student_performance_summary_tool(mocker, mock_data_service):
    # Patch the data_service instance in the tool's module
    mocker.patch('app.tools.analysis_tools.data_service', mock_data_service)

    # Mock the return value of the specific analysis function
    summary_data = {"student_name": "John Doe", "weighted_average": 85.5, "incident_count": 1}
    mock_data_service.get_student_performance_summary.return_value = summary_data

    # Call the tool
    result_str = get_student_performance_summary_tool("John Doe", "Math Grade 5")
    result_json = json.loads(result_str)

    # Assertions
    mock_data_service.get_student_by_name.assert_called_with("John Doe")
    mock_data_service.get_all_classes.assert_called_once()
    mock_data_service.get_student_performance_summary.assert_called_with(1, 101)
    assert result_json["weighted_average"] == 85.5
    assert result_json["student_name"] == "John Doe"

def test_get_students_at_risk_tool(mocker, mock_data_service):
    # Patch the data_service instance
    mocker.patch('app.tools.analysis_tools.data_service', mock_data_service)

    # Mock the return value
    at_risk_data = [{"student_name": "Jane Doe", "reasons": ["Low grade in Math"]}]
    mock_data_service.get_students_at_risk.return_value = at_risk_data

    # Call the tool
    result_str = get_students_at_risk_tool("Math Grade 5")
    result_json = json.loads(result_str)

    # Assertions
    mock_data_service.get_all_classes.assert_called_once()
    mock_data_service.get_students_at_risk.assert_called_with(101)
    assert len(result_json) == 1
    assert result_json[0]["student_name"] == "Jane Doe"

def test_get_students_at_risk_tool_no_students(mocker, mock_data_service):
    # Patch the data_service instance
    mocker.patch('app.tools.analysis_tools.data_service', mock_data_service)

    # Mock an empty return value
    mock_data_service.get_students_at_risk.return_value = []

    result_str = get_students_at_risk_tool("Math Grade 5")

    assert "No students were identified" in result_str

def test_suggest_lesson_activities_tool():
    # This tool does not depend on external services, so no mocking is needed.
    topic = "the solar system"
    student_level = "4th grade"
    num_suggestions = 2

    result = suggest_lesson_activities_tool(topic, student_level, num_suggestions)

    # Assert that the output is the expected formatted string for the LLM
    assert "2 creative and engaging lesson activities" in result
    assert "'the solar system'" in result
    assert "4th grade students" in result
