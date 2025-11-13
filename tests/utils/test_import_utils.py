import pytest
from datetime import date
from unittest.mock import MagicMock, call, AsyncMock
from app.utils.import_utils import import_students_from_csv
from app.services.data_service import DataService

@pytest.fixture
def test_csv_content():
    """Provides a string content of a CSV file for testing."""
    content = [
        "Relatório de Alunos",
        "Nome do Aluno;Data de Nascimento;Situação do Aluno",
        "ANA JULIA GONÇALVES;09/06/2008;Transferido",
        "ANDRÉ HENRIQUE COSTA E SILVA;01/10/2009;Ativo",
    ]
    return "\n".join(content)

@pytest.fixture
def mock_ai_response():
    """Provides a mock JSON response from the AI parser."""
    return [
        {
            "full_name": "ANA JULIA GONÇALVES",
            "first_name": "Ana Julia",
            "last_name": "Gonçalves",
            "birth_date": "09/06/2008",
            "status": "Transferido"
        },
        {
            "full_name": "ANDRÉ HENRIQUE COSTA E SILVA",
            "first_name": "André Henrique",
            "last_name": "Costa e Silva",
            "birth_date": "01/10/2009",
            "status": "Ativo"
        },
        {
            "full_name": "STUDENT WITHOUT DATE",
            "first_name": "Student",
            "last_name": "Without Date",
            "birth_date": None,
            "status": "Ativo"
        }
    ]

@pytest.mark.anyio
async def test_import_with_ai_parser(test_csv_content, mock_ai_response, data_service: DataService, assistant_service, mocker, tmp_path):
    """
    Tests the import utility with the new AI parser flow.
    """
    # Arrange
    # Create a temporary file with the content
    filepath = tmp_path / "students.csv"
    filepath.write_text(test_csv_content, encoding="utf-8")

    class_id_to_import = 1

    # Mock the AI parser to return a predictable JSON structure
    mocker.patch.object(assistant_service, 'parse_student_csv_with_ai', new=AsyncMock(return_value=mock_ai_response))

    # Spy on the final batch database call
    batch_spy = mocker.spy(data_service, "batch_upsert_students_and_enroll")

    # Act
    success_count, errors = await import_students_from_csv(
        str(filepath), class_id_to_import, data_service, assistant_service
    )

    # Assert
    assert success_count == 3
    assert len(errors) == 0

    # Verify the AI parser was called once with the file content
    assistant_service.parse_student_csv_with_ai.assert_called_once_with(test_csv_content)

    # Verify that the batch method was called once
    batch_spy.assert_called_once()

    # Inspect the data passed to the batch method
    _, called_student_data = batch_spy.call_args.args

    assert len(called_student_data) == 3

    # Check the processed data for a specific student
    ana_data = next(d for d in called_student_data if d['full_name'] == "ANA JULIA GONÇALVES")
    assert ana_data['first_name'] == "Ana Julia"
    assert ana_data['birth_date'] == date(2008, 6, 9)
    assert ana_data['status'] == "Inactive"
    assert ana_data['status_detail'] == "Transferido"

    # Check the student with no date
    no_date_student = next(d for d in called_student_data if d['full_name'] == "STUDENT WITHOUT DATE")
    assert no_date_student['birth_date'] is None
    assert no_date_student['status'] == "Active"
