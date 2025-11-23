import pytest
from app.services.data_service import DataService
from app.services.report_service import ReportService
from app.models.student import Student
from app.models.course import Course
from app.models.class_ import Class

def test_upsert_grades_key_error_bug(data_service, db_session):
    """Bug 1: upsert_grades_for_class handles missing keys gracefully."""
    course = data_service.add_course("Test", "T1")
    class_ = data_service.create_class("Class 1", course['id'])

    # Missing 'assessment_id'
    bad_data = [{'student_id': 1, 'score': 10}]

    # Fix: Should NOT raise KeyError anymore, just skip.
    data_service.upsert_grades_for_class(class_['id'], bad_data)

    # Check that nothing crashed.

def test_delete_course_silent_failure_bug(data_service, db_session):
    """Bug 2: delete_course raises ValueError if course has classes."""
    course = data_service.add_course("Course With Class", "CWC")
    data_service.create_class("Class", course['id'])

    # Action: Try to delete
    # Fix: Expect ValueError
    with pytest.raises(ValueError, match="Não é possível excluir um curso que possui turmas associadas"):
        data_service.delete_course(course['id'])

def test_report_service_distortion_bug(data_service, db_session, mocker):
    """Bug 3: ReportService skips students with NO grades."""
    mocker.patch('matplotlib.pyplot.figure')
    mocker.patch('matplotlib.pyplot.hist')
    mocker.patch('matplotlib.pyplot.savefig')
    mocker.patch('matplotlib.pyplot.close')

    rs = ReportService()
    rs.data_service = data_service

    student = data_service.add_student("New", "Student")
    course = data_service.add_course("C", "C1")
    class_ = data_service.create_class("Cl", course['id'])
    data_service.add_assessment(class_['id'], "A1", 1.0)
    data_service.add_student_to_class(student['id'], class_['id'], 1)

    # Student has NO grades.

    # Generate distribution.
    # Fix: Should raise "No data to generate distribution" because the only student was skipped.
    with pytest.raises(ValueError, match="No data to generate distribution"):
        rs.generate_class_grade_distribution(class_['id'])

def test_ghost_student_bug(data_service, db_session):
    """Bug 4: get_student_performance_summary returns None for non-existent student."""
    course = data_service.add_course("C", "C1")
    class_ = data_service.create_class("Cl", course['id'])

    # Random ID
    summary = data_service.get_student_performance_summary(9999, class_['id'])

    # Fix: returns None
    assert summary is None

def test_negative_weight_bug(data_service, db_session):
    """Bug 5: add_assessment rejects negative weight."""
    course = data_service.add_course("C", "C1")
    class_ = data_service.create_class("Cl", course['id'])

    # Action: Add
    # Fix: Raise ValueError
    with pytest.raises(ValueError, match="O peso da avaliação não pode ser negativo"):
        data_service.add_assessment(class_['id'], "Bad Assessment", -5.0)

    # Action: Update
    assessment = data_service.add_assessment(class_['id'], "Good Assessment", 5.0)
    with pytest.raises(ValueError, match="O peso da avaliação não pode ser negativo"):
        data_service.update_assessment(assessment['id'], "Bad Update", -1.0)
