import pytest
import asyncio
from datetime import date
from app.utils.import_utils import import_students_from_csv
from app.services.data_service import DataService

@pytest.fixture
def test_csv_file(tmp_path):
    """Creates a temporary CSV file for testing."""
    filepath = tmp_path / "students.csv"
    content = [
        "Relatório de Alunos",
        "Nome do Aluno;Data de Nascimento;Situação do Aluno",
        "ANA JULIA GONÇALVES;09/06/2008;Transferido",
        "ANDRÉ HENRIQUE COSTA E SILVA;01/10/2009;Ativo",
        "NEW STUDENT TO BE CREATED;01/01/2010;Ativo",
        "ANA JULIA GONÇALVES;09/06/2008;Transferido", # Duplicate name in CSV
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        f.write("\n".join(content))
    return str(filepath)

@pytest.mark.anyio
async def test_import_hybrid_batch_logic(test_csv_file, data_service: DataService, assistant_service, mocker):
    """
    Tests the full import pipeline with the hybrid batching logic,
    ensuring the final database state is correct.
    """
    # Arrange
    # Pre-seed the database with one existing student
    existing_student = data_service.add_student("Ana Julia", "Gonçalves")

    course = data_service.add_course("Science", "SCI101")
    class_to_import = data_service.create_class("Grade 5 Science", course.id)

    # Mock the assistant service to return predictable names
    async def mock_split_name(full_name):
        await asyncio.sleep(0.01)
        if "ANA JULIA" in full_name:
            return "Ana Julia", "Gonçalves"
        if "NEW STUDENT" in full_name:
            return "New Student", "To Be Created"
        parts = full_name.split()
        return parts[0], " ".join(parts[1:])
    mocker.patch.object(assistant_service, 'split_full_name', new=mock_split_name)

    # Act
    success_count, errors = await import_students_from_csv(
        test_csv_file, class_to_import.id, data_service, assistant_service
    )

    # Assert
    assert success_count == 3
    assert len(errors) == 0

    # Verify the database state
    all_students = data_service.get_all_students()
    enrollments = data_service.get_enrollments_for_class(class_to_import.id)

    # Should be 3 students total: 1 pre-existing, 1 from CSV that matched, 1 new from CSV
    # Wait, the logic is based on full name matching. Let's adjust.
    # The pre-existing student's name is "Ana Julia Gonçalves"
    # The CSV has "ANA JULIA GONÇALVES" which should match.
    # Then it has "ANDRÉ HENRIQUE COSTA E SILVA" (new) and "NEW STUDENT..." (new).
    # Total students in DB should be 1 (pre-existing) + 2 (new) = 3
    assert len(all_students) == 3

    # All 3 unique students from the CSV should be enrolled.
    assert len(enrollments) == 3

    # Check enrollment details
    ana_enrollment = next(e for e in enrollments if e.student.first_name == "Ana Julia")
    assert ana_enrollment.status == "Inactive"
    assert ana_enrollment.status_detail == "Transferido"
    assert ana_enrollment.student_id == existing_student.id # Ensure it matched the existing one

    new_student_enrollment = next(e for e in enrollments if e.student.first_name == "New Student")
    assert new_student_enrollment.status == "Active"
