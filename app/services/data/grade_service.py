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
from datetime import date
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from app.models.student import Student
from app.models.course import Course
from app.models.grade import Grade
from app.models.class_ import Class
from app.models.class_subject import ClassSubject
from app.models.class_enrollment import ClassEnrollment
from app.models.assessment import Assessment
from .base_service import BaseDataService

class GradeService(BaseDataService):
    def add_assessment(self, class_subject_id: int, name: str, weight: float, grading_period: int = 1, bncc_codes: str = None) -> dict | None:
        if not all([class_subject_id, name, weight is not None]): return None
        if weight < 0:
            raise ValueError("O peso da avaliação não pode ser negativo.")
        if not (1 <= grading_period <= 5):
             raise ValueError("O período de avaliação deve estar entre 1 e 5.")

        assessment = Assessment(class_subject_id=class_subject_id, name=name, weight=weight, grading_period=grading_period, bncc_codes=bncc_codes)
        with self._get_db() as db:
            db.add(assessment)
            db.flush()
            db.refresh(assessment)
            return {
                "id": assessment.id,
                "name": assessment.name,
                "weight": assessment.weight,
                "class_subject_id": assessment.class_subject_id,
                "grading_period": assessment.grading_period,
                "bncc_codes": assessment.bncc_codes
            }

    def ensure_final_assessment(self, class_subject_id: int) -> dict:
        with self._get_db() as db:
            assessment = db.query(Assessment).filter(
                Assessment.class_subject_id == class_subject_id,
                Assessment.grading_period == 5
            ).first()

            if assessment:
                return {"id": assessment.id, "name": assessment.name}

            new_assessment = Assessment(
                class_subject_id=class_subject_id,
                name="Média Final (Manual)",
                weight=1.0,
                grading_period=5
            )
            db.add(new_assessment)
            db.flush()
            db.refresh(new_assessment)
            return {"id": new_assessment.id, "name": new_assessment.name}

    def update_assessment(self, assessment_id: int, name: str, weight: float, grading_period: int = None, bncc_codes: str = None):
        if weight < 0:
            raise ValueError("O peso da avaliação não pode ser negativo.")
        if grading_period is not None and not (1 <= grading_period <= 5):
             raise ValueError("O período de avaliação deve estar entre 1 e 5.")

        with self._get_db() as db:
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if assessment:
                assessment.name = name
                assessment.weight = weight
                if grading_period is not None:
                    assessment.grading_period = grading_period
                assessment.bncc_codes = bncc_codes

    def delete_assessment(self, assessment_id: int):
        with self._get_db() as db:
            db.query(Grade).filter(Grade.assessment_id == assessment_id).delete()
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if assessment:
                db.delete(assessment)

    def get_assessments_for_subject(self, class_subject_id: int) -> list[dict]:
        with self._get_db() as db:
            assessments = (
                db.query(
                    Assessment.id,
                    Assessment.name,
                    Assessment.weight,
                    Assessment.grading_period,
                    Assessment.bncc_codes,
                )
                .filter(Assessment.class_subject_id == class_subject_id)
                .order_by(Assessment.grading_period, Assessment.name)
                .all()
            )
            return [
                {
                    "id": a.id,
                    "name": a.name,
                    "weight": a.weight,
                    "grading_period": a.grading_period,
                    "bncc_codes": a.bncc_codes,
                }
                for a in assessments
            ]

    def get_all_grades(self) -> list[dict]:
        with self._get_db() as db:
            grades = db.query(Grade).all()
            return [{"id": g.id, "student_id": g.student_id, "assessment_id": g.assessment_id, "score": g.score} for g in grades]

    def get_grades_for_subject(self, class_subject_id: int) -> list[dict]:
        with self._get_db() as db:
            grades = (db.query(Grade.id, Grade.student_id, Grade.assessment_id, Grade.score, Assessment.name.label('assessment_name'))
                      .join(Assessment, Grade.assessment_id == Assessment.id)
                      .join(ClassSubject, Assessment.class_subject_id == ClassSubject.id)
                      .join(ClassEnrollment, (Grade.student_id == ClassEnrollment.student_id) & (ClassSubject.class_id == ClassEnrollment.class_id))
                      .filter(Assessment.class_subject_id == class_subject_id)
                      .filter(ClassEnrollment.status == 'Active').all())
            return [
                {"id": g.id, "student_id": g.student_id, "assessment_id": g.assessment_id, "score": g.score, "assessment_name": g.assessment_name}
                for g in grades
            ]

    @classmethod
    def _compute_period_averages(
        cls,
        student_id: int,
        grades_map: dict[int, float],
        period_assessments: dict[int, list[dict]],
        period_weights: dict[int, float],
        final_assessment_id: int | None,
    ) -> dict:
        """Calcula médias bimestrais (1 a 4), média anual calculada e override final (período 5)."""
        results = {}
        final_sum = 0.0

        for period in range(1, 5):
            assessments_data = period_assessments[period]
            if not assessments_data:
                results[period] = None
                continue

            avg = cls.calculate_weighted_average(
                student_id,
                grades_map,
                assessments_data,
                total_weight=period_weights[period],
            )
            results[period] = avg
            final_sum += avg

        results["final_calculated"] = final_sum / 4.0
        results["final_override"] = (
            grades_map[final_assessment_id]
            if final_assessment_id and final_assessment_id in grades_map
            else None
        )
        return results

    @staticmethod
    def _group_assessments_by_period(assessments) -> tuple[dict[int, list[dict]], dict[int, float], int | None]:
        """Agrupa avaliações por período (1..5), pré-calcula pesos e identifica o override final."""
        period_assessments: dict[int, list[dict]] = {1: [], 2: [], 3: [], 4: [], 5: []}
        for a in assessments:
            period_assessments.setdefault(a.grading_period, []).append({"id": a.id, "weight": a.weight})
        period_weights = {p: sum(a['weight'] for a in period_assessments[p]) for p in range(1, 6)}
        final_assessment_id = period_assessments[5][0]['id'] if period_assessments[5] else None
        return period_assessments, period_weights, final_assessment_id

    def get_student_period_averages(self, student_id: int, class_subject_id: int) -> dict:
        with self._get_db() as db:
            assessments = db.query(Assessment).filter(Assessment.class_subject_id == class_subject_id).all()
            if not assessments:
                return {}

            assessment_ids = [a.id for a in assessments]
            grades = db.query(Grade.assessment_id, Grade.score).filter(
                Grade.student_id == student_id,
                Grade.assessment_id.in_(assessment_ids)
            ).all()

            grades_map = {g.assessment_id: g.score for g in grades}
            period_assessments, period_weights, final_assessment_id = self._group_assessments_by_period(assessments)
            return self._compute_period_averages(
                student_id, grades_map, period_assessments, period_weights, final_assessment_id
            )

    def get_class_period_averages(self, class_subject_id: int) -> dict:
        with self._get_db() as db:
            assessments = db.query(Assessment).filter(Assessment.class_subject_id == class_subject_id).all()
            if not assessments:
                return {}

            assessment_ids = [a.id for a in assessments]
            grades = db.query(Grade.student_id, Grade.assessment_id, Grade.score).filter(
                Grade.assessment_id.in_(assessment_ids)
            ).all()

            student_grades: dict[int, dict[int, float]] = {}
            for g in grades:
                student_grades.setdefault(g.student_id, {})[g.assessment_id] = g.score

            period_assessments, period_weights, final_assessment_id = self._group_assessments_by_period(assessments)
            return {
                student_id: self._compute_period_averages(
                    student_id, s_grades_map, period_assessments, period_weights, final_assessment_id
                )
                for student_id, s_grades_map in student_grades.items()
            }

    def get_grades_for_student_in_course(self, student_id: int, course_id: int) -> list[dict]:
        """Consulta filtrada no banco pelas notas de um aluno em uma disciplina específica."""
        with self._get_db() as db:
            rows = (
                db.query(
                    Grade.id,
                    Grade.score,
                    Assessment.id.label("assessment_id"),
                    Assessment.name.label("assessment_name"),
                    Class.id.label("class_id"),
                    Class.name.label("class_name"),
                    Course.id.label("course_id"),
                    Course.course_name.label("course_name"),
                )
                .join(Assessment, Grade.assessment_id == Assessment.id)
                .join(ClassSubject, Assessment.class_subject_id == ClassSubject.id)
                .join(Class, ClassSubject.class_id == Class.id)
                .join(Course, ClassSubject.course_id == Course.id)
                .filter(Grade.student_id == student_id, Course.id == course_id)
                .all()
            )
            return [row._asdict() for row in rows]

    def get_all_grades_with_details(self) -> list[dict]:
        with self._get_db() as db:
            grades_query = (
                db.query(
                    Grade.id, Grade.score, Student.id.label("student_id"),
                    Student.first_name.label("student_first_name"), Student.last_name.label("student_last_name"),
                    Assessment.id.label("assessment_id"), Assessment.name.label("assessment_name"),
                    Class.id.label("class_id"), Class.name.label("class_name"),
                    Course.id.label("course_id"), Course.course_name.label("course_name")
                )
                .join(Student, Grade.student_id == Student.id)
                .join(Assessment, Grade.assessment_id == Assessment.id)
                .join(ClassSubject, Assessment.class_subject_id == ClassSubject.id)
                .join(Class, ClassSubject.class_id == Class.id)
                .join(Course, ClassSubject.course_id == Course.id)
                .all()
            )
            return [row._asdict() for row in grades_query]

    def add_grade(self, student_id: int, assessment_id: int, score: float) -> dict | None:
        if not all([student_id, assessment_id, score is not None]): return None
        if not (0 <= score <= 10):
            raise ValueError("A nota deve estar entre 0 e 10.")

        today_str = date.today().isoformat()
        with self._get_db() as db:
            existing = db.query(Grade).filter(
                Grade.student_id == student_id,
                Grade.assessment_id == assessment_id
            ).first()
            if existing:
                existing.score = score
                existing.date_recorded = today_str
                db.flush()
                return {"id": existing.id, "score": existing.score}

            new_grade = Grade(student_id=student_id, assessment_id=assessment_id, score=score, date_recorded=today_str)
            db.add(new_grade)
            db.flush()
            db.refresh(new_grade)
            return {"id": new_grade.id, "score": new_grade.score}

    def delete_grade(self, grade_id: int):
        with self._get_db() as db:
            grade = db.query(Grade).filter(Grade.id == grade_id).first()
            if grade:
                db.delete(grade)

    def upsert_grades_for_subject(self, class_subject_id: int, grades_data: list[dict]):
        with self._get_db() as db:
            valid_assessment_ids = {
                row.id for row in db.query(Assessment.id).filter(Assessment.class_subject_id == class_subject_id).all()
            }
            existing_grades_query = (
                db.query(Grade.id, Grade.student_id, Grade.assessment_id, Grade.score)
                .join(Assessment)
                .filter(Assessment.class_subject_id == class_subject_id)
            )
            existing_grades_map = {(g.student_id, g.assessment_id): g for g in existing_grades_query}

            # Deduplica entradas por (student_id, assessment_id), mantendo a última nota informada.
            deduped_grades = {}
            for grade_info in grades_data:
                try:
                    student_id = int(grade_info['student_id'])
                    assessment_id = int(grade_info['assessment_id'])
                except (ValueError, TypeError, KeyError):
                    continue

                score = grade_info['score']
                if not (0 <= score <= 10):
                    raise ValueError("A nota deve estar entre 0 e 10.")

                if assessment_id not in valid_assessment_ids:
                    continue

                deduped_grades[(student_id, assessment_id)] = score

            to_insert = []
            to_update = []
            today_str = date.today().isoformat()

            for (student_id, assessment_id), score in deduped_grades.items():
                existing_grade = existing_grades_map.get((student_id, assessment_id))
                if existing_grade:
                    if existing_grade.score != score:
                        to_update.append({"id": existing_grade.id, "score": score})
                else:
                    to_insert.append({
                        "student_id": student_id,
                        "assessment_id": assessment_id,
                        "score": score,
                        "date_recorded": today_str
                    })

            if to_insert:
                db.bulk_insert_mappings(Grade, to_insert)
            if to_update:
                db.bulk_update_mappings(Grade, to_update)

            db.flush()

    @staticmethod
    def calculate_weighted_average(student_id: int, grades: list[dict] | dict[int, float], assessments: list[dict], total_weight: float = None) -> float:
        if total_weight is None:
            total_weight = sum(a['weight'] for a in assessments)
        if total_weight == 0: return 0.0

        if isinstance(grades, dict):
            student_grades = grades
        else:
            student_grades = {g['assessment_id']: g['score'] for g in grades if g.get('student_id') == student_id}

        weighted_sum = sum(student_grades.get(a['id'], 0.0) * a['weight'] for a in assessments)
        return weighted_sum / total_weight

    @staticmethod
    def calculate_subject_final_average(student_id: int, student_grades: dict[int, float], assessments: list[dict]) -> float:
        """
        Calcula a média final de uma disciplina respeitando a nota manual (grading_period == 5)
        como override e excluindo-a do cálculo ponderado das avaliações regulares (períodos 1 a 4).
        """
        override_assessment = next((a for a in assessments if a.get('grading_period') == 5), None)
        if override_assessment and override_assessment['id'] in student_grades:
            return student_grades[override_assessment['id']]

        regular_assessments = [a for a in assessments if a.get('grading_period', 1) != 5]
        if not regular_assessments:
            return 0.0

        total_weight = sum(a['weight'] for a in regular_assessments)
        return GradeService.calculate_weighted_average(student_id, student_grades, regular_assessments, total_weight=total_weight)
