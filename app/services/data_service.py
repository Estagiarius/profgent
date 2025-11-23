# Importa a classe 'date' e 'datetime' para manipulação de datas.
from datetime import date, datetime
# Importa a função 'func' do SQLAlchemy para usar funções SQL como COUNT, MAX, etc.
from sqlalchemy import func
# Importa 'joinedload' para carregamento otimizado de relacionamentos (evita N+1 queries) e 'Session' para type hinting.
from sqlalchemy.orm import joinedload, Session
# Importa o gerenciador de contexto para obter uma sessão de banco de dados.
from app.data.database import get_db_session
# Importa todos os modelos de dados necessários para as operações do serviço.
from app.models.student import Student
from app.models.course import Course
from app.models.grade import Grade
from app.models.class_ import Class
from app.models.class_subject import ClassSubject
from app.models.class_enrollment import ClassEnrollment
from app.models.assessment import Assessment
from app.models.lesson import Lesson
from app.models.incident import Incident
# Importa a função de parsing de CSV de alunos.
from app.utils.student_csv_parser import parse_student_csv
# Importa o gerenciador de contexto para criar blocos 'with'.
from contextlib import contextmanager

# Define a classe DataService, que encapsula toda a lógica de acesso e manipulação de dados.
class DataService:
    """
    Serviço responsável por gerenciar operações relacionadas a estudantes, incluindo
    importação de dados, criação, atualização, exclusão e consultas.

    Esse serviço abstrai a manipulação direta com o banco de dados, permitindo
    que as operações sejam realizadas com sessões de banco de dados injetáveis
    para facilitar testes e integração.

    :ivar _db_session: Sessão injetada do banco de dados, utilizada se provida.
    :type _db_session: Session
    """
    # O construtor permite a injeção de uma sessão de banco de dados, útil para testes.
    def __init__(self, db_session: Session = None):
        # Armazena a sessão de banco de dados injetada, se houver.
        self._db_session = db_session

    # Cria um gerenciador de contexto privado para fornecer uma sessão de banco de dados.
    @contextmanager
    def _get_db(self):
        # Se uma sessão foi injetada no construtor (modo de teste), usa essa sessão.
        if self._db_session:
            yield self._db_session
        # Caso contrário (modo de produção), cria uma nova sessão usando o gerenciador de contexto padrão.
        else:
            with get_db_session() as db:
                yield db

    # Método para importar alunos de um arquivo CSV.
    def import_students_from_csv(self, class_id: int, file_content: str) -> dict:
        # Inicializa listas para armazenar erros e contar o número de alunos importados.
        errors = []
        imported_count = 0
        try:
            # Usa o parser de CSV para extrair os dados dos alunos do conteúdo do arquivo.
            parsed_data = parse_student_csv(file_content)
            # Se não houver dados válidos, retorna um erro.
            if not parsed_data:
                errors.append("O arquivo CSV não contém dados de alunos válidos.")
                return {"imported_count": 0, "errors": errors}
            # Lista para armazenar os dados dos alunos formatados para o banco de dados.
            student_data_for_db = []
            # Itera sobre cada linha de aluno extraída do CSV.
            for student_row in parsed_data:
                birth_date_obj = None
                # Se houver uma data de nascimento, tenta convertê-la para um objeto 'date'.
                if student_row.get("birth_date"):
                    try:
                        birth_date_obj = datetime.strptime(student_row["birth_date"], "%d/%m/%Y").date()
                    except ValueError:
                        # Se o formato da data for inválido, adiciona um erro e continua sem a data.
                        errors.append(f"Formato de data inválido para {student_row['full_name']}: {student_row['birth_date']}. O aluno será importado sem data de nascimento.")
                # Adiciona os dados do aluno formatados à lista.
                student_data_for_db.append({
                    "full_name": student_row["full_name"], "first_name": student_row["first_name"],
                    "last_name": student_row["last_name"], "birth_date": birth_date_obj,
                    "status": student_row["status"], "status_detail": student_row.get("status_detail", "")
                })
            # Abre uma sessão de banco de dados para realizar a operação em lote.
            with self._get_db() as db:
                # Chama o método que insere/atualiza os alunos e suas matrículas de forma otimizada.
                self._batch_upsert_students_and_enroll(db, class_id, student_data_for_db)
            # Conta o número de alunos únicos (pelo nome completo) que foram processados.
            imported_count = len({d['full_name'].lower() for d in student_data_for_db})
        # Captura erros específicos de valor, como os lançados pelo parser.
        except ValueError as ve:
            errors.append(str(ve))
        # Captura quaisquer outros erros inesperados.
        except Exception as e:
            errors.append(f"Ocorreu um erro inesperado durante a importação: {e}")
        # Retorna o resultado da importação.
        return {"imported_count": imported_count, "errors": errors}

    # Método para adicionar um novo aluno.
    def add_student(self, first_name: str, last_name: str, birth_date: date | None = None) -> dict | None:
        # Retorna None se o nome ou sobrenome não forem fornecidos.
        if not first_name or not last_name: return None
        # Abre uma sessão de banco de dados.
        with self._get_db() as db:
            # Verifica se um aluno com o mesmo nome completo (ignorando maiúsculas/minúsculas) já existe.
            existing = db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == f"{first_name} {last_name}".lower()).first()
            # Se existir, retorna os dados do aluno existente.
            if existing:
                return {
                    "id": existing.id, "first_name": existing.first_name,
                    "last_name": existing.last_name, "birth_date": existing.birth_date.isoformat() if existing.birth_date else None
                }
            # Se não existir, cria um novo objeto Student.
            today = date.today()
            new_student = Student(first_name=first_name, last_name=last_name, enrollment_date=today.isoformat(), birth_date=birth_date)
            # Adiciona o novo aluno à sessão.
            db.add(new_student)
            # 'flush' envia a operação para o banco de dados para que o ID seja gerado.
            db.flush()
            # 'refresh' atualiza o objeto 'new_student' com os dados do banco (como o ID).
            db.refresh(new_student)
            # Retorna os dados do novo aluno criado.
            return {
                "id": new_student.id, "first_name": new_student.first_name,
                "last_name": new_student.last_name, "birth_date": new_student.birth_date.isoformat() if new_student.birth_date else None
            }

    # Método para buscar todos os alunos.
    def get_all_students(self) -> list[dict]:
        with self._get_db() as db:
            # Busca todos os alunos, ordenados pelo primeiro nome.
            students = db.query(Student).order_by(Student.first_name).all()
            # Retorna uma lista de dicionários com os dados dos alunos (padrão DTO - Data Transfer Object).
            return [{"id": s.id, "first_name": s.first_name, "last_name": s.last_name, "birth_date": s.birth_date.isoformat() if s.birth_date else None} for s in students]

    # Método para obter a contagem total de alunos.
    def get_student_count(self) -> int:
        with self._get_db() as db:
            # Usa a função `count` do SQLAlchemy e `scalar` para obter um único valor.
            return db.query(func.count(Student.id)).scalar()

    # Método para buscar um aluno pelo nome completo.
    def get_student_by_name(self, name: str) -> dict | None:
        with self._get_db() as db:
            # Filtra pelo nome completo, ignorando maiúsculas/minúsculas.
            student = db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == name.lower()).first()
            # Se encontrar, retorna os dados em formato de dicionário.
            if student:
                return {
                    "id": student.id, "first_name": student.first_name,
                    "last_name": student.last_name, "birth_date": student.birth_date.isoformat() if student.birth_date else None
                }
            return None

    # Método para atualizar os dados de um aluno.
    def update_student(self, student_id: int, first_name: str, last_name: str):
        with self._get_db() as db:
            # Busca o aluno pelo ID.
            student = db.query(Student).filter(Student.id == student_id).first()
            # Se encontrar, atualiza os campos. O 'commit' é feito pelo gerenciador de contexto.
            if student:
                student.first_name = first_name
                student.last_name = last_name

    # Método para deletar um aluno.
    def delete_student(self, student_id: int):
        with self._get_db() as db:
            # Deleta manualmente os registros dependentes (notas, matrículas) para evitar erros de chave estrangeira.
            db.query(Grade).filter(Grade.student_id == student_id).delete()
            db.query(ClassEnrollment).filter(ClassEnrollment.student_id == student_id).delete()
            # Busca o aluno pelo ID.
            student = db.query(Student).filter(Student.id == student_id).first()
            # Se encontrar, deleta o aluno.
            if student:
                db.delete(student)

    # Método para buscar todos os alunos com pelo menos uma matrícula ativa.
    def get_students_with_active_enrollment(self) -> list[dict]:
        with self._get_db() as db:
            # Usa 'join' para conectar Student com ClassEnrollment e filtra pelo status 'Active'.
            active_students = db.query(Student).join(ClassEnrollment).filter(ClassEnrollment.status == 'Active').all()
            return [{"id": s.id, "first_name": s.first_name, "last_name": s.last_name} for s in active_students]

    # Método para buscar alunos que não estão matriculados em uma turma específica.
    def get_unenrolled_students(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            # Cria uma subconsulta para obter os IDs de todos os alunos já matriculados na turma.
            enrolled_student_ids = db.query(ClassEnrollment.student_id).filter(ClassEnrollment.class_id == class_id)
            # Busca todos os alunos cujo ID não está na lista de IDs de matriculados.
            students = db.query(Student).filter(Student.id.notin_(enrolled_student_ids)).all()
            return [{"id": s.id, "first_name": s.first_name, "last_name": s.last_name} for s in students]

    # Método para adicionar um novo curso.
    def add_course(self, course_name: str, course_code: str) -> dict | None:
        if not course_name or not course_code: return None
        new_course = Course(course_name=course_name, course_code=course_code)
        with self._get_db() as db:
            db.add(new_course)
            db.flush()
            db.refresh(new_course)
            return {"id": new_course.id, "course_name": new_course.course_name, "course_code": new_course.course_code}

    # Método para buscar todos os cursos.
    def get_all_courses(self) -> list[dict]:
        with self._get_db() as db:
            courses = db.query(Course).order_by(Course.course_name).all()
            return [{"id": c.id, "course_name": c.course_name, "course_code": c.course_code} for c in courses]

    # Método para obter a contagem total de cursos.
    def get_course_count(self) -> int:
        with self._get_db() as db:
            return db.query(func.count(Course.id)).scalar()

    # Método para buscar um curso pelo nome.
    def get_course_by_name(self, name: str) -> dict | None:
        with self._get_db() as db:
            course = db.query(Course).filter(func.lower(Course.course_name) == name.lower()).first()
            if course:
                return {"id": course.id, "course_name": course.course_name, "course_code": course.course_code}
            return None

    # Método para buscar um curso pelo ID.
    def get_course_by_id(self, course_id: int) -> dict | None:
        with self._get_db() as db:
            # Carrega também as turmas associadas através de class_subjects
            course = db.query(Course).options(
                joinedload(Course.class_subjects).joinedload(ClassSubject.class_)
            ).filter(Course.id == course_id).first()

            if course:
                # Monta a lista de turmas onde este curso é ministrado
                classes_list = []
                for cs in course.class_subjects:
                    if cs.class_:
                        classes_list.append({
                            "id": cs.class_.id,
                            "name": cs.class_.name,
                            "class_subject_id": cs.id
                        })

                return {
                    "id": course.id,
                    "course_name": course.course_name,
                    "course_code": course.course_code,
                    "classes": classes_list
                }
            return None

    # Método para atualizar um curso.
    def update_course(self, course_id: int, course_name: str, course_code: str):
        with self._get_db() as db:
            course = db.query(Course).filter(Course.id == course_id).first()
            if course:
                course.course_name = course_name
                course.course_code = course_code

    # Método para deletar um curso.
    def delete_course(self, course_id: int):
        with self._get_db() as db:
            # Verifica se há associações com turmas (ClassSubject)
            subjects = db.query(ClassSubject).filter(ClassSubject.course_id == course_id).first()
            if not subjects:
                course = db.query(Course).filter(Course.id == course_id).first()
                if course:
                    db.delete(course)

    # Método para criar uma nova turma (Agora sem vincular um curso obrigatório).
    def create_class(self, name: str, calculation_method: str = 'arithmetic') -> dict | None:
        if not name: return None

        with self._get_db() as db:
            # Verifica se já existe uma turma com o mesmo nome (case-insensitive)
            if db.query(Class).filter(func.lower(Class.name) == func.lower(name)).first():
                raise ValueError(f"Uma turma com o nome '{name}' já existe.")

            new_class = Class(name=name, calculation_method=calculation_method)
            db.add(new_class)
            db.flush()
            db.refresh(new_class)
            return {"id": new_class.id, "name": new_class.name}

    # Adiciona uma disciplina a uma turma.
    def add_subject_to_class(self, class_id: int, course_id: int) -> dict | None:
        if not all([class_id, course_id]): return None

        with self._get_db() as db:
            # Verifica se já existe
            existing = db.query(ClassSubject).filter_by(class_id=class_id, course_id=course_id).first()
            if existing:
                return {"id": existing.id, "class_id": existing.class_id, "course_id": existing.course_id}

            new_subject = ClassSubject(class_id=class_id, course_id=course_id)
            db.add(new_subject)
            db.flush()
            db.refresh(new_subject)
            return {"id": new_subject.id, "class_id": new_subject.class_id, "course_id": new_subject.course_id}

    # Busca todas as disciplinas de uma turma.
    def get_subjects_for_class(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            subjects = db.query(ClassSubject).options(joinedload(ClassSubject.course)).filter(ClassSubject.class_id == class_id).all()
            return [{"id": s.id, "course_id": s.course.id, "course_name": s.course.course_name, "course_code": s.course.course_code} for s in subjects]

    # Método para buscar uma turma pelo nome.
    def get_class_by_name(self, name: str) -> dict | None:
        with self._get_db() as db:
            class_ = db.query(Class).filter(func.lower(Class.name) == name.lower()).first()
            if class_:
                return {"id": class_.id, "name": class_.name}
            return None

    # Método para buscar todas as turmas.
    def get_all_classes(self) -> list[dict]:
        with self._get_db() as db:
            # Carrega as matrículas relacionadas para evitar consultas extras.
            classes = db.query(Class).options(joinedload(Class.enrollments)).order_by(Class.name).all()
            # Calcula a contagem de alunos para cada turma.
            return [{"id": c.id, "name": c.name, "student_count": len(c.enrollments)} for c in classes]

    # Método para buscar uma turma pelo ID.
    def get_class_by_id(self, class_id: int) -> dict | None:
        with self._get_db() as db:
            class_ = db.query(Class).filter(Class.id == class_id).first()
            if class_:
                return {"id": class_.id, "name": class_.name}
            return None

    # Método para atualizar uma turma.
    def update_class(self, class_id: int, name: str):
        with self._get_db() as db:
            class_ = db.query(Class).filter(Class.id == class_id).first()
            if class_:
                class_.name = name

    # Método para deletar uma turma.
    def delete_class(self, class_id: int):
        with self._get_db() as db:
            # Deleta as matrículas associadas antes de deletar a turma.
            db.query(ClassEnrollment).filter(ClassEnrollment.class_id == class_id).delete()
            class_ = db.query(Class).filter(Class.id == class_id).first()
            if class_:
                db.delete(class_)

    # Método para adicionar (ou atualizar) um aluno em uma turma.
    def add_student_to_class(self, student_id: int, class_id: int, call_number: int, status: str = "Active") -> dict | None:
        if not all([student_id, class_id, call_number is not None]): return None
        with self._get_db() as db:
            # Verifica se a matrícula já existe.
            existing = db.query(ClassEnrollment).filter_by(student_id=student_id, class_id=class_id).first()
            # Se existir, atualiza o número de chamada e o status.
            if existing:
                existing.call_number = call_number
                existing.status = status
                db.flush()
                return {"id": existing.id, "student_id": existing.student_id, "class_id": existing.class_id, "status": existing.status}
            # Se não existir, cria uma nova matrícula.
            enrollment = ClassEnrollment(student_id=student_id, class_id=class_id, call_number=call_number, status=status)
            db.add(enrollment)
            db.flush()
            db.refresh(enrollment)
            return {"id": enrollment.id, "student_id": enrollment.student_id, "class_id": enrollment.class_id, "status": enrollment.status}

    # Método para buscar todas as matrículas de uma turma.
    def get_enrollments_for_class(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            # Carrega os dados do aluno junto com a matrícula e ordena pelo número de chamada.
            enrollments = db.query(ClassEnrollment).options(joinedload(ClassEnrollment.student)).filter(ClassEnrollment.class_id == class_id).order_by(ClassEnrollment.call_number).all()
            # Retorna uma lista de dicionários com dados combinados da matrícula e do aluno.
            return [
                {
                    "id": e.id, "call_number": e.call_number, "status": e.status,
                    "student_id": e.student.id,
                    "student_first_name": e.student.first_name, "student_last_name": e.student.last_name,
                    "student_birth_date": e.student.birth_date.isoformat() if e.student.birth_date else None
                } for e in enrollments
            ]

    # Método para atualizar o status de uma matrícula (ex: "Active", "Inactive").
    def update_enrollment_status(self, enrollment_id: int, status: str):
        with self._get_db() as db:
            enrollment = db.query(ClassEnrollment).filter(ClassEnrollment.id == enrollment_id).first()
            if enrollment:
                enrollment.status = status

    # Método privado para calcular o próximo número de chamada disponível em uma turma.
    @staticmethod
    def _get_next_call_number(db: Session, class_id: int) -> int:
        # Busca o maior número de chamada existente na turma.
        max_call_number = db.query(func.max(ClassEnrollment.call_number)).filter(ClassEnrollment.class_id == class_id).scalar()
        # Retorna o maior número + 1, ou 1 se a turma estiver vazia.
        return (max_call_number or 0) + 1

    # Método público que expõe a funcionalidade do método privado.
    def get_next_call_number(self, class_id: int) -> int:
        with self._get_db() as db:
            return self._get_next_call_number(db, class_id)

    # Método para adicionar uma nova avaliação a uma disciplina de uma turma.
    def add_assessment(self, class_subject_id: int, name: str, weight: float) -> dict | None:
        if not all([class_subject_id, name, weight is not None]): return None
        assessment = Assessment(class_subject_id=class_subject_id, name=name, weight=weight)
        with self._get_db() as db:
            db.add(assessment)
            db.flush()
            db.refresh(assessment)
            return {"id": assessment.id, "name": assessment.name, "weight": assessment.weight, "class_subject_id": assessment.class_subject_id}

    # Método para atualizar uma avaliação.
    def update_assessment(self, assessment_id: int, name: str, weight: float):
        with self._get_db() as db:
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if assessment:
                assessment.name = name
                assessment.weight = weight

    # Método para deletar uma avaliação.
    def delete_assessment(self, assessment_id: int):
        with self._get_db() as db:
            # Deleta as notas associadas antes de deletar a avaliação.
            db.query(Grade).filter(Grade.assessment_id == assessment_id).delete()
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if assessment:
                db.delete(assessment)

    # Método para buscar avaliações de uma disciplina da turma.
    def get_assessments_for_subject(self, class_subject_id: int) -> list[dict]:
        with self._get_db() as db:
            assessments = db.query(Assessment).filter(Assessment.class_subject_id == class_subject_id).all()
            return [{"id": a.id, "name": a.name, "weight": a.weight} for a in assessments]

    # Método para buscar todas as notas (geralmente para fins administrativos).
    def get_all_grades(self) -> list[dict]:
        with self._get_db() as db:
            grades = db.query(Grade).all()
            return [{"id": g.id, "student_id": g.student_id, "assessment_id": g.assessment_id, "score": g.score} for g in grades]

    # Método para buscar todas as notas de uma disciplina específica da turma.
    def get_grades_for_subject(self, class_subject_id: int) -> list[dict]:
        with self._get_db() as db:
            # Consulta complexa que busca notas apenas de alunos com status 'Active' na turma associada à disciplina.
            # Grade -> Assessment -> ClassSubject -> Class -> Enrollment
            grades = (db.query(Grade).options(joinedload(Grade.assessment))
                      .join(Assessment, Grade.assessment_id == Assessment.id)
                      .join(ClassSubject, Assessment.class_subject_id == ClassSubject.id)
                      .join(ClassEnrollment, (Grade.student_id == ClassEnrollment.student_id) & (ClassSubject.class_id == ClassEnrollment.class_id))
                      .filter(Assessment.class_subject_id == class_subject_id)
                      .filter(ClassEnrollment.status == 'Active').all())
            return [
                {"id": g.id, "student_id": g.student_id, "assessment_id": g.assessment_id, "score": g.score, "assessment_name": g.assessment.name}
                for g in grades
            ]

    # Método para buscar todas as notas com detalhes completos (aluno, avaliação, turma, curso).
    def get_all_grades_with_details(self) -> list[dict]:
        with self._get_db() as db:
            # Query otimizada que junta todas as tabelas relacionadas e seleciona colunas específicas.
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
            # Converte o resultado (que é uma lista de Row objects) em uma lista de dicionários.
            return [row._asdict() for row in grades_query]

    # Método para gerar um resumo de desempenho de um aluno em uma turma (geral ou por disciplina?).
    # Vou manter a assinatura, mas internamente vou considerar todas as disciplinas.
    # No futuro, isso poderia ser filtrado por disciplina.
    def get_student_performance_summary(self, student_id: int, class_id: int) -> dict | None:
        # Como agora temos várias disciplinas, calcular uma média global pode ser complexo (média das médias?).
        # Vou calcular a média de todas as notas existentes, ponderadas pelos seus pesos, ignorando a separação de matérias por enquanto,
        # ou assumindo que o "Resumo" deve ser detalhado.
        # Para manter a compatibilidade, vou calcular uma média simples de todas as avaliações de todas as matérias da turma.

        with self._get_db() as db:
            # Pega todas as disciplinas da turma
            subjects = db.query(ClassSubject).filter(ClassSubject.class_id == class_id).all()
            if not subjects:
                return {"weighted_average": 0.0, "incident_count": 0}

            subject_ids = [s.id for s in subjects]

            # Pega todas as avaliações de todas as disciplinas
            assessments = db.query(Assessment).filter(Assessment.class_subject_id.in_(subject_ids)).all()
            assessment_ids = [a.id for a in assessments]
            assessments_data = [{"id": a.id, "weight": a.weight} for a in assessments]

            if not assessments:
                # Se não há avaliações, retorna 0
                # Incidentes ainda contam
                incidents_count = db.query(func.count(Incident.id)).filter(Incident.class_id == class_id, Incident.student_id == student_id).scalar()
                return {"weighted_average": 0.0, "incident_count": incidents_count}

            # Pega todas as notas do aluno nessas avaliações
            grades = db.query(Grade).filter(Grade.student_id == student_id, Grade.assessment_id.in_(assessment_ids)).all()
            grades_data = [{"assessment_id": g.assessment_id, "score": g.score, "student_id": g.student_id} for g in grades]

            # Calcula a média
            weighted_average = self.calculate_weighted_average(student_id, grades_data, assessments_data)

            # Incidentes
            incidents_count = db.query(func.count(Incident.id)).filter(Incident.class_id == class_id, Incident.student_id == student_id).scalar()

            return {
                "weighted_average": weighted_average,
                "incident_count": incidents_count
            }

    # Método para identificar alunos em situação de risco (notas baixas ou muitos incidentes).
    def get_students_at_risk(self, class_id: int, grade_threshold: float = 5.0, incident_threshold: int = 2) -> list[dict]:
        enrollments = self.get_enrollments_for_class(class_id)
        at_risk_students = []
        # Itera sobre cada aluno matriculado na turma.
        for enrollment in enrollments:
            student_id = enrollment['student_id']
            # Obtém o resumo de desempenho.
            summary = self.get_student_performance_summary(student_id, class_id)
            if summary:
                # Aplica a lógica para determinar se o aluno está em risco.
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

    # Método para criar um novo registro de aula.
    def create_lesson(self, class_subject_id: int, title: str, content: str, lesson_date: date) -> dict | None:
        if not all([class_subject_id, title, lesson_date]): return None
        new_lesson = Lesson(class_subject_id=class_subject_id, title=title, content=content, date=lesson_date)
        with self._get_db() as db:
            db.add(new_lesson)
            db.flush()
            db.refresh(new_lesson)
            return {"id": new_lesson.id, "title": new_lesson.title, "content": new_lesson.content, "date": new_lesson.date.isoformat()}

    # Método para atualizar uma aula.
    def update_lesson(self, lesson_id: int, title: str, content: str, lesson_date: date):
        with self._get_db() as db:
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                lesson.title = title
                lesson.content = content
                lesson.date = lesson_date

    # Método para deletar uma aula.
    def delete_lesson(self, lesson_id: int):
        with self._get_db() as db:
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                db.delete(lesson)

    # Método para buscar todas as aulas de uma disciplina da turma.
    def get_lessons_for_subject(self, class_subject_id: int) -> list[dict]:
        with self._get_db() as db:
            lessons = db.query(Lesson).filter(Lesson.class_subject_id == class_subject_id).order_by(Lesson.date.desc()).all()
            return [{"id": l.id, "title": l.title, "content": l.content, "date": l.date.isoformat()} for l in lessons]

    # Método para criar um novo incidente.
    def create_incident(self, class_id: int, student_id: int, description: str, incident_date: date) -> dict | None:
        if not all([class_id, student_id, description, incident_date]): return None
        new_incident = Incident(class_id=class_id, student_id=student_id, description=description, date=incident_date)
        with self._get_db() as db:
            db.add(new_incident)
            db.flush()
            db.refresh(new_incident)
            return {"id": new_incident.id}

    # Método para buscar todos os incidentes de uma turma.
    def get_incidents_for_class(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            incidents = db.query(Incident).options(joinedload(Incident.student)).filter(Incident.class_id == class_id).order_by(Incident.date.desc()).all()
            return [
                {
                    "id": i.id, "description": i.description, "date": i.date.isoformat(),
                    "student_id": i.student.id, "student_first_name": i.student.first_name, "student_last_name": i.student.last_name
                } for i in incidents
            ]

    # Método para adicionar uma nova nota.
    def add_grade(self, student_id: int, assessment_id: int, score: float) -> dict | None:
        if not all([student_id, assessment_id, score is not None]): return None
        today = date.today()
        new_grade = Grade(student_id=student_id, assessment_id=assessment_id, score=score, date_recorded=today)
        with self._get_db() as db:
            db.add(new_grade)
            db.flush()
            db.refresh(new_grade)
            return {"id": new_grade.id, "score": new_grade.score}

    # Método para deletar uma nota.
    def delete_grade(self, grade_id: int):
        with self._get_db() as db:
            grade = db.query(Grade).filter(Grade.id == grade_id).first()
            if grade:
                db.delete(grade)

    # Método para inserir ou atualizar notas em lote para uma disciplina de uma turma (upsert).
    def upsert_grades_for_subject(self, class_subject_id: int, grades_data: list[dict]):
        with self._get_db() as db:
            # Busca todas as notas existentes para a disciplina e as armazena em um mapa para acesso rápido.
            existing_grades_query = db.query(Grade).join(Assessment).filter(Assessment.class_subject_id == class_subject_id)
            existing_grades_map = {(g.student_id, g.assessment_id): g for g in existing_grades_query}
            # Itera sobre os novos dados de nota.
            for grade_info in grades_data:
                # Garante que os IDs sejam inteiros para evitar duplicações causadas por incompatibilidade de tipos (ex: string vs int).
                try:
                    student_id = int(grade_info['student_id'])
                    assessment_id = int(grade_info['assessment_id'])
                except (ValueError, TypeError):
                    # Se a conversão falhar, pula este registro para evitar inconsistências.
                    continue

                score = grade_info['score']

                existing_grade = existing_grades_map.get((student_id, assessment_id))
                # Se a nota já existe, atualiza o valor se for diferente.
                if existing_grade:
                    if existing_grade.score != score:
                        existing_grade.score = score
                # Se a nota não existe, cria um novo registro.
                else:
                    new_grade = Grade(student_id=student_id, assessment_id=assessment_id, score=score, date_recorded=date.today())
                    db.add(new_grade)

    # Método para calcular a média ponderada de um aluno.
    @staticmethod
    def calculate_weighted_average(student_id: int, grades: list[dict], assessments: list[dict]) -> float:
        # Soma o peso de todas as avaliações da turma.
        total_weight = sum(a['weight'] for a in assessments)
        if total_weight == 0: return 0.0
        # Cria um mapa das notas do aluno para acesso rápido.
        student_grades = {g['assessment_id']: g['score'] for g in grades if g.get('student_id') == student_id}
        # Calcula a soma ponderada das notas (nota * peso). Se uma nota não existir, considera como 0.
        weighted_sum = sum(student_grades.get(a['id'], 0.0) * a['weight'] for a in assessments)
        # Retorna a média ponderada.
        return weighted_sum / total_weight

    # Método privado para inserir/atualizar alunos e matrículas em lote (usado pela importação de CSV).
    def _batch_upsert_students_and_enroll(self, db: Session, class_id: int, student_data_list: list[dict]):
        # Garante que cada aluno no CSV seja processado apenas uma vez, mesmo que haja duplicatas no arquivo.
        unique_student_data = {data['full_name'].lower(): data for data in student_data_list}
        # Obtém o próximo número de chamada para a turma.
        next_call_number = self._get_next_call_number(db, class_id)

        # Itera sobre os dados únicos dos alunos.
        for full_name_lower, data in unique_student_data.items():
            # Verifica se o aluno já existe no banco de dados.
            student = db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == full_name_lower).first()
            # Se o aluno já existe:
            if student:
                # Atualiza a data de nascimento se ela for fornecida no CSV e for diferente da existente.
                if data['birth_date'] and student.birth_date != data['birth_date']:
                    student.birth_date = data['birth_date']
            # Se o aluno não existe:
            else:
                # Cria um novo objeto Student.
                student = Student(
                    first_name=data['first_name'], last_name=data['last_name'],
                    birth_date=data['birth_date'], enrollment_date=date.today()
                )
                db.add(student)
                db.flush()  # Garante que o ID do aluno seja gerado antes de criar a matrícula.

            # Obtém o status do aluno do CSV.
            status = data['status']

            # Verifica se a matrícula para este aluno nesta turma já existe.
            enrollment = db.query(ClassEnrollment).filter_by(student_id=student.id, class_id=class_id).first()
            # Se a matrícula já existe:
            if enrollment:
                # Atualiza o status se for diferente.
                if enrollment.status != status:
                    enrollment.status = status
            # Se a matrícula não existe:
            else:
                # Cria um novo registro de matrícula.
                new_enrollment = ClassEnrollment(
                    class_id=class_id, student_id=student.id,
                    call_number=next_call_number, status=status
                )
                db.add(new_enrollment)
                # Incrementa o número de chamada para o próximo aluno.
                next_call_number += 1
