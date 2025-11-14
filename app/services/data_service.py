from datetime import date
from sqlalchemy import func, select
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
                    "full_name": student_row["full_name"],
                    "first_name": student_row["first_name"],
                    "last_name": student_row["last_name"],
                    "birth_date": birth_date_obj,
                    "status": student_row["status"],
                    "status_detail": student_row.get("status_detail", "")
                })

            self.batch_upsert_students_and_enroll(class_id, student_data_for_db)
            imported_count = len(student_data_for_db)

        except ValueError as ve:
            errors.append(str(ve))
        except Exception as e:
            errors.append(f"Ocorreu um erro inesperado durante a importação: {e}")

        return {"imported_count": imported_count, "errors": errors}

    # --- Student Methods ---
    def add_student(self, first_name: str, last_name: str, birth_date: date | None = None) -> Student | None:
        if not first_name or not last_name: return None
        with self._get_db() as db:
            existing = db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == f"{first_name} {last_name}".lower()).first()
            if existing:
                return existing
            today = date.today().isoformat()
            new_student = Student(first_name=first_name, last_name=last_name, enrollment_date=today, birth_date=birth_date)
            db.add(new_student)
            db.flush()
            db.refresh(new_student)
            return new_student

    def get_all_students(self) -> list[Student]:
        with self._get_db() as db:
            return db.query(Student).order_by(Student.first_name).all()

    def get_student_by_name(self, name: str) -> Student | None:
        with self._get_db() as db:
            return db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == name.lower()).first()

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

    def get_student_count(self) -> int:
        with self._get_db() as db:
            return db.query(Student).count()

    def get_students_with_active_enrollment(self) -> list[Student]:
        with self._get_db() as db:
            return db.query(Student).join(ClassEnrollment).filter(ClassEnrollment.status == 'Active').distinct().all()

    def get_unenrolled_students(self, class_id: int) -> list[Student]:
        with self._get_db() as db:
            enrolled_student_ids = db.query(ClassEnrollment.student_id).filter(ClassEnrollment.class_id == class_id)
            return db.query(Student).filter(Student.id.notin_(enrolled_student_ids)).all()

    # --- Course Methods ---
    def add_course(self, course_name: str, course_code: str) -> Course | None:
        if not course_name or not course_code: return None
        new_course = Course(course_name=course_name, course_code=course_code)
        with self._get_db() as db:
            db.add(new_course)
            db.flush()
            db.refresh(new_course)
            return new_course

    def get_all_courses(self) -> list[Course]:
        with self._get_db() as db:
            return db.query(Course).options(joinedload(Course.classes)).order_by(Course.course_name).all()

    def get_course_by_name(self, name: str) -> Course | None:
        with self._get_db() as db:
            return db.query(Course).options(joinedload(Course.classes)).filter(func.lower(Course.course_name) == name.lower()).first()

    def get_student_by_id(self, student_id: int) -> Student | None:
        with self._get_db() as db:
            return db.query(Student).filter(Student.id == student_id).first()

    def get_grade_by_id(self, grade_id: int) -> Grade | None:
        with self._get_db() as db:
            return db.query(Grade).filter(Grade.id == grade_id).first()

    def get_course_by_id(self, course_id: int) -> Course | None:
        with self._get_db() as db:
            return db.query(Course).options(joinedload(Course.classes)).filter(Course.id == course_id).first()

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

    def get_course_count(self) -> int:
        with self._get_db() as db:
            return db.query(Course).count()

    # --- Class (Turma) Methods ---
    def create_class(self, name: str, course_id: int, calculation_method: str = 'arithmetic') -> Class | None:
        if not name or not course_id: return None
        new_class = Class(name=name, course_id=course_id, calculation_method=calculation_method)
        with self._get_db() as db:
            db.add(new_class)
            db.flush()
            db.refresh(new_class)
            return new_class

    def get_all_classes(self) -> list[Class]:
        with self._get_db() as db:
            return db.query(Class).options(joinedload(Class.course), joinedload(Class.enrollments)).order_by(Class.name).all()

    def get_class_by_id(self, class_id: int) -> Class | None:
        with self._get_db() as db:
            return db.query(Class).options(joinedload(Class.assessments)).filter(Class.id == class_id).first()

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

    def add_student_to_class(self, student_id: int, class_id: int, call_number: int, status: str = "Active") -> ClassEnrollment | None:
        if not all([student_id, class_id, call_number is not None]): return None
        with self._get_db() as db:
            existing = db.query(ClassEnrollment).filter_by(student_id=student_id, class_id=class_id).first()
            if existing:
                existing.call_number = call_number
                existing.status = status
                return existing
            enrollment = ClassEnrollment(student_id=student_id, class_id=class_id, call_number=call_number, status=status)
            db.add(enrollment)
            db.flush()
            db.refresh(enrollment)
            return enrollment

    def get_enrollments_for_class(self, class_id: int) -> list[ClassEnrollment]:
        with self._get_db() as db:
            return db.query(ClassEnrollment).options(joinedload(ClassEnrollment.student)).filter(ClassEnrollment.class_id == class_id).order_by(ClassEnrollment.call_number).all()

    def update_enrollment_status(self, enrollment_id: int, status: str):
        with self._get_db() as db:
            enrollment = db.query(ClassEnrollment).filter(ClassEnrollment.id == enrollment_id).first()
            if enrollment:
                enrollment.status = status

    def get_next_call_number(self, class_id: int) -> int:
        with self._get_db() as db:
            max_call_number = db.query(func.max(ClassEnrollment.call_number)).filter(ClassEnrollment.class_id == class_id).scalar()
            return (max_call_number or 0) + 1

    # --- Assessment Methods ---
    def add_assessment(self, class_id: int, name: str, weight: float) -> Assessment | None:
        if not all([class_id, name, weight is not None]): return None
        assessment = Assessment(class_id=class_id, name=name, weight=weight)
        with self._get_db() as db:
            db.add(assessment)
            db.flush()
            db.refresh(assessment)
            return assessment

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

    # --- Analysis Methods ---
    def get_student_performance_summary(self, student_id: int, class_id: int) -> dict | None:
        with self._get_db() as db:
            enrollment = db.query(ClassEnrollment).options(joinedload(ClassEnrollment.student), joinedload(ClassEnrollment.class_).options(joinedload(Class.assessments), joinedload(Class.course))).filter(ClassEnrollment.student_id == student_id, ClassEnrollment.class_id == class_id).first()
            if not enrollment: return None
            # ... (rest of the method is read-only, no changes needed)
            student = enrollment.student
            class_ = enrollment.class_
            grades = db.query(Grade).join(Assessment).filter(Grade.student_id == student_id, Assessment.class_id == class_id).options(joinedload(Grade.assessment)).all()
            incidents = db.query(Incident).filter(Incident.student_id == student_id, Incident.class_id == class_id).order_by(Incident.date.desc()).all()
            weighted_average = self.calculate_weighted_average(student_id, grades, class_.assessments)
            highest_grade, lowest_grade, formatted_grades = (None, None, [])
            if grades:
                grades.sort(key=lambda g: g.score, reverse=True)
                highest_grade = {"assessment_name": grades[0].assessment.name, "score": grades[0].score}
                lowest_grade = {"assessment_name": grades[-1].assessment.name, "score": grades[-1].score}
                formatted_grades = [{"assessment_name": g.assessment.name, "score": g.score, "weight": g.assessment.weight} for g in grades]
            formatted_incidents = [{"date": i.date.isoformat(), "description": i.description} for i in incidents]
            return {"student_name": f"{student.first_name} {student.last_name}", "class_name": class_.name, "course_name": class_.course.course_name, "weighted_average": round(weighted_average, 2), "grades": formatted_grades, "incident_count": len(incidents), "incidents": formatted_incidents, "highest_grade": highest_grade, "lowest_grade": lowest_grade}

    def get_students_at_risk(self, class_id: int, grade_threshold: float = 5.0, incident_threshold: int = 2) -> list[dict]:
        with self._get_db() as db:
            # ... (read-only method, no changes needed)
            low_grade_student_ids = db.query(Grade.student_id.label("student_id")).join(Assessment).filter(Assessment.class_id == class_id, Grade.score < grade_threshold).distinct()
            high_incident_student_ids = db.query(Incident.student_id.label("student_id")).filter(Incident.class_id == class_id).group_by(Incident.student_id).having(func.count(Incident.id) >= incident_threshold).distinct()
            combined_student_ids = low_grade_student_ids.union(high_incident_student_ids).subquery()
            at_risk_student_ids = select(combined_student_ids.c.student_id)
            at_risk_students = db.query(Student, func.count(func.distinct(Incident.id)).label('incident_count'), func.min(Grade.score).label('lowest_grade_score')).join(ClassEnrollment, Student.id == ClassEnrollment.student_id).outerjoin(Incident, (Student.id == Incident.student_id) & (Incident.class_id == class_id)).outerjoin(Grade, (Student.id == Grade.student_id) & (Grade.assessment.has(Assessment.class_id == class_id))).filter(ClassEnrollment.class_id == class_id, ClassEnrollment.status == 'Active', Student.id.in_(at_risk_student_ids)).group_by(Student.id).all()
            result = []
            for student, incident_count, lowest_grade in at_risk_students:
                reasons = []
                if lowest_grade is not None and lowest_grade < grade_threshold: reasons.append(f"Nota mais baixa: {lowest_grade:.2f}")
                if incident_count is not None and incident_count >= incident_threshold: reasons.append(f"{incident_count} incidentes registrados")
                result.append({"student_id": student.id, "student_name": f"{student.first_name} {student.last_name}", "reasons": reasons})
            return result

    # --- Lesson Methods ---
    def get_lessons_for_class(self, class_id: int) -> list[Lesson]:
        with self._get_db() as db:
            return db.query(Lesson).filter(Lesson.class_id == class_id).order_by(Lesson.date.desc()).all()

    def create_lesson(self, class_id: int, title: str, content: str, lesson_date: date) -> Lesson | None:
        if not all([class_id, title, lesson_date]): return None
        new_lesson = Lesson(class_id=class_id, title=title, content=content, date=lesson_date)
        with self._get_db() as db:
            db.add(new_lesson)
            db.flush()
            db.refresh(new_lesson)
            return new_lesson

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

    # --- Incident Methods ---
    def get_incidents_for_class(self, class_id: int) -> list[Incident]:
        with self._get_db() as db:
            return db.query(Incident).options(joinedload(Incident.student)).filter(Incident.class_id == class_id).order_by(Incident.date.desc()).all()

    def create_incident(self, class_id: int, student_id: int, description: str, incident_date: date) -> Incident | None:
        if not all([class_id, student_id, description, incident_date]): return None
        new_incident = Incident(class_id=class_id, student_id=student_id, description=description, date=incident_date)
        with self._get_db() as db:
            db.add(new_incident)
            db.flush()
            db.refresh(new_incident)
            return new_incident

    # --- Grade Methods ---
    def add_grade(self, student_id: int, assessment_id: int, score: float) -> Grade | None:
        if not all([student_id, assessment_id, score is not None]): return None
        today = date.today().isoformat()
        new_grade = Grade(student_id=student_id, assessment_id=assessment_id, score=score, date_recorded=today)
        with self._get_db() as db:
            db.add(new_grade)
            db.flush()
            db.refresh(new_grade)
            return new_grade

    def get_all_grades(self) -> list[Grade]:
        with self._get_db() as db:
            return db.query(Grade).all()

    def get_all_grades_with_details(self) -> list[Grade]:
        with self._get_db() as db:
            return db.query(Grade).options(joinedload(Grade.student), joinedload(Grade.assessment).joinedload(Assessment.class_).joinedload(Class.course)).all()

    def get_grades_for_class(self, class_id: int) -> list[Grade]:
        with self._get_db() as db:
            return db.query(Grade).join(Assessment).join(ClassEnrollment, (ClassEnrollment.student_id == Grade.student_id) & (ClassEnrollment.class_id == Assessment.class_id)).filter(Assessment.class_id == class_id).filter(ClassEnrollment.status == 'Active').all()

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
                    new_grade = Grade(student_id=student_id, assessment_id=assessment_id, score=score, date_recorded=date.today().isoformat())
                    db.add(new_grade)

    def calculate_weighted_average(self, student_id: int, grades: list[Grade], assessments: list[Assessment]) -> float:
        total_weight = sum(a.weight for a in assessments)
        if total_weight == 0: return 0.0
        student_grades = {g.assessment_id: g.score for g in grades if g.student_id == student_id}
        weighted_sum = sum(student_grades.get(a.id, 0.0) * a.weight for a in assessments)
        return weighted_sum / total_weight

    def batch_upsert_students_and_enroll(self, class_id: int, student_data_list: list[dict]):
        with self._get_db() as db:
            new_students_to_create, all_students_for_enrollment, processed_full_names = [], [], set()
            for data in student_data_list:
                full_name_lower = data['full_name'].lower()
                if full_name_lower in processed_full_names: continue
                student = db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == full_name_lower).first()
                if student:
                    all_students_for_enrollment.append(student)
                else:
                    new_student = Student(first_name=data['first_name'], last_name=data['last_name'], birth_date=data['birth_date'], enrollment_date=date.today().isoformat())
                    new_students_to_create.append(new_student)
                processed_full_names.add(full_name_lower)

            if new_students_to_create:
                db.add_all(new_students_to_create)
                db.flush()
                all_students_for_enrollment.extend(new_students_to_create)

            next_call_number = self.get_next_call_number(class_id)
            enrollments_to_create = []
            student_map = {f"{s.first_name} {s.last_name}".lower(): s for s in all_students_for_enrollment}

            for i, data in enumerate(student_data_list):
                student = student_map.get(data['full_name'].lower())
                if student:
                    enrollments_to_create.append(ClassEnrollment(class_id=class_id, student_id=student.id, call_number=next_call_number + i, status=data['status']))

            if enrollments_to_create:
                db.bulk_save_objects(enrollments_to_create)
