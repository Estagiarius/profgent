import pytest
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError
from app.services.data_service import DataService

def test_duplicate_course_code_fixed(data_service, db_session):
    """Bug 1 Fix: add_course checks for duplicate code."""
    data_service.add_course("Math", "M101")

    # Action: Add same code
    # Fix: Expect ValueError
    with pytest.raises(ValueError, match="Código do curso .* já existe"):
        data_service.add_course("Advanced Math", "M101")

def test_grade_out_of_range_fixed(data_service, db_session):
    """Bug 2 Fix: add_grade validates range 0-10."""
    student = data_service.add_student("S", "1")
    course = data_service.add_course("C", "C1")
    class_ = data_service.create_class("Cl", course['id'])
    # Enroll
    data_service.add_student_to_class(student['id'], class_['id'], 1)
    assessment = data_service.add_assessment(class_['id'], "A1", 1.0)

    # Action: Grade 11
    # Fix: Expect ValueError
    with pytest.raises(ValueError, match="A nota deve estar entre 0 e 10"):
        data_service.add_grade(student['id'], assessment['id'], 11.0)

def test_future_incident_fixed(data_service, db_session):
    """Bug 3 Fix: create_incident prevents future dates."""
    student = data_service.add_student("S", "1")
    course = data_service.add_course("C", "C1")
    class_ = data_service.create_class("Cl", course['id'])
    data_service.add_student_to_class(student['id'], class_['id'], 1)

    future = date.today() + timedelta(days=1)

    # Action
    # Fix: Expect ValueError
    with pytest.raises(ValueError, match="Data do incidente não pode ser no futuro"):
        data_service.create_incident(class_['id'], student['id'], "Desc", future)

def test_duplicate_assessment_name_fixed(data_service, db_session):
    """Bug 4 Fix: add_assessment prevents duplicate names."""
    course = data_service.add_course("C", "C1")
    class_ = data_service.create_class("Cl", course['id'])

    data_service.add_assessment(class_['id'], "Midterm", 1.0)

    # Action: Add same name
    # Fix: Expect ValueError
    with pytest.raises(ValueError, match="Avaliação com nome .* já existe"):
        data_service.add_assessment(class_['id'], "Midterm", 2.0)

def test_call_number_collision_fixed(data_service, db_session):
    """Bug 5 Fix: add_student_to_class checks call number collision."""
    s1 = data_service.add_student("S", "1")
    s2 = data_service.add_student("S", "2")
    course = data_service.add_course("C", "C1")
    class_ = data_service.create_class("Cl", course['id'])

    # Enroll S1 as #1
    data_service.add_student_to_class(s1['id'], class_['id'], 1)

    # Enroll S2 as #1 (Collision)
    # Fix: Expect ValueError
    with pytest.raises(ValueError, match="Número de chamada .* já está em uso"):
        data_service.add_student_to_class(s2['id'], class_['id'], 1)
