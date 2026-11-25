# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
import pytest
from datetime import date, timedelta
from app.services.data_service import DataService

def test_add_assessment_negative_weight_raises_error(data_service: DataService):
    course = data_service.add_course("C", "1")
    class_ = data_service.create_class("Cls")
    subject = data_service.add_subject_to_class(class_['id'], course['id'])

    with pytest.raises(ValueError, match="O peso da avaliação não pode ser negativo"):
        data_service.add_assessment(subject['id'], "Neg", -5.0)

def test_update_assessment_negative_weight_raises_error(data_service: DataService, db_session):
    course = data_service.add_course("C", "1")
    class_ = data_service.create_class("Cls")
    subject = data_service.add_subject_to_class(class_['id'], course['id'])
    assessment = data_service.add_assessment(subject['id'], "Pos", 5.0)
    db_session.flush()

    with pytest.raises(ValueError, match="O peso da avaliação não pode ser negativo"):
        data_service.update_assessment(assessment['id'], "New Neg", -1.0)

def test_add_grade_score_out_of_range_raises_error(data_service: DataService):
    student = data_service.add_student("S", "1")
    course = data_service.add_course("C", "1")
    class_ = data_service.create_class("Cls")
    subject = data_service.add_subject_to_class(class_['id'], course['id'])
    data_service.add_student_to_class(student['id'], class_['id'], 1)
    assessment = data_service.add_assessment(subject['id'], "A", 1.0)

    # Nota > 10
    with pytest.raises(ValueError, match="A nota deve estar entre 0 e 10"):
        data_service.add_grade(student['id'], assessment['id'], 11.0)

    # Nota < 0
    with pytest.raises(ValueError, match="A nota deve estar entre 0 e 10"):
        data_service.add_grade(student['id'], assessment['id'], -1.0)

def test_upsert_grade_score_out_of_range_raises_error(data_service: DataService):
    student = data_service.add_student("S", "1")
    course = data_service.add_course("C", "1")
    class_ = data_service.create_class("Cls")
    subject = data_service.add_subject_to_class(class_['id'], course['id'])
    data_service.add_student_to_class(student['id'], class_['id'], 1)
    assessment = data_service.add_assessment(subject['id'], "A", 1.0)

    grades = [{"student_id": student['id'], "assessment_id": assessment['id'], "score": 15.0}]

    with pytest.raises(ValueError, match="A nota deve estar entre 0 e 10"):
        data_service.upsert_grades_for_subject(subject['id'], grades)

def test_add_student_future_birth_date_raises_error(data_service: DataService):
    future = date.today() + timedelta(days=365)
    with pytest.raises(ValueError, match="A data de nascimento não pode estar no futuro"):
        data_service.add_student("Baby", "Future", birth_date=future)
