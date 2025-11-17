from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import joinedload, Session
from app.data.database import get_db_session
from app.models.student import Student
from app.models.course import Course
from app.models.grade import Grade
from app.models.class_ import Class
from app.models.class_enrollment import ClassEnrollment
from app.models.assessment import Assessment
from app.models.lesson import Lesson
from app.models.incident import Incident
from app.utils.student_csv_parser import parse_student_csv
from datetime import datetime
from contextlib import contextmanager

class DataService:
    def __init__(self, db_session: Session = None):
        self._db_session = db_session

    @contextmanager
    def _get_db(self):
        if self._db_session:
            yield self._db_session
        else:
            with get_db_session() as db:
                yield db

    def import_students_from_csv(self, class_id: int, file_content: str) -> dict:
        errors = []
        imported_count = 0
        try:
            parsed_data = parse_student_csv(file_content)
            if not parsed_data:
                errors.append("O arquivo CSV não contém dados de alunos válidos.")
                return {"imported_count": 0, "errors": errors}
            student_data_for_db = []
            for student_row in parsed_data:
                birth_date_obj = None
                if student_row.get("birth_date"):
                    try:
                        birth_date_obj = datetime.strptime(student_row["birth_date"], "%d/%m/%Y").date()
                    except ValueError:
                        errors.append(f"Formato de data inválido para {student_row['full_name']}: {student_row['birth_date']}. O aluno será importado sem data de nascimento.")
                student_data_for_db.append({
                    "full_name": student_row["full_name"], "first_name": student_row["first_name"],
                    "last_name": student_row["last_name"], "birth_date": birth_date_obj,
                    "status": student_row["status"], "status_detail": student_row.get("status_detail", "")
                })
            with self._get_db() as db:
                self._batch_upsert_students_and_enroll(db, class_id, student_data_for_db)
            imported_count = len({d['full_name'].lower() for d in student_data_for_db})
        except ValueError as ve:
            errors.append(str(ve))
        except Exception as e:
            errors.append(f"Ocorreu um erro inesperado durante a importação: {e}")
        return {"imported_count": imported_count, "errors": errors}

    def add_student(self, first_name: str, last_name: str, birth_date: date | None = None) -> dict | None:
        if not first_name or not last_name: return None
        with self._get_db() as db:
            existing = db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == f"{first_name} {last_name}".lower()).first()
            if existing:
                return {
                    "id": existing.id, "first_name": existing.first_name,
                    "last_name": existing.last_name, "birth_date": existing.birth_date.isoformat() if existing.birth_date else None
                }
            today = date.today()
            new_student = Student(first_name=first_name, last_name=last_name, enrollment_date=today, birth_date=birth_date)
            db.add(new_student)
            db.flush()
            db.refresh(new_student)
            return {
                "id": new_student.id, "first_name": new_student.first_name,
                "last_name": new_student.last_name, "birth_date": new_student.birth_date.isoformat() if new_student.birth_date else None
            }

    def get_all_students(self) -> list[dict]:
        with self._get_db() as db:
            students = db.query(Student).order_by(Student.first_name).all()
            return [{"id": s.id, "first_name": s.first_name, "last_name": s.last_name, "birth_date": s.birth_date.isoformat() if s.birth_date else None} for s in students]

    def get_student_count(self) -> int:
        with self._get_db() as db:
            return db.query(func.count(Student.id)).scalar()

    def get_student_by_name(self, name: str) -> dict | None:
        with self._get_db() as db:
            student = db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == name.lower()).first()
            if student:
                return {
                    "id": student.id, "first_name": student.first_name,
                    "last_name": student.last_name, "birth_date": student.birth_date.isoformat() if student.birth_date else None
                }
            return None

    def update_student(self, student_id: int, first_name: str, last_name: str):
        with self._get_db() as db:
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                student.first_name = first_name
                student.last_name = last_name

    def delete_student(self, student_id: int):
        with self._get_db() as db:
            db.query(Grade).filter(Grade.student_id == student_id).delete()
            db.query(ClassEnrollment).filter(ClassEnrollment.student_id == student_id).delete()
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                db.delete(student)

    def get_students_with_active_enrollment(self) -> list[dict]:
        with self._get_db() as db:
            active_students = db.query(Student).join(ClassEnrollment).filter(ClassEnrollment.status == 'Active').all()
            return [{"id": s.id, "first_name": s.first_name, "last_name": s.last_name} for s in active_students]

    def get_unenrolled_students(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            enrolled_student_ids = db.query(ClassEnrollment.student_id).filter(ClassEnrollment.class_id == class_id)
            students = db.query(Student).filter(Student.id.notin_(enrolled_student_ids)).all()
            return [{"id": s.id, "first_name": s.first_name, "last_name": s.last_name} for s in students]

    def add_course(self, course_name: str, course_code: str) -> dict | None:
        if not course_name or not course_code: return None
        new_course = Course(course_name=course_name, course_code=course_code)
        with self._get_db() as db:
            db.add(new_course)
            db.flush()
            db.refresh(new_course)
            return {"id": new_course.id, "course_name": new_course.course_name, "course_code": new_course.course_code}

    def get_all_courses(self) -> list[dict]:
        with self._get_db() as db:
            courses = db.query(Course).order_by(Course.course_name).all()
            return [{"id": c.id, "course_name": c.course_name, "course_code": c.course_code} for c in courses]

    def get_course_count(self) -> int:
        with self._get_db() as db:
            return db.query(func.count(Course.id)).scalar()

    def get_course_by_name(self, name: str) -> dict | None:
        with self._get_db() as db:
            course = db.query(Course).options(joinedload(Course.classes)).filter(func.lower(Course.course_name) == name.lower()).first()
            if course:
                course_data = {"id": course.id, "course_name": course.course_name, "course_code": course.course_code}
                course_data["classes"] = [{"id": c.id, "name": c.name} for c in course.classes]
                return course_data
            return None

    def get_course_by_id(self, course_id: int) -> dict | None:
        with self._get_db() as db:
            course = db.query(Course).options(joinedload(Course.classes)).filter(Course.id == course_id).first()
            if course:
                course_data = {"id": course.id, "course_name": course.course_name, "course_code": course.course_code}
                course_data["classes"] = [{"id": c.id, "name": c.name} for c in course.classes]
                return course_data
            return None

    def update_course(self, course_id: int, course_name: str, course_code: str):
        with self._get_db() as db:
            course = db.query(Course).filter(Course.id == course_id).first()
            if course:
                course.course_name = course_name
                course.course_code = course_code

    def delete_course(self, course_id: int):
        with self._get_db() as db:
            course = db.query(Course).filter(Course.id == course_id).first()
            if course and not course.classes:
                db.delete(course)

    def create_class(self, name: str, course_id: int, calculation_method: str = 'arithmetic') -> dict | None:
        if not name or not course_id: return None
        new_class = Class(name=name, course_id=course_id, calculation_method=calculation_method)
        with self._get_db() as db:
            db.add(new_class)
            db.flush()
            db.refresh(new_class)
            return {"id": new_class.id, "name": new_class.name}

    def get_all_classes(self) -> list[dict]:
        with self._get_db() as db:
            classes = db.query(Class).options(joinedload(Class.course), joinedload(Class.enrollments)).order_by(Class.name).all()
            return [{"id": c.id, "name": c.name, "course_name": c.course.course_name, "student_count": len(c.enrollments)} for c in classes]

    def get_class_by_id(self, class_id: int, simplified: bool = False) -> dict | None:
        with self._get_db() as db:
            query = db.query(Class)
            if not simplified:
                query = query.options(joinedload(Class.assessments), joinedload(Class.course))

            class_ = query.filter(Class.id == class_id).first()
            if class_:
                class_data = {"id": class_.id, "name": class_.name}
                if not simplified:
                    class_data["course_name"] = class_.course.course_name
                    class_data["assessments"] = [{"id": a.id, "name": a.name, "weight": a.weight} for a in class_.assessments]
                return class_data
            return None

    def update_class(self, class_id: int, name: str):
        with self._get_db() as db:
            class_ = db.query(Class).filter(Class.id == class_id).first()
            if class_:
                class_.name = name

    def delete_class(self, class_id: int):
        with self._get_db() as db:
            db.query(ClassEnrollment).filter(ClassEnrollment.class_id == class_id).delete()
            class_ = db.query(Class).filter(Class.id == class_id).first()
            if class_:
                db.delete(class_)

    def add_student_to_class(self, student_id: int, class_id: int, call_number: int, status: str = "Active") -> dict | None:
        if not all([student_id, class_id, call_number is not None]): return None
        with self._get_db() as db:
            existing = db.query(ClassEnrollment).filter_by(student_id=student_id, class_id=class_id).first()
            if existing:
                existing.call_number = call_number
                existing.status = status
                db.flush()
                return {"id": existing.id, "student_id": existing.student_id, "class_id": existing.class_id, "status": existing.status}
            enrollment = ClassEnrollment(student_id=student_id, class_id=class_id, call_number=call_number, status=status)
            db.add(enrollment)
            db.flush()
            db.refresh(enrollment)
            return {"id": enrollment.id, "student_id": enrollment.student_id, "class_id": enrollment.class_id, "status": enrollment.status}

    def get_enrollments_for_class(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            enrollments = db.query(ClassEnrollment).options(joinedload(ClassEnrollment.student)).filter(ClassEnrollment.class_id == class_id).order_by(ClassEnrollment.call_number).all()
            return [
                {
                    "id": e.id, "call_number": e.call_number, "status": e.status,
                    "student_id": e.student.id,
                    "student_first_name": e.student.first_name, "student_last_name": e.student.last_name,
                    "student_birth_date": e.student.birth_date.isoformat() if e.student.birth_date else None
                } for e in enrollments
            ]

    def update_enrollment_status(self, enrollment_id: int, status: str):
        with self._get_db() as db:
            enrollment = db.query(ClassEnrollment).filter(ClassEnrollment.id == enrollment_id).first()
            if enrollment:
                enrollment.status = status

    def _get_next_call_number(self, db: Session, class_id: int) -> int:
        max_call_number = db.query(func.max(ClassEnrollment.call_number)).filter(ClassEnrollment.class_id == class_id).scalar()
        return (max_call_number or 0) + 1

    def get_next_call_number(self, class_id: int) -> int:
        with self._get_db() as db:
            return self._get_next_call_number(db, class_id)

    def add_assessment(self, class_id: int, name: str, weight: float) -> dict | None:
        if not all([class_id, name, weight is not None]): return None
        assessment = Assessment(class_id=class_id, name=name, weight=weight)
        with self._get_db() as db:
            db.add(assessment)
            db.flush()
            db.refresh(assessment)
            return {"id": assessment.id, "name": assessment.name, "weight": assessment.weight, "class_id": assessment.class_id}

    def update_assessment(self, assessment_id: int, name: str, weight: float):
        with self._get_db() as db:
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if assessment:
                assessment.name = name
                assessment.weight = weight

    def delete_assessment(self, assessment_id: int):
        with self._get_db() as db:
            db.query(Grade).filter(Grade.assessment_id == assessment_id).delete()
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if assessment:
                db.delete(assessment)

    def get_all_grades(self) -> list[dict]:
        with self._get_db() as db:
            grades = db.query(Grade).all()
            return [{"id": g.id, "student_id": g.student_id, "assessment_id": g.assessment_id, "score": g.score} for g in grades]

    def get_grades_for_class(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            grades = (db.query(Grade).options(joinedload(Grade.assessment))
                      .join(Assessment).join(ClassEnrollment, Grade.student_id == ClassEnrollment.student_id)
                      .filter(Assessment.class_id == class_id)
                      .filter(ClassEnrollment.class_id == class_id)
                      .filter(ClassEnrollment.status == 'Active').all())
            return [
                {"id": g.id, "student_id": g.student_id, "assessment_id": g.assessment_id, "score": g.score, "assessment_name": g.assessment.name}
                for g in grades
            ]

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
                .join(Class, Assessment.class_id == Class.id)
                .join(Course, Class.course_id == Course.id)
                .all()
            )
            return [row._asdict() for row in grades_query]

    def get_student_performance_summary(self, student_id: int, class_id: int) -> dict | None:
        with self._get_db() as db:
            class_info = self.get_class_by_id(class_id)
            if not class_info:
                return None

            grades = self.get_grades_for_class(class_id)
            student_grades = [g for g in grades if g['student_id'] == student_id]

            assessments = class_info.get('assessments', [])

            weighted_average = self.calculate_weighted_average(student_id, student_grades, assessments)

            incidents = self.get_incidents_for_class(class_id)
            student_incidents = [i for i in incidents if i['student_id'] == student_id]

            return {
                "weighted_average": weighted_average,
                "incident_count": len(student_incidents)
            }

    def get_students_at_risk(self, class_id: int, grade_threshold: float = 5.0, incident_threshold: int = 2) -> list[dict]:
        with self._get_db() as db:
            enrollments = self.get_enrollments_for_class(class_id)
            at_risk_students = []
            for enrollment in enrollments:
                student_id = enrollment['student_id']
                summary = self.get_student_performance_summary(student_id, class_id)
                if summary:
                    is_at_risk = (summary['weighted_average'] < grade_threshold) or \
                                 (summary['incident_count'] >= incident_threshold)
                    if is_at_risk:
                        at_risk_students.append({
                            "student_id": student_id,
                            "student_name": f"{enrollment['student_first_name']} {enrollment['student_last_name']}",
                            "average_grade": summary['weighted_average'],
                            "incident_count": summary['incident_count']
                        })
            return at_risk_students

    def create_lesson(self, class_id: int, title: str, content: str, lesson_date: date) -> dict | None:
        if not all([class_id, title, lesson_date]): return None
        new_lesson = Lesson(class_id=class_id, title=title, content=content, date=lesson_date)
        with self._get_db() as db:
            db.add(new_lesson)
            db.flush()
            db.refresh(new_lesson)
            return {"id": new_lesson.id, "title": new_lesson.title, "content": new_lesson.content, "date": new_lesson.date.isoformat()}

    def update_lesson(self, lesson_id: int, title: str, content: str, lesson_date: date):
        with self._get_db() as db:
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                lesson.title = title
                lesson.content = content
                lesson.date = lesson_date

    def delete_lesson(self, lesson_id: int):
        with self._get_db() as db:
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                db.delete(lesson)

    def get_lessons_for_class(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            lessons = db.query(Lesson).filter(Lesson.class_id == class_id).order_by(Lesson.date.desc()).all()
            return [{"id": l.id, "title": l.title, "content": l.content, "date": l.date.isoformat()} for l in lessons]

    def create_incident(self, class_id: int, student_id: int, description: str, incident_date: date) -> dict | None:
        if not all([class_id, student_id, description, incident_date]): return None
        new_incident = Incident(class_id=class_id, student_id=student_id, description=description, date=incident_date)
        with self._get_db() as db:
            db.add(new_incident)
            db.flush()
            db.refresh(new_incident)
            return {"id": new_incident.id}

    def get_incidents_for_class(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            incidents = db.query(Incident).options(joinedload(Incident.student)).filter(Incident.class_id == class_id).order_by(Incident.date.desc()).all()
            return [
                {
                    "id": i.id, "description": i.description, "date": i.date.isoformat(),
                    "student_id": i.student.id, "student_first_name": i.student.first_name, "student_last_name": i.student.last_name
                } for i in incidents
            ]

    def add_grade(self, student_id: int, assessment_id: int, score: float) -> dict | None:
        if not all([student_id, assessment_id, score is not None]): return None
        today = date.today()
        new_grade = Grade(student_id=student_id, assessment_id=assessment_id, score=score, date_recorded=today)
        with self._get_db() as db:
            db.add(new_grade)
            db.flush()
            db.refresh(new_grade)
            return {"id": new_grade.id, "score": new_grade.score}

    def delete_grade(self, grade_id: int):
        with self._get_db() as db:
            grade = db.query(Grade).filter(Grade.id == grade_id).first()
            if grade:
                db.delete(grade)

    def upsert_grades_for_class(self, class_id: int, grades_data: list[dict]):
        with self._get_db() as db:
            existing_grades_query = db.query(Grade).join(Assessment).filter(Assessment.class_id == class_id)
            existing_grades_map = {(g.student_id, g.assessment_id): g for g in existing_grades_query}
            for grade_info in grades_data:
                student_id, assessment_id, score = grade_info['student_id'], grade_info['assessment_id'], grade_info['score']
                existing_grade = existing_grades_map.get((student_id, assessment_id))
                if existing_grade:
                    if existing_grade.score != score:
                        existing_grade.score = score
                else:
                    new_grade = Grade(student_id=student_id, assessment_id=assessment_id, score=score, date_recorded=date.today())
                    db.add(new_grade)

    def calculate_weighted_average(self, student_id: int, grades: list[dict], assessments: list[dict]) -> float:
        total_weight = sum(a['weight'] for a in assessments)
        if total_weight == 0: return 0.0
        student_grades = {g['assessment_id']: g['score'] for g in grades if g.get('student_id') == student_id}
        weighted_sum = sum(student_grades.get(a['id'], 0.0) * a['weight'] for a in assessments)
        return weighted_sum / total_weight

    def _batch_upsert_students_and_enroll(self, db: Session, class_id: int, student_data_list: list[dict]):
        unique_student_data = {data['full_name'].lower(): data for data in student_data_list}
        next_call_number = self._get_next_call_number(db, class_id)

        for full_name_lower, data in unique_student_data.items():
            student = db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == full_name_lower).first()
            if student:
                if data['birth_date'] and student.birth_date != data['birth_date']:
                    student.birth_date = data['birth_date']
            else:
                student = Student(
                    first_name=data['first_name'], last_name=data['last_name'],
                    birth_date=data['birth_date'], enrollment_date=date.today()
                )
                db.add(student)
                db.flush()

            status = data['status']

            enrollment = db.query(ClassEnrollment).filter_by(student_id=student.id, class_id=class_id).first()
            if enrollment:
                if enrollment.status != status:
                    enrollment.status = status
            else:
                new_enrollment = ClassEnrollment(
                    class_id=class_id, student_id=student.id,
                    call_number=next_call_number, status=status
                )
                db.add(new_enrollment)
                next_call_number += 1
