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
from app.services.data_service import DataService
from datetime import date

def test_get_grade_grid_data(data_service, db_session):
    # 1. Setup Data
    # Create Class
    class_id = data_service.create_class("Test Class")['id']

    # Create Course and Subject
    course_id = data_service.add_course("Math", "Mathematics")['id']
    data_service.add_subject_to_class(class_id, course_id)
    subjects = data_service.get_subjects_for_class(class_id)
    class_subject_id = subjects[0]['id']

    # Create Students
    s1 = data_service.add_student("Active", "Student", date(2010, 1, 1))['id']
    s2 = data_service.add_student("Inactive", "Student", date(2010, 1, 1))['id']

    # Enroll
    data_service.enroll_students(class_id, [s1, s2])

    # Set s2 to Inactive
    enrollments = data_service.get_enrollments_for_class(class_id)
    enrollment_s2 = next(e for e in enrollments if e['student_id'] == s2)
    data_service.update_enrollment_status(enrollment_s2['id'], "Inactive")

    # Create Assessment
    assessment = data_service.add_assessment(class_subject_id, "Test 1", 10.0, grading_period=1)

    # Add Grades
    data_service.add_grade(s1, assessment['id'], 8.0)
    data_service.add_grade(s2, assessment['id'], 5.0)

    # 2. Test Default (Active Only)
    grid_active = data_service.get_grade_grid_data(class_subject_id, 1)

    student_ids_active = [s['id'] for s in grid_active['students']]
    assert s1 in student_ids_active
    assert s2 not in student_ids_active
    assert len(grid_active['students']) == 1

    # Check Average
    assert grid_active['averages'][s1] == 8.0

    # 3. Test Include Inactive
    grid_all = data_service.get_grade_grid_data(class_subject_id, 1, active_only=False)

    student_ids_all = [s['id'] for s in grid_all['students']]
    assert s1 in student_ids_all
    assert s2 in student_ids_all
    assert len(grid_all['students']) == 2

    # Check Average for Inactive
    assert grid_all['averages'][s2] == 5.0
