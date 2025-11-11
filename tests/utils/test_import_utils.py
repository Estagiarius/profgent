import pytest
from datetime import date
from unittest.mock import MagicMock
from app.utils.import_utils import import_students_from_csv

@pytest.fixture
def test_csv_file(tmp_path):
    """Creates a temporary CSV file with the new format for testing."""
    filepath = tmp_path / "students.csv"
    content = [
        "Alunos;11/11/2025 13:31",
        "Filtros",
        "Ano Letivo;2025",
        "Nº de chamada;Nome do Aluno;Data de Nascimento;Situação do Aluno",
        "1;ANA JULIA GONÇALVES;09/06/2008;Transferido",
        "2;ANDRÉ HENRIQUE COSTA E SILVA;01/10/2009;Ativo",
        "3;BÁRBARA ESTEVÃO RESENDE CAROZZI;21/12/2009;BAIXA - TRANSFERÊNCIA",
        "4;INVALID ROW", # Malformed row to test error handling
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        f.write("\n".join(content))
    return str(filepath)

def test_import_students_logic_success(test_csv_file, data_service, assistant_service, mocker):
    """
    Tests the core logic of the import utility, ensuring it correctly parses the CSV
    and calls the data_service with the right data.
    """
    # Arrange
    course = data_service.add_course("History", "HIST101")
    class_ = data_service.create_class("Grade 5 History", course.id)

    # Mock the assistant service's name splitter to be predictable
    async def mock_split_name(full_name):
        if "ANA JULIA" in full_name:
            return "ANA JULIA", "GONÇALVES"
        parts = full_name.split()
        return parts[0], " ".join(parts[1:])
    mocker.patch.object(assistant_service, 'split_full_name', new=mock_split_name)

    # Act
    success_count, errors = import_students_from_csv(test_csv_file, class_.id, data_service, assistant_service)

    # Assert
    assert success_count == 3
    assert len(errors) == 1
    assert "Linha 4" in errors[0] # Check that the malformed row was caught

    enrollments = data_service.get_enrollments_for_class(class_.id)
    assert len(enrollments) == 3

    # Check student 1 (Ana Julia)
    ana = next(e for e in enrollments if e.student.first_name == "ANA JULIA")
    assert ana.student.last_name == "GONÇALVES"
    assert ana.student.birth_date == date(2008, 6, 9)
    assert ana.status == "Inactive"
    assert ana.status_detail == "Transferido"

    # Check student 2 (André Henrique)
    andre = next(e for e in enrollments if e.student.first_name == "ANDRÉ")
    assert andre.status == "Active"
    assert andre.status_detail is None

    # Check student 3 (Bárbara)
    barbara = next(e for e in enrollments if e.student.first_name == "BÁRBARA")
    assert barbara.status == "Inactive"
    assert barbara.status_detail == "BAIXA - TRANSFERÊNCIA"
