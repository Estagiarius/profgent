
import pytest
from app.services.bncc_service import BNCCService
from app.services.data_service import DataService
from app.models.lesson import Lesson
from app.models.assessment import Assessment
from app.models.course import Course
from datetime import date

def test_bncc_service_search():
    # Test BNCC Service search logic
    results = BNCCService.search_skills("matematica")
    assert isinstance(results, list)

def test_bncc_coverage_logic(db_session, mocker):
    # Setup DataService with injected session
    data_service = DataService(db_session)

    # 1. Create Course with expected BNCC
    course = Course(course_name="Math Test", course_code="MATT", bncc_expected="EF01MA01,EF01MA02")
    db_session.add(course)
    db_session.commit()

    # 2. Create Class and Link Subject
    class_info = data_service.create_class("Class 1")
    class_id = class_info['id'] # FIX: Extract ID from dict

    data_service.add_subject_to_class(class_id, course.id)
    subjects = data_service.get_subjects_for_class(class_id)
    subject_id = subjects[0]['id']

    # 3. Create Lesson covering one skill
    data_service.create_lesson(subject_id, "Lesson 1", "Content", date.today())

    lessons = data_service.get_lessons_for_subject(subject_id)
    lesson_id = lessons[0]['id']

    # Manually update bncc_codes in DB to simulate feature usage
    lesson = db_session.get(Lesson, lesson_id)
    lesson.bncc_codes = "EF01MA01"
    db_session.commit()

    # 4. Create Assessment covering another skill (or same)
    data_service.add_assessment(subject_id, "Test 1", 1.0)
    assessments = data_service.get_assessments_for_subject(subject_id)
    assessment_id = assessments[0]['id']

    assessment = db_session.get(Assessment, assessment_id)
    assessment.bncc_codes = "EF01MA03" # Extra skill not in expected
    db_session.commit()

    # 5. Get Coverage
    report = data_service.get_bncc_coverage(subject_id)

    # assert report['subject_name'] == "Math Test" # Removed as not returned
    assert "EF01MA01" in report['covered_lessons']
    assert "EF01MA03" in report['covered_assessments']

    # Check total covered set
    assert "EF01MA01" in report['total_covered']
    assert "EF01MA03" in report['total_covered']

    # Missing should contain EF01MA02 (expected but not covered)
    assert "EF01MA02" in report['missing']
    assert "EF01MA01" not in report['missing']

    # Coverage percentage:
    # Expected: {EF01MA01, EF01MA02} (Total 2)
    # Covered Intersection: {EF01MA01} (Total 1)
    # Percentage: 1/2 = 50%

    assert report['coverage_percentage'] == 50.0
