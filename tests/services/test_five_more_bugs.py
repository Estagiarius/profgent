import pytest
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError
from app.services.data_service import DataService
from app.models.class_ import Class

def test_calculation_method_fixed(data_service, db_session):
    """Bug 1 Fix: 'arithmetic' calculation method is now respected."""
    course = data_service.add_course("Math", "M1")
    # Create class with arithmetic method
    class_ = data_service.create_class("Math Class", course['id'], calculation_method='arithmetic')

    # Add assessments: One with weight 9, one with weight 1
    a1 = data_service.add_assessment(class_['id'], "A1", 9.0)
    a2 = data_service.add_assessment(class_['id'], "A2", 1.0)
    assessments = [a1, a2]

    student = data_service.add_student("S", "1")
    data_service.add_student_to_class(student['id'], class_['id'], 1)

    # Add grades: 0 on the heavy one, 10 on the light one.
    data_service.add_grade(student['id'], a1['id'], 0.0)
    data_service.add_grade(student['id'], a2['id'], 10.0)

    grades = data_service.get_grades_for_class(class_['id'])

    # Fetch class data to get calculation method (simulate UI behavior)
    class_data = data_service.get_class_by_id(class_['id'])
    method = class_data['calculation_method']
    assert method == 'arithmetic'

    # Calculate
    avg = data_service.calculate_average(student['id'], grades, assessments, method)

    # Verify arithmetic average: (0 + 10) / 2 = 5.0
    assert avg == 5.0

def test_update_class_duplicate_name_fixed(data_service, db_session):
    """Bug 2 Fix: update_class raises ValueError for duplicate names."""
    course = data_service.add_course("C", "C1")
    c1 = data_service.create_class("Class A", course['id'])
    c2 = data_service.create_class("Class B", course['id'])

    # Action: Rename B to A
    with pytest.raises(ValueError, match="Uma turma com o nome .* já existe"):
        data_service.update_class(c2['id'], "Class A")

def test_create_incident_unenrolled_fixed(data_service, db_session):
    """Bug 3 Fix: create_incident validates enrollment."""
    course = data_service.add_course("C", "C1")
    class_ = data_service.create_class("Class", course['id'])
    student = data_service.add_student("Unenrolled", "Student")

    # Action
    with pytest.raises(ValueError, match="Aluno não está matriculado"):
        data_service.create_incident(class_['id'], student['id'], "Bad Incident", date.today())

def test_add_grade_unenrolled_fixed(data_service, db_session):
    """Bug 4 Fix: add_grade validates enrollment."""
    course = data_service.add_course("C", "C1")
    class_ = data_service.create_class("Class", course['id'])
    assessment = data_service.add_assessment(class_['id'], "Test", 1.0)
    student = data_service.add_student("Unenrolled", "Student")

    # Action
    with pytest.raises(ValueError, match="Aluno não está matriculado"):
        data_service.add_grade(student['id'], assessment['id'], 10.0)

def test_future_birth_date_fixed(data_service, db_session):
    """Bug 5 Fix: add_student prevents future birth date."""
    future_date = date.today() + timedelta(days=365)

    # Action
    with pytest.raises(ValueError, match="Data de nascimento não pode ser no futuro"):
        data_service.add_student("Future", "Boy", birth_date=future_date)
