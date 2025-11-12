import pytest
import asyncio
from datetime import date
from unittest.mock import MagicMock, call
from app.utils.import_utils import import_students_from_csv

@pytest.fixture
def test_csv_file(tmp_path):
    """Creates a temporary CSV file for testing."""
    filepath = tmp_path / "students.csv"
    content = [
        "Relatório de Alunos",
        "Nome do Aluno;Data de Nascimento;Situação do Aluno",
        "ANA JULIA GONÇALVES;09/06/2008;Transferido",
        "ANDRÉ HENRIQUE COSTA E SILVA;01/10/2009;Ativo",
        "BÁRBARA ESTEVÃO RESENDE CAROZZI;21/12/2009;BAIXA - TRANSFERÊNCIA",
        "VALID STUDENT WITHOUT DATE;;Ativo",
        ";20/01/2010;Ativo", # Should be ignored
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        f.write("\n".join(content))
    return str(filepath)

@pytest.mark.anyio
async def test_import_with_batching(test_csv_file, data_service, assistant_service, mocker):
    """
    Tests that the import utility correctly prepares data and calls the
    batch upsert method in the data service.
    """
    # Arrange
    class_id_to_import = 1

    # Mock the assistant service to return predictable names
    async def mock_split_name(full_name):
        await asyncio.sleep(0.01)
        if "ANA JULIA" in full_name:
            return "ANA JULIA", "GONÇALVES"
        parts = full_name.split()
        return parts[0], " ".join(parts[1:])
    mocker.patch.object(assistant_service, 'split_full_name', new=mock_split_name)

    # Spy on the batch method to verify it's called correctly
    batch_spy = mocker.spy(data_service, "batch_upsert_students_and_enroll")

    # Act
    success_count, errors = await import_students_from_csv(
        test_csv_file, class_id_to_import, data_service, assistant_service
    )

    # Assert
    assert success_count == 4
    assert len(errors) == 0

    # Verify that the batch method was called exactly once
    batch_spy.assert_called_once()

    # Inspect the arguments passed to the batch method
    call_args, _ = batch_spy.call_args
    called_class_id, called_student_data = call_args

    assert called_class_id == class_id_to_import
    assert len(called_student_data) == 4

    # Check the data for a specific student
    ana_data = next(d for d in called_student_data if d['full_name'] == "ANA JULIA GONÇALVES")
    assert ana_data['first_name'] == "ANA JULIA"
    assert ana_data['last_name'] == "GONÇALVES"
    assert ana_data['birth_date'] == date(2008, 6, 9)
    assert ana_data['status'] == "Inactive"
    assert ana_data['status_detail'] == "Transferido"

    # Check the student with no date
    no_date_student = next(d for d in called_student_data if d['full_name'] == "VALID STUDENT WITHOUT DATE")
    assert no_date_student['birth_date'] is None
    assert no_date_student['status'] == "Active"
