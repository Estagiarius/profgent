from datetime import date, datetime, timedelta # Importa a classe 'date', 'datetime' e 'timedelta'.
from sqlalchemy import func, or_, and_ # Importa a função 'func' do SQLAlchemy para usar funções SQL como COUNT, MAX, etc.
from sqlalchemy.orm import joinedload, Session # Importa 'joinedload' para carregamento otimizado de relacionamentos (evita N+1 queries) e 'Session' para type hinting.
from app.data.database import get_db_session # Importa o gerenciador de contexto para obter uma sessão de banco de dados.

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
from app.models.schedule import TimeSlot, WeeklySchedule
from app.models.attendance import Attendance
from app.utils.student_csv_parser import parse_student_csv # Importa a função de parsing de CSV de alunos.
from contextlib import contextmanager # Importa o gerenciador de contexto para criar blocos 'with'.

# Define a classe DataService, que encapsula toda a lógica de acesso e manipulação de dados.
class DataService:
    """
    Classe que fornece métodos para manipulação de dados de estudantes, tais como
    importação, criação, atualização, deleção e recuperação de informações. Suporta
    operações em lote e integrações com banco de dados via sessões do SQLAlchemy.

    :ivar _db_session: Sessão de banco de dados injetada no construtor para fins de
        teste ou execução customizada. Se não fornecida, uma nova sessão será gerada
        ao longo das operações.
    :type _db_session: Session | None
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

        if birth_date and birth_date > date.today():
            raise ValueError("Birth date cannot be in the future.")

        # Abre uma sessão de banco de dados.
        with self._get_db() as db:
            # Verifica se um aluno com o mesmo nome completo (ignorando maiúsculas/minúsculas) já existe.
            # Otimização 3: Compara first_name e last_name separadamente para evitar concatenação em todas as linhas (Full Scan).
            existing = db.query(Student).filter(
                and_(
                    func.lower(Student.first_name) == first_name.lower(),
                    func.lower(Student.last_name) == last_name.lower()
                )
            ).first()
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
            # Otimização 6: Tenta dividir o nome para buscar por colunas indexáveis primeiro.
            # Evita 'func.lower(col1+col2)' que causa full table scan.

            name = name.strip()
            parts = name.split(' ', 1)

            student = None
            if len(parts) == 2:
                first, last = parts
                student = db.query(Student).filter(
                    and_(
                        func.lower(Student.first_name) == first.lower(),
                        func.lower(Student.last_name) == last.lower()
                    )
                ).first()

            # Fallback se a busca dividida falhar (ex: nome do meio, ou formato incomum), ou se não tiver sobrenome
            if not student:
                 student = db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == name.lower()).first()

            if student:
                return {
                    "id": student.id, "first_name": student.first_name,
                    "last_name": student.last_name, "birth_date": student.birth_date.isoformat() if student.birth_date else None
                }
            return None

    # Método para buscar um aluno pelo ID.
    def get_student_by_id(self, student_id: int) -> dict | None:
        with self._get_db() as db:
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                return {
                    "id": student.id, "first_name": student.first_name,
                    "last_name": student.last_name, "birth_date": student.birth_date.isoformat() if student.birth_date else None
                }
            return None

    # Método para atualizar os dados de um aluno.
    def update_student(self, student_id: int, first_name: str, last_name: str, birth_date: date | None = None):
        if birth_date and birth_date > date.today():
            raise ValueError("Birth date cannot be in the future.")

        with self._get_db() as db:
            # Busca o aluno pelo ID.
            student = db.query(Student).filter(Student.id == student_id).first()
            # Se encontrar, atualiza os campos. O 'commit' é feito pelo gerenciador de contexto.
            if student:
                student.first_name = first_name
                student.last_name = last_name
                student.birth_date = birth_date

    # Método para deletar um aluno.
    def delete_student(self, student_id: int):
        with self._get_db() as db:
            # Otimização 6: Cascade Delete completo para garantir integridade e evitar dados órfãos.
            # Deleta manualmente os registros dependentes (incidentes, notas, matrículas)
            db.query(Incident).filter(Incident.student_id == student_id).delete()
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

    # Método para buscar alunos com paginação e filtro.
    def get_paginated_students(self, page: int, page_size: int, search_term: str = None, active_only: bool = False) -> dict:
        with self._get_db() as db:
            query = db.query(Student)

            if active_only:
                # Otimização 2: Usar EXISTS ao invés de JOIN + DISTINCT para performance
                # SELECT * FROM students s WHERE EXISTS (SELECT 1 FROM enrollments e WHERE e.student_id = s.id AND status = 'Active')
                query = query.filter(
                    db.query(ClassEnrollment.id).filter(
                        ClassEnrollment.student_id == Student.id,
                        ClassEnrollment.status == 'Active'
                    ).exists()
                )

            if search_term:
                search_pattern = f"%{search_term.lower()}%"
                query = query.filter(func.lower(Student.first_name + " " + Student.last_name).like(search_pattern))

            total_count = query.count()

            # Ordena por nome
            query = query.order_by(Student.first_name, Student.last_name)

            # Aplica paginação
            offset = (page - 1) * page_size
            students = query.offset(offset).limit(page_size).all()

            student_list = [
                {
                    "id": s.id,
                    "first_name": s.first_name,
                    "last_name": s.last_name,
                    "birth_date": s.birth_date.isoformat() if s.birth_date else None
                }
                for s in students
            ]

            return {
                "students": student_list,
                "total_count": total_count,
                "total_pages": (total_count + page_size - 1) // page_size if page_size > 0 else 1,
                "current_page": page
            }

    # Método para buscar alunos que não estão matriculados em uma turma específica.
    def get_unenrolled_students(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            # Otimização 3: Usar LEFT JOIN ... WHERE NULL ao invés de NOT IN (Subquery)
            # Isso geralmente performa melhor em bancos SQL para datasets maiores.
            students = (db.query(Student)
                        .outerjoin(ClassEnrollment, (ClassEnrollment.student_id == Student.id) & (ClassEnrollment.class_id == class_id))
                        .filter(ClassEnrollment.id == None)
                        .all())
            return [{"id": s.id, "first_name": s.first_name, "last_name": s.last_name} for s in students]

    # Método para buscar alunos (ativos) que fazem aniversário no dia de hoje.
    def get_students_with_birthday_today(self) -> list[dict]:
        today = date.today()
        # Converte para strings com zero à esquerda (ex: '01', '02', ..., '12').
        current_month = f"{today.month:02d}"
        current_day = f"{today.day:02d}"

        with self._get_db() as db:
            # Consulta otimizada que faz join com ClassEnrollment e Class para obter o nome da turma.
            # Filtra apenas matrículas 'Active'.
            # Usa strftime para extrair dia e mês da data de nascimento no SQLite.
            students = (
                db.query(Student, Class.name.label("class_name"))
                .join(ClassEnrollment, Student.id == ClassEnrollment.student_id)
                .join(Class, ClassEnrollment.class_id == Class.id)
                .filter(ClassEnrollment.status == 'Active')
                # noinspection PyTypeChecker
                .filter(func.strftime('%m', Student.birth_date) == current_month)
                # noinspection PyTypeChecker
                .filter(func.strftime('%d', Student.birth_date) == current_day)
                .all()
            )

            results = []
            for student, class_name in students:
                # Calcula a idade que o aluno está completando hoje.
                age = today.year - student.birth_date.year if student.birth_date else 0
                results.append({
                    "id": student.id,
                    "name": f"{student.first_name} {student.last_name}",
                    "age": age,
                    "class_name": class_name
                })
            return results

    # Método para adicionar um novo curso.
    def add_course(self, course_name: str, course_code: str, bncc_expected: str = None) -> dict | None:
        if not course_name or not course_code: return None
        new_course = Course(course_name=course_name, course_code=course_code, bncc_expected=bncc_expected)
        with self._get_db() as db:
            db.add(new_course)
            db.flush()
            db.refresh(new_course)
            return {"id": new_course.id, "course_name": new_course.course_name, "course_code": new_course.course_code, "bncc_expected": new_course.bncc_expected}

    # Método para buscar todos os cursos.
    def get_all_courses(self) -> list[dict]:
        with self._get_db() as db:
            courses = db.query(Course).order_by(Course.course_name).all()
            return [{"id": c.id, "course_name": c.course_name, "course_code": c.course_code, "bncc_expected": c.bncc_expected} for c in courses]

    # Método para obter a contagem total de cursos.
    def get_course_count(self) -> int:
        with self._get_db() as db:
            return db.query(func.count(Course.id)).scalar()

    # Método para buscar um curso pelo nome.
    def get_course_by_name(self, name: str) -> dict | None:
        with self._get_db() as db:
            course = db.query(Course).filter(func.lower(Course.course_name) == name.lower()).first()
            if course:
                return {"id": course.id, "course_name": course.course_name, "course_code": course.course_code, "bncc_expected": course.bncc_expected}
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
                    "bncc_expected": course.bncc_expected,
                    "classes": classes_list
                }
            return None

    # Método para atualizar um curso.
    def update_course(self, course_id: int, course_name: str, course_code: str, bncc_expected: str = None):
        with self._get_db() as db:
            course = db.query(Course).filter(Course.id == course_id).first()
            if course:
                course.course_name = course_name
                course.course_code = course_code
                course.bncc_expected = bncc_expected

    # Método para deletar um curso.
    def delete_course(self, course_id: int):
        with self._get_db() as db:
            # Verifica se há associações com turmas (ClassSubject)
            subjects = db.query(ClassSubject).filter(ClassSubject.course_id == course_id).first()
            if subjects:
                raise ValueError("Cannot delete course because it is associated with one or more classes.")

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

    # Método para copiar uma turma existente (estrutura e/ou alunos).
    def copy_class(self, source_class_id: int, new_name: str, copy_subjects: bool = False, copy_assessments: bool = False, copy_students: bool = False) -> dict | None:
        if not new_name:
            raise ValueError("O nome da nova turma não pode ser vazio.")

        with self._get_db() as db:
            # Verifica turma de origem
            source_class = db.query(Class).filter(Class.id == source_class_id).first()
            if not source_class:
                raise ValueError("Turma de origem não encontrada.")

            # Verifica duplicidade de nome
            if db.query(Class).filter(func.lower(Class.name) == func.lower(new_name)).first():
                raise ValueError(f"Uma turma com o nome '{new_name}' já existe.")

            # Cria nova turma
            new_class = Class(name=new_name, calculation_method=source_class.calculation_method)
            db.add(new_class)
            db.flush() # Gera ID

            # Copia Disciplinas (e Avaliações)
            if copy_subjects:
                source_subjects = db.query(ClassSubject).options(joinedload(ClassSubject.assessments)).filter(ClassSubject.class_id == source_class_id).all()

                for source_subj in source_subjects:
                    new_subj = ClassSubject(class_id=new_class.id, course_id=source_subj.course_id)
                    db.add(new_subj)
                    db.flush() # Gera ID para avaliações

                    if copy_assessments:
                        for source_assess in source_subj.assessments:
                            new_assess = Assessment(
                                class_subject_id=new_subj.id,
                                name=source_assess.name,
                                weight=source_assess.weight,
                                grading_period=source_assess.grading_period
                            )
                            db.add(new_assess)

            # Copia Alunos (apenas Ativos)
            if copy_students:
                source_enrollments = db.query(ClassEnrollment).filter(
                    ClassEnrollment.class_id == source_class_id,
                    ClassEnrollment.status == 'Active'
                ).order_by(ClassEnrollment.call_number).all()

                next_call = 1
                for enroll in source_enrollments:
                    new_enroll = ClassEnrollment(
                        class_id=new_class.id,
                        student_id=enroll.student_id,
                        call_number=next_call,
                        status='Active'
                    )
                    db.add(new_enroll)
                    next_call += 1

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
            # Otimização 1: Calcular contagem via SQL aggregation ao invés de carregar objetos em memória.
            results = (db.query(Class, func.count(ClassEnrollment.id).label('count'))
                       .outerjoin(ClassEnrollment, Class.id == ClassEnrollment.class_id)
                       .group_by(Class.id)
                       .order_by(Class.name)
                       .all())

            return [{"id": c.id, "name": c.name, "student_count": count} for c, count in results]

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
            # Otimização 7: Deep Cascade Delete para Turma.
            # Uma turma tem Subjects, que tem Assessments, que tem Grades.
            # Uma turma tem Incidents.
            # Uma turma tem Enrollments.
            # Uma turma tem Lessons (via Subject).

            # 1. Deletar Grades e Lessons e Assessments (via Subjects)
            subjects = db.query(ClassSubject).filter(ClassSubject.class_id == class_id).all()
            subject_ids = [s.id for s in subjects]

            if subject_ids:
                 assessments = db.query(Assessment).filter(Assessment.class_subject_id.in_(subject_ids)).all()
                 assessment_ids = [a.id for a in assessments]

                 if assessment_ids:
                     # Deletar notas dessas avaliações
                     db.query(Grade).filter(Grade.assessment_id.in_(assessment_ids)).delete(synchronize_session=False)

                 # Deletar avaliações
                 db.query(Assessment).filter(Assessment.class_subject_id.in_(subject_ids)).delete(synchronize_session=False)

                 # Deletar aulas
                 db.query(Lesson).filter(Lesson.class_subject_id.in_(subject_ids)).delete(synchronize_session=False)

                 # Deletar os subjects em si
                 db.query(ClassSubject).filter(ClassSubject.class_id == class_id).delete(synchronize_session=False)

            # 2. Deletar Incidentes
            db.query(Incident).filter(Incident.class_id == class_id).delete(synchronize_session=False)

            # 3. Deletar Matrículas
            db.query(ClassEnrollment).filter(ClassEnrollment.class_id == class_id).delete(synchronize_session=False)

            # 4. Finalmente, deletar a turma
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

    # Método para matricular múltiplos alunos de uma vez em uma turma.
    def enroll_students(self, class_id: int, student_ids: list[int]):
        with self._get_db() as db:
            # Pega o próximo número de chamada inicial.
            next_call_number = self._get_next_call_number(db, class_id)

            # Busca todas as matrículas existentes para esses alunos nesta turma de uma vez.
            existing_enrollments = db.query(ClassEnrollment).filter(
                ClassEnrollment.class_id == class_id,
                ClassEnrollment.student_id.in_(student_ids)
            ).all()

            # Mapeia por student_id para acesso rápido.
            existing_map = {e.student_id: e for e in existing_enrollments}

            new_enrollments_data = []

            for student_id in student_ids:
                existing = existing_map.get(student_id)
                if existing:
                    # Se já existe (talvez inativo), reativa e atualiza número.
                    existing.status = "Active"
                    existing.call_number = next_call_number
                else:
                    # Otimização 5: Preparar inserção em lote
                    new_enrollments_data.append({
                        "class_id": class_id,
                        "student_id": student_id,
                        "call_number": next_call_number,
                        "status": "Active"
                    })

                next_call_number += 1

            if new_enrollments_data:
                db.bulk_insert_mappings(ClassEnrollment, new_enrollments_data)

            # Persiste as mudanças na sessão (necessário para testes com autoflush=False e para garantir visibilidade)
            db.flush()

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
    def add_assessment(self, class_subject_id: int, name: str, weight: float, grading_period: int = 1, bncc_codes: str = None) -> dict | None:
        if not all([class_subject_id, name, weight is not None]): return None

        if weight < 0:
            raise ValueError("Assessment weight must be non-negative.")

        if not (1 <= grading_period <= 5):
             raise ValueError("Grading period must be between 1 and 5.")

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

    # Método auxiliar para garantir que a avaliação final (período 5) exista.
    def ensure_final_assessment(self, class_subject_id: int) -> dict:
        with self._get_db() as db:
            # Procura por uma avaliação existente no período 5
            assessment = db.query(Assessment).filter(
                Assessment.class_subject_id == class_subject_id,
                Assessment.grading_period == 5
            ).first()

            if assessment:
                return {"id": assessment.id, "name": assessment.name}

            # Se não existir, cria uma nova
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

    # Método para atualizar uma avaliação.
    def update_assessment(self, assessment_id: int, name: str, weight: float, grading_period: int = None, bncc_codes: str = None):
        if weight < 0:
            raise ValueError("Assessment weight must be non-negative.")

        if grading_period is not None and not (1 <= grading_period <= 5):
             raise ValueError("Grading period must be between 1 and 5.")

        with self._get_db() as db:
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if assessment:
                assessment.name = name
                assessment.weight = weight
                if grading_period is not None:
                    assessment.grading_period = grading_period
                assessment.bncc_codes = bncc_codes

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
            assessments = db.query(Assessment).filter(Assessment.class_subject_id == class_subject_id).order_by(Assessment.grading_period, Assessment.name).all()
            return [{"id": a.id, "name": a.name, "weight": a.weight, "grading_period": a.grading_period} for a in assessments]

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

    def get_student_period_averages(self, student_id: int, class_subject_id: int) -> dict:
        """
        Calcula as médias para cada bimestre (1-4) e a média final.
        Retorna um dicionário com as médias e a nota final sobrescrita (se houver).
        """
        with self._get_db() as db:
            # Busca todas as avaliações desta disciplina
            assessments = db.query(Assessment).filter(Assessment.class_subject_id == class_subject_id).all()
            if not assessments:
                return {}

            # Busca notas do aluno
            assessment_ids = [a.id for a in assessments]
            grades = db.query(Grade).filter(
                Grade.student_id == student_id,
                Grade.assessment_id.in_(assessment_ids)
            ).all()

            # Organiza dados
            grades_map = {g.assessment_id: g.score for g in grades}

            results = {}
            final_sum = 0.0
            periods_count = 0

            # Processa bimestres 1 a 4
            for period in range(1, 5):
                period_assessments = [a for a in assessments if a.grading_period == period]
                if not period_assessments:
                    results[period] = None
                    # Se não tem avaliação no bimestre, considera média 0 para o final?
                    # Ou ignora no cálculo? "média simples das médias finais"
                    # Geralmente, se o bimestre passou, a média é 0. Se não passou, é null.
                    # Vamos assumir 0 para o cálculo final por enquanto.
                    final_sum += 0.0
                    periods_count += 1
                else:
                    assessments_data = [{"id": a.id, "weight": a.weight} for a in period_assessments]

                    # Otimização: Passar grades_map diretamente e pré-calcular peso
                    period_total_weight = sum(a['weight'] for a in assessments_data)

                    # calculate_weighted_average agora aceita dict e total_weight
                    avg = self.calculate_weighted_average(student_id, grades_map, assessments_data, total_weight=period_total_weight)
                    results[period] = avg
                    final_sum += avg
                    periods_count += 1

            # Calcula média final (aritmética)
            calculated_final = final_sum / 4.0 if periods_count > 0 else 0.0
            results["final_calculated"] = calculated_final

            # Verifica override (período 5)
            final_assessment = next((a for a in assessments if a.grading_period == 5), None)
            if final_assessment and final_assessment.id in grades_map:
                results["final_override"] = grades_map[final_assessment.id]
            else:
                results["final_override"] = None

            return results

    def get_class_period_averages(self, class_subject_id: int) -> dict:
        """
        Calcula médias de todos os bimestres e final para todos os alunos da disciplina.
        Retorna: { student_id: { 1: float, ..., "final_calculated": float, "final_override": float } }
        """
        with self._get_db() as db:
            assessments = db.query(Assessment).filter(Assessment.class_subject_id == class_subject_id).all()
            if not assessments: return {}

            assessment_ids = [a.id for a in assessments]
            # Fetch simple columns
            grades = db.query(Grade.student_id, Grade.assessment_id, Grade.score).filter(Grade.assessment_id.in_(assessment_ids)).all()

            # Map: student -> assessment_id -> score
            student_grades = {}
            for g in grades:
                if g.student_id not in student_grades: student_grades[g.student_id] = {}
                student_grades[g.student_id][g.assessment_id] = g.score

            results = {}
            # Group assessments by period
            period_assessments = {1: [], 2: [], 3: [], 4: [], 5: []}
            for a in assessments:
                period_assessments[a.grading_period].append({"id": a.id, "weight": a.weight})

            final_assessment_id = next((a.id for a in assessments if a.grading_period == 5), None)

            # Pre-calcular pesos por período
            period_weights = {
                p: sum(a['weight'] for a in period_assessments[p])
                for p in range(1, 6)
            }

            for student_id, s_grades_map in student_grades.items():
                s_results = {}
                final_sum = 0.0
                periods_count = 0

                for period in range(1, 5):
                    assessments_data = period_assessments[period]
                    if not assessments_data:
                        s_results[period] = None
                        final_sum += 0.0
                        periods_count += 1
                        continue

                    # Otimização: Usar peso pré-calculado e chamar calculate_weighted_average otimizado
                    total_weight = period_weights[period]
                    avg = self.calculate_weighted_average(student_id, s_grades_map, assessments_data, total_weight=total_weight)

                    s_results[period] = avg
                    final_sum += avg
                    periods_count += 1

                s_results["final_calculated"] = final_sum / 4.0 if periods_count > 0 else 0.0

                if final_assessment_id and final_assessment_id in s_grades_map:
                    s_results["final_override"] = s_grades_map[final_assessment_id]
                else:
                    s_results["final_override"] = None

                results[student_id] = s_results

            return results

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
            # Otimização 4: Reduzir queries usando queries combinadas ou joinedload
            # Originalmente fazia 4 queries: subjects, assessments, grades, incidents

            # Buscar subjects e assessments juntos é possível mas complexo se filtrar por ids.
            # Vamos fazer de forma eficiente:
            # 1. Buscar todas as avaliações da turma (join ClassSubject)
            assessments = (db.query(Assessment)
                           .join(ClassSubject)
                           .filter(ClassSubject.class_id == class_id)
                           .all())

            assessments_data = [{"id": a.id, "weight": a.weight} for a in assessments]
            assessment_ids = [a['id'] for a in assessments_data]

            if not assessments_data:
                 weighted_average = 0.0
            else:
                 # 2. Buscar notas para essas avaliações e este aluno
                 grades = db.query(Grade).filter(
                     Grade.student_id == student_id,
                     Grade.assessment_id.in_(assessment_ids)
                 ).all()
                 grades_data = [{"assessment_id": g.assessment_id, "score": g.score, "student_id": g.student_id} for g in grades]

                 # Calcula a média
                 weighted_average = self.calculate_weighted_average(student_id, grades_data, assessments_data)

            # 3. Incidentes (Query separada é ok aqui pois é simples count)
            incidents_count = db.query(func.count(Incident.id)).filter(Incident.class_id == class_id, Incident.student_id == student_id).scalar()

            return {
                "weighted_average": weighted_average,
                "incident_count": incidents_count
            }

    # Método para identificar alunos em situação de risco (notas baixas ou muitos incidentes).
    def get_students_at_risk(self, class_id: int, grade_threshold: float = 5.0, incident_threshold: int = 2) -> list[dict]:
        # Otimização 5: Fetch em lote de todos os dados necessários para evitar N+1 queries.
        # Anteriormente chamava get_student_performance_summary para cada aluno.

        with self._get_db() as db:
             # 1. Busca todas as matrículas ativas da turma (com dados dos alunos)
             enrollments = (db.query(ClassEnrollment)
                            .options(joinedload(ClassEnrollment.student))
                            .filter(ClassEnrollment.class_id == class_id, ClassEnrollment.status == 'Active')
                            .all())

             student_ids = [e.student_id for e in enrollments]
             if not student_ids:
                 return []

             # 2. Busca todos os incidentes da turma de uma vez, agrupados por aluno
             incidents_query = (db.query(Incident.student_id, func.count(Incident.id).label('count'))
                                .filter(Incident.class_id == class_id, Incident.student_id.in_(student_ids))
                                .group_by(Incident.student_id).all())
             incidents_map = {row.student_id: row.count for row in incidents_query}

             # 3. Busca todas as avaliações da turma (para os pesos)
             assessments = (db.query(Assessment)
                            .join(ClassSubject)
                            .filter(ClassSubject.class_id == class_id)
                            .all())
             assessments_data = [{"id": a.id, "weight": a.weight} for a in assessments]
             assessment_ids = [a['id'] for a in assessments_data]

             # 4. Busca todas as notas de todos os alunos nessas avaliações
             grades = db.query(Grade).filter(
                 Grade.student_id.in_(student_ids),
                 Grade.assessment_id.in_(assessment_ids)
             ).all()

             # Organiza notas por aluno para cálculo em memória
             # grades_by_student = {student_id: {assessment_id: score}}
             grades_by_student = {}
             for g in grades:
                 if g.student_id not in grades_by_student:
                     grades_by_student[g.student_id] = {}
                 grades_by_student[g.student_id][g.assessment_id] = g.score

             # Pre-calcula peso total
             total_weight = sum(a['weight'] for a in assessments_data)

             at_risk_students = []
             # Processamento em memória
             for enrollment in enrollments:
                 student_id = enrollment.student_id

                 # Recupera incidentes do mapa (default 0)
                 incident_count = incidents_map.get(student_id, 0)

                 # Recupera notas e calcula média
                 student_grades = grades_by_student.get(student_id, {})
                 weighted_average = self.calculate_weighted_average(student_id, student_grades, assessments_data, total_weight=total_weight)

                 is_at_risk = (weighted_average < grade_threshold) or \
                              (incident_count >= incident_threshold)

                 if is_at_risk:
                     at_risk_students.append({
                        "student_id": student_id,
                        "student_name": f"{enrollment.student.first_name} {enrollment.student.last_name}",
                        "average_grade": weighted_average,
                        "incident_count": incident_count
                    })

        return at_risk_students

    # Método para criar um novo registro de aula.
    def create_lesson(self, class_subject_id: int, title: str, content: str, lesson_date: date, bncc_codes: str = None) -> dict | None:
        if not all([class_subject_id, title, lesson_date]): return None
        new_lesson = Lesson(class_subject_id=class_subject_id, title=title, content=content, date=lesson_date, bncc_codes=bncc_codes)
        with self._get_db() as db:
            db.add(new_lesson)
            db.flush()
            db.refresh(new_lesson)
            return {"id": new_lesson.id, "title": new_lesson.title, "content": new_lesson.content, "date": new_lesson.date.isoformat(), "bncc_codes": new_lesson.bncc_codes}

    # Método para atualizar uma aula.
    def update_lesson(self, lesson_id: int, title: str, content: str, lesson_date: date, bncc_codes: str = None):
        with self._get_db() as db:
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                lesson.title = title
                lesson.content = content
                lesson.date = lesson_date
                lesson.bncc_codes = bncc_codes

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

    # Método para copiar aulas (conteúdo) para outra disciplina.
    def copy_lessons(self, source_lesson_ids: list[int], target_class_subject_id: int) -> int:
        if not source_lesson_ids or not target_class_subject_id:
            return 0

        with self._get_db() as db:
            # Busca as aulas de origem
            source_lessons = db.query(Lesson).filter(Lesson.id.in_(source_lesson_ids)).all()

            count = 0
            for src in source_lessons:
                new_lesson = Lesson(
                    class_subject_id=target_class_subject_id,
                    title=src.title,
                    content=src.content,
                    date=src.date # Mantém a mesma data (pode ser editada depois)
                )
                db.add(new_lesson)
                count += 1

            db.flush()
            return count

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

    # Método para buscar incidentes de um aluno específico em uma turma (Otimização para Boletim).
    def get_student_incidents(self, student_id: int, class_id: int) -> list[dict]:
        with self._get_db() as db:
            incidents = db.query(Incident).filter(
                Incident.student_id == student_id,
                Incident.class_id == class_id
            ).order_by(Incident.date.desc()).all()

            return [
                {"id": i.id, "description": i.description, "date": i.date.isoformat()}
                for i in incidents
            ]

    # --- Métodos de Controle de Frequência ---

    def register_attendance(self, lesson_id: int, attendance_data: list[dict]):
        """
        Registra ou atualiza a frequência para uma aula.

        :param lesson_id: ID da aula.
        :param attendance_data: Lista de dicts com {'student_id': int, 'status': str}.
                                Status aceitos: 'P', 'F', 'J', 'A'.
        """
        valid_statuses = {'P', 'F', 'J', 'A'}

        with self._get_db() as db:
            # Verifica se a aula existe
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if not lesson:
                raise ValueError(f"Lesson with id {lesson_id} not found.")

            # Busca registros existentes para upsert
            existing_records = db.query(Attendance).filter(Attendance.lesson_id == lesson_id).all()
            existing_map = {att.student_id: att for att in existing_records}

            to_insert = []

            for entry in attendance_data:
                student_id = entry.get('student_id')
                status = entry.get('status', 'P')

                if status not in valid_statuses:
                    continue # Ou raise ValueError

                existing = existing_map.get(student_id)
                if existing:
                    if existing.status != status:
                        existing.status = status
                else:
                    to_insert.append({
                        "lesson_id": lesson_id,
                        "student_id": student_id,
                        "status": status
                    })

            if to_insert:
                db.bulk_insert_mappings(Attendance, to_insert)

            db.flush()

    def get_lesson_attendance(self, lesson_id: int) -> list[dict]:
        """Retorna a lista de frequência para uma aula."""
        with self._get_db() as db:
            records = db.query(Attendance).filter(Attendance.lesson_id == lesson_id).all()
            return [{"student_id": r.student_id, "status": r.status} for r in records]

    def get_student_attendance_stats(self, student_id: int, class_subject_id: int) -> dict:
        """
        Calcula as estatísticas de frequência do aluno em uma disciplina.

        Retorna:
            {
                "total_lessons": int,
                "present_count": int, # P + A + J
                "absent_count": int, # F
                "percentage": float
            }
        """
        with self._get_db() as db:
            # Busca todas as aulas da disciplina
            lesson_ids = db.query(Lesson.id).filter(Lesson.class_subject_id == class_subject_id)

            # Conta registros de presença do aluno nessas aulas
            # Assumption: Se não tiver registro, conta como ausência ou ignora?
            # Pela lógica de "Chamada", só conta aulas onde houve chamada registrada para o aluno.
            # Mas se o aluno faltou e não foi registrado (ex: bug), ou a chamada não foi feita?
            # Vamos contar apenas registros existentes na tabela Attendance.

            records = db.query(Attendance).filter(
                Attendance.student_id == student_id,
                Attendance.lesson_id.in_(lesson_ids)
            ).all()

            total_recorded = len(records)
            if total_recorded == 0:
                return {"total_lessons": 0, "present_count": 0, "absent_count": 0, "percentage": 100.0}

            # P, A (Atraso), J (Justificada) -> Contam como Presença no cálculo simplificado acordado.
            # F -> Falta.

            present_count = sum(1 for r in records if r.status in ('P', 'A', 'J'))
            absent_count = sum(1 for r in records if r.status == 'F')

            percentage = (present_count / total_recorded) * 100

            return {
                "total_lessons": total_recorded,
                "present_count": present_count,
                "absent_count": absent_count,
                "percentage": percentage
            }

    def get_class_attendance_stats(self, class_subject_id: int) -> dict:
        """
        Calcula estatísticas de frequência para todos os alunos de uma disciplina em lote.
        Retorna: { student_id: { "total_lessons": int, "percentage": float, ... } }
        """
        with self._get_db() as db:
            # Busca IDs das aulas
            lessons = db.query(Lesson.id).filter(Lesson.class_subject_id == class_subject_id).all()
            lesson_ids = [l.id for l in lessons]

            if not lesson_ids:
                return {}

            # Busca todos os registros de presença dessas aulas de uma só vez
            # Otimização: Select specific columns to avoid ORM overhead
            records = db.query(Attendance.student_id, Attendance.status).filter(Attendance.lesson_id.in_(lesson_ids)).all()

            stats = {} # student_id -> {present, absent, total}

            for r in records:
                if r.student_id not in stats:
                    stats[r.student_id] = {'present': 0, 'absent': 0, 'total': 0}

                stats[r.student_id]['total'] += 1
                if r.status in ('P', 'A', 'J'):
                    stats[r.student_id]['present'] += 1
                elif r.status == 'F':
                    stats[r.student_id]['absent'] += 1

            result = {}
            for sid, data in stats.items():
                total = data['total']
                pct = (data['present'] / total * 100) if total > 0 else 100.0
                result[sid] = {
                    "total_lessons": total,
                    "present_count": data['present'],
                    "absent_count": data['absent'],
                    "percentage": pct
                }
            return result

    # Método para adicionar uma nova nota.
    def add_grade(self, student_id: int, assessment_id: int, score: float) -> dict | None:
        if not all([student_id, assessment_id, score is not None]): return None

        if not (0 <= score <= 10):
            raise ValueError("Score must be between 0 and 10.")

        today = date.today()
        new_grade = Grade(student_id=student_id, assessment_id=assessment_id, score=score, date_recorded=today.isoformat())
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
            # Otimização 4: Batch Update/Insert para alta performance

            # 1. Identificar existentes
            existing_grades_query = db.query(Grade).join(Assessment).filter(Assessment.class_subject_id == class_subject_id)
            existing_grades_map = {(g.student_id, g.assessment_id): g for g in existing_grades_query}

            to_insert = []
            to_update = []

            today_str = date.today().isoformat()

            for grade_info in grades_data:
                try:
                    student_id = int(grade_info['student_id'])
                    assessment_id = int(grade_info['assessment_id'])
                except (ValueError, TypeError):
                    continue

                score = grade_info['score']
                if not (0 <= score <= 10):
                    raise ValueError(f"Score must be between 0 and 10.")

                existing_grade = existing_grades_map.get((student_id, assessment_id))

                if existing_grade:
                    if existing_grade.score != score:
                        # Para update em lote, precisamos do ID primário
                        to_update.append({
                            "id": existing_grade.id,
                            "score": score
                        })
                else:
                    to_insert.append({
                        "student_id": student_id,
                        "assessment_id": assessment_id,
                        "score": score,
                        "date_recorded": today_str
                    })

            # Executar em lote
            if to_insert:
                db.bulk_insert_mappings(Grade, to_insert)
            if to_update:
                db.bulk_update_mappings(Grade, to_update)

            # Commit é gerenciado pelo context manager, mas se estivermos em transação manual:
            db.flush()

    # Método para calcular a média ponderada de um aluno.
    @staticmethod
    def calculate_weighted_average(student_id: int, grades: list[dict] | dict[int, float], assessments: list[dict], total_weight: float = None) -> float:
        # Soma o peso de todas as avaliações da turma.
        if total_weight is None:
            total_weight = sum(a['weight'] for a in assessments)
        if total_weight == 0: return 0.0

        # Cria um mapa das notas do aluno para acesso rápido, se não for passado um dict.
        if isinstance(grades, dict):
            student_grades = grades
        else:
            student_grades = {g['assessment_id']: g['score'] for g in grades if g.get('student_id') == student_id}

        # Calcula a soma ponderada das notas (nota * peso). Se uma nota não existir, considera como 0.
        weighted_sum = sum(student_grades.get(a['id'], 0.0) * a['weight'] for a in assessments)
        # Retorna a média ponderada.
        return weighted_sum / total_weight

    # Método para obter estatísticas globais do sistema.
    def get_global_dashboard_stats(self) -> dict:
        with self._get_db() as db:
            # Otimização 7: Count distinct direto no SQL, evitando fetch.
            active_students = db.query(func.count(func.distinct(ClassEnrollment.student_id))).filter(ClassEnrollment.status == 'Active').scalar()
            total_classes = db.query(func.count(Class.id)).scalar()
            total_courses = db.query(func.count(Course.id)).scalar()
            total_incidents = db.query(func.count(Incident.id)).scalar()

            return {
                "active_students": active_students or 0,
                "total_classes": total_classes or 0,
                "total_courses": total_courses or 0,
                "total_incidents": total_incidents or 0
            }

    # Método para obter o ranking de incidentes por turma.
    def get_class_incident_ranking(self, limit: int = 5) -> list[dict]:
        with self._get_db() as db:
            # Query grouped by Class.id, ordering by count descending
            ranking = (
                db.query(Class.name, func.count(Incident.id).label('count'))
                .join(Incident, Class.id == Incident.class_id)
                .group_by(Class.id)
                .order_by(func.count(Incident.id).desc())
                .limit(limit)
                .all()
            )
            return [{"class_name": r.name, "count": r.count} for r in ranking]

    # Método auxiliar para buscar dados completos de uma turma para relatórios (Optimized Fetch).
    def get_class_report_data(self, class_id: int) -> dict:
        """
        Busca todos os dados necessários para gerar relatórios de uma turma (Disciplinas, Avaliações, Notas, Alunos)
        em poucas queries otimizadas, evitando o problema de N+1 queries.
        """
        with self._get_db() as db:
            # 1. Buscar Disciplinas e Avaliações
            subjects = (db.query(ClassSubject)
                        .options(joinedload(ClassSubject.assessments), joinedload(ClassSubject.course))
                        .filter(ClassSubject.class_id == class_id)
                        .all())

            # Estruturar disciplinas e avaliações
            subjects_data = []
            all_assessment_ids = []

            for s in subjects:
                assessments = [{"id": a.id, "name": a.name, "weight": a.weight} for a in s.assessments]
                all_assessment_ids.extend([a['id'] for a in assessments])
                subjects_data.append({
                    "id": s.id,
                    "course_name": s.course.course_name,
                    "assessments": assessments
                })

            # 2. Buscar Alunos (Matrículas Ativas)
            enrollments = (db.query(ClassEnrollment)
                           .options(joinedload(ClassEnrollment.student))
                           .filter(ClassEnrollment.class_id == class_id) # Pega todos (ativos e inativos) para histórico ou só ativos? Relatórios costumam ser de ativos.
                           .order_by(ClassEnrollment.call_number)
                           .all())

            students_data = []
            student_ids = []
            for e in enrollments:
                student_ids.append(e.student_id)
                students_data.append({
                    "student_id": e.student_id,
                    "name": f"{e.student.first_name} {e.student.last_name}",
                    "call_number": e.call_number,
                    "status": e.status
                })

            # 3. Buscar Notas
            grades_map = {} # (student_id, assessment_id) -> score
            if all_assessment_ids and student_ids:
                 # Otimização: Seleciona apenas colunas necessárias para evitar overhead de objetos ORM
                 grades = db.query(Grade.student_id, Grade.assessment_id, Grade.score).filter(
                     Grade.assessment_id.in_(all_assessment_ids),
                     Grade.student_id.in_(student_ids)
                 ).all()
                 for g in grades:
                     grades_map[(g.student_id, g.assessment_id)] = g.score

            return {
                "subjects": subjects_data,
                "students": students_data,
                "grades_map": grades_map
            }

    # Método para calcular as médias finais de todos os alunos ativos em um curso.
    def get_course_averages(self, course_id: int) -> list[float]:
        """Calcula as médias finais ponderadas para todos os alunos ativos em um curso."""
        # Otimização 6: Eager Loading massivo para evitar N+1 ao iterar sobre turmas

        averages = []
        with self._get_db() as db:
            # Busca todas as disciplinas deste curso, carregando eagermente as avaliações
            subjects = (db.query(ClassSubject)
                        .options(joinedload(ClassSubject.assessments))
                        .filter(ClassSubject.course_id == course_id)
                        .all())

            if not subjects:
                return []

            subject_ids = [s.id for s in subjects]
            class_ids = [s.class_id for s in subjects]

            # Busca todas as matrículas ativas de uma vez para todas as turmas envolvidas
            # Usa joinedload se precisasse de dados do aluno, mas aqui só precisamos do ID
            enrollments = db.query(ClassEnrollment).filter(
                ClassEnrollment.class_id.in_(class_ids),
                ClassEnrollment.status == 'Active'
            ).all()

            # Mapa: class_id -> list of student_ids
            class_students_map = {}
            for e in enrollments:
                if e.class_id not in class_students_map:
                    class_students_map[e.class_id] = []
                class_students_map[e.class_id].append(e.student_id)

            # Busca TODAS as notas relevantes para este curso de uma vez
            # Filtramos por assessments que pertencem aos subjects deste curso
            # Como carregamos subjects.assessments, podemos coletar os IDs
            all_assessment_ids = []
            assessments_map = {} # subject_id -> list of assessments data

            for subject in subjects:
                s_assessments = [{"id": a.id, "weight": a.weight} for a in subject.assessments]
                assessments_map[subject.id] = s_assessments
                all_assessment_ids.extend([a['id'] for a in s_assessments])

            if not all_assessment_ids:
                return []

            # Otimização: Seleciona apenas colunas necessárias para evitar overhead de objetos ORM
            all_grades = db.query(Grade.student_id, Grade.assessment_id, Grade.score).filter(Grade.assessment_id.in_(all_assessment_ids)).all()

            # Mapa: (student_id, assessment_id) -> score OU student_id -> {assessment_id: score}
            # Otimização: Usar dict para busca O(1) e evitar reprocessamento em calculate_weighted_average
            grades_by_student = {}
            for g in all_grades:
                if g.student_id not in grades_by_student:
                    grades_by_student[g.student_id] = {}
                grades_by_student[g.student_id][g.assessment_id] = g.score

            for subject in subjects:
                assessments_data = assessments_map.get(subject.id, [])
                if not assessments_data:
                    continue

                # Pre-calcula peso total para o subject
                total_weight = sum(a['weight'] for a in assessments_data)

                student_ids = class_students_map.get(subject.class_id, [])

                for student_id in student_ids:
                    # Passa o mapa de notas diretamente e o peso total
                    student_grades = grades_by_student.get(student_id, {})
                    avg = self.calculate_weighted_average(student_id, student_grades, assessments_data, total_weight=total_weight)
                    averages.append(avg)

        return averages

    # Método para calcular a taxa de aprovação global baseada em todas as disciplinas e alunos ativos.
    def get_global_performance_stats(self) -> dict:
        """Calcula taxas globais de aprovação/reprovação e lista alunos em risco e destaque."""
        # Otimização 7: Carregamento massivo de dados para evitar milhares de queries.

        total_enrollments_analyzed = 0
        approved_count = 0
        failed_details = []
        honor_roll_details = []

        with self._get_db() as db:
            # 1. Carrega todos Subjects com Class e Course
            subjects = db.query(ClassSubject).options(
                joinedload(ClassSubject.class_),
                joinedload(ClassSubject.course),
                joinedload(ClassSubject.assessments) # Eager load assessments
            ).all()

            if not subjects:
                return {
                    "total_analyzed": 0, "approved": 0, "failed": 0, "approval_rate": 0.0,
                    "failed_details": [], "honor_roll_details": []
                }

            # 2. Carrega todas as matrículas ativas do sistema com dados dos alunos
            all_active_enrollments = (db.query(ClassEnrollment)
                                      .options(joinedload(ClassEnrollment.student))
                                      .filter(ClassEnrollment.status == 'Active')
                                      .all())

            # Indexar enrollments por class_id -> list[enrollment_obj]
            enrollments_by_class = {}
            for e in all_active_enrollments:
                if e.class_id not in enrollments_by_class:
                    enrollments_by_class[e.class_id] = []
                enrollments_by_class[e.class_id].append(e)

            # 3. Carregar TODAS as notas do sistema? Pode ser muito.
            # Mas carregar N vezes é pior.
            # Vamos carregar todas as notas cujos assessments foram carregados.
            all_assessment_ids = []
            for s in subjects:
                for a in s.assessments:
                    all_assessment_ids.append(a.id)

            # Se houver muitas notas, isso pode consumir muita memória.
            # Mas para um relatório global, é trade-off: Memória vs DB Latency.
            # Vamos assumir que cabe na memória (alguns milhares de notas).
            all_grades = []
            if all_assessment_ids:
                 # Batch fetch se for muito grande?
                 # SQLite aguenta muitos parâmetros em IN clause (até 999 ou mais dependendo da versão/config).
                 # Vamos fazer em chunks de 500 para segurança.
                 chunk_size = 500
                 for i in range(0, len(all_assessment_ids), chunk_size):
                     chunk = all_assessment_ids[i:i+chunk_size]
                     # Otimização: Seleciona apenas colunas necessárias
                     grades_chunk = db.query(Grade.student_id, Grade.assessment_id, Grade.score).filter(Grade.assessment_id.in_(chunk)).all()
                     all_grades.extend(grades_chunk)

            # Indexar grades por student_id (Map para busca rápida O(1))
            grades_by_student = {}
            for g in all_grades:
                if g.student_id not in grades_by_student:
                    grades_by_student[g.student_id] = {}
                grades_by_student[g.student_id][g.assessment_id] = g.score

            # Processamento em memória
            for subject in subjects:
                assessments_data = [{"id": a.id, "weight": a.weight} for a in subject.assessments]
                if not assessments_data: continue

                # Pre-calcula peso
                total_weight = sum(a['weight'] for a in assessments_data)

                class_enrollments = enrollments_by_class.get(subject.class_id, [])

                for enrollment in class_enrollments:
                    student_grades = grades_by_student.get(enrollment.student_id, {})
                    avg = self.calculate_weighted_average(enrollment.student_id, student_grades, assessments_data, total_weight=total_weight)

                    total_enrollments_analyzed += 1

                    if avg >= 5.0:
                        approved_count += 1
                        if avg >= 9.0:
                             honor_roll_details.append({
                                "student_name": f"{enrollment.student.first_name} {enrollment.student.last_name}",
                                "class_name": subject.class_.name,
                                "course_name": subject.course.course_name,
                                "average": round(avg, 2)
                            })
                    else:
                        failed_details.append({
                            "student_name": f"{enrollment.student.first_name} {enrollment.student.last_name}",
                            "class_name": subject.class_.name,
                            "course_name": subject.course.course_name,
                            "average": round(avg, 2)
                        })

        return {
            "total_analyzed": total_enrollments_analyzed,
            "approved": approved_count,
            "failed": total_enrollments_analyzed - approved_count,
            "approval_rate": (approved_count / total_enrollments_analyzed * 100) if total_enrollments_analyzed > 0 else 0.0,
            "failed_details": failed_details,
            "honor_roll_details": honor_roll_details
        }

    # Método privado para inserir/atualizar alunos e matrículas em lote (usado pela importação de CSV).
    def _batch_upsert_students_and_enroll(self, db: Session, class_id: int, student_data_list: list[dict]):
        # Garante que cada aluno no CSV seja processado apenas uma vez, mesmo que haja duplicatas no arquivo.
        unique_student_data = {data['full_name'].lower(): data for data in student_data_list}

        # Otimização: Buscar todos os candidatos a alunos existentes de uma só vez usando OR conditions
        # Isso evita fazer queries individuais dentro do loop.
        existing_students_map = {}
        conditions_list = list(unique_student_data.values())

        if conditions_list:
            # Busca em lotes de 50 para evitar queries gigantescas se a lista for muito grande
            batch_size = 50

            for i in range(0, len(conditions_list), batch_size):
                batch = conditions_list[i:i+batch_size]
                batch_conditions = [
                    and_(func.lower(Student.first_name) == data['first_name'].lower(),
                         func.lower(Student.last_name) == data['last_name'].lower())
                    for data in batch
                ]
                found_students = db.query(Student).filter(or_(*batch_conditions)).all()
                for s in found_students:
                    full_name = (s.first_name + " " + s.last_name).lower()
                    existing_students_map[full_name] = s

        # Obtém o próximo número de chamada para a turma.
        next_call_number = self._get_next_call_number(db, class_id)

        # Otimização: Buscar matrículas existentes para os alunos encontrados
        existing_student_ids = [s.id for s in existing_students_map.values()]
        existing_enrollments_map = {}
        if existing_student_ids:
             enrollments = db.query(ClassEnrollment).filter(
                 ClassEnrollment.class_id == class_id,
                 ClassEnrollment.student_id.in_(existing_student_ids)
             ).all()
             existing_enrollments_map = {e.student_id: e for e in enrollments}

        # Itera sobre os dados únicos dos alunos.
        for full_name_lower, data in unique_student_data.items():
            # Verifica se o aluno já existe no mapa pré-carregado
            student = existing_students_map.get(full_name_lower)

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
                    birth_date=data['birth_date'], enrollment_date=date.today().isoformat()
                )
                db.add(student)
                db.flush()  # Garante que o ID do aluno seja gerado antes de criar a matrícula.
                # Não adicionamos ao existing_enrollments_map porque é novo e não terá matricula

            # Obtém o status do aluno do CSV.
            status = data['status']

            # Verifica se a matrícula para este aluno nesta turma já existe.
            # Se o aluno acabou de ser criado, enrollment será None naturalmente (não está no map)
            enrollment = existing_enrollments_map.get(student.id)

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

    # --- Schedule Methods ---

    def create_time_slot(self, day_of_week: int, period_index: int, start_time: str, end_time: str) -> dict | None:
        """Cria um novo slot de tempo na grade horária."""
        try:
             start = datetime.strptime(start_time, "%H:%M").time()
             end = datetime.strptime(end_time, "%H:%M").time()
        except ValueError:
             raise ValueError("Horários devem estar no formato HH:MM.")

        with self._get_db() as db:
            existing = db.query(TimeSlot).filter(
                TimeSlot.day_of_week == day_of_week,
                TimeSlot.period_index == period_index
            ).first()

            if existing:
                raise ValueError("Já existe um período configurado para este dia com este índice.")

            new_slot = TimeSlot(
                day_of_week=day_of_week,
                period_index=period_index,
                start_time=start,
                end_time=end
            )
            db.add(new_slot)
            db.flush()
            db.refresh(new_slot)
            return {
                "id": new_slot.id,
                "day_of_week": new_slot.day_of_week,
                "period_index": new_slot.period_index,
                "start_time": new_slot.start_time.strftime("%H:%M"),
                "end_time": new_slot.end_time.strftime("%H:%M")
            }

    def get_time_slots(self, day_of_week: int = None) -> list[dict]:
        """Retorna todos os slots de tempo, opcionalmente filtrados por dia."""
        with self._get_db() as db:
            query = db.query(TimeSlot)
            if day_of_week is not None:
                query = query.filter(TimeSlot.day_of_week == day_of_week)

            # Ordena por dia e depois por índice
            slots = query.order_by(TimeSlot.day_of_week, TimeSlot.period_index).all()

            return [{
                "id": s.id,
                "day_of_week": s.day_of_week,
                "period_index": s.period_index,
                "start_time": s.start_time.strftime("%H:%M"),
                "end_time": s.end_time.strftime("%H:%M")
            } for s in slots]

    def delete_time_slot(self, slot_id: int):
        with self._get_db() as db:
            # Note: Cascade delete handled by DB if properly set up, but let's be explicit
            db.query(WeeklySchedule).filter(WeeklySchedule.time_slot_id == slot_id).delete()
            db.query(TimeSlot).filter(TimeSlot.id == slot_id).delete()

    def create_schedule_assignment(self, time_slot_id: int, class_subject_id: int) -> dict | None:
        """Aloca uma disciplina de uma turma a um slot de tempo."""
        with self._get_db() as db:
            # Remove anterior se existir (sobrescreve)
            existing = db.query(WeeklySchedule).filter(WeeklySchedule.time_slot_id == time_slot_id).first()
            if existing:
                db.delete(existing)
                db.flush()

            assignment = WeeklySchedule(time_slot_id=time_slot_id, class_subject_id=class_subject_id)
            db.add(assignment)
            db.flush()
            db.refresh(assignment)
            return {"id": assignment.id}

    def get_full_schedule_grid(self) -> dict:
        """
        Retorna a grade completa combinando Slots e Assignments.
        Estrutura otimizada para a UI renderizar o grid.
        Retorno: { day_int: [ { slot_data, assignment_data }, ... ] }
        """
        with self._get_db() as db:
            # Query Slots joined with WeeklySchedule, ClassSubject, Class, and Course
            results = (db.query(TimeSlot, WeeklySchedule, ClassSubject, Class, Course)
                       .outerjoin(WeeklySchedule, TimeSlot.id == WeeklySchedule.time_slot_id)
                       .outerjoin(ClassSubject, WeeklySchedule.class_subject_id == ClassSubject.id)
                       .outerjoin(Class, ClassSubject.class_id == Class.id)
                       .outerjoin(Course, ClassSubject.course_id == Course.id)
                       .order_by(TimeSlot.day_of_week, TimeSlot.period_index)
                       .all())

            grid = {}
            for slot, schedule, subj, cls, course in results:
                day = slot.day_of_week
                if day not in grid:
                    grid[day] = []

                item = {
                    "slot_id": slot.id,
                    "period_index": slot.period_index,
                    "start_time": slot.start_time.strftime("%H:%M"),
                    "end_time": slot.end_time.strftime("%H:%M"),
                    "assignment": None
                }

                if schedule and cls and course:
                    item["assignment"] = {
                        "class_id": cls.id,
                        "class_name": cls.name,
                        "course_name": course.course_name,
                        "class_subject_id": subj.id
                    }

                grid[day].append(item)

            return grid

    def get_lesson_for_schedule(self, class_subject_id: int, date_val: date) -> dict | None:
        """Verifica se existe uma aula registrada para a disciplina na data específica."""
        with self._get_db() as db:
            lesson = db.query(Lesson).filter(
                Lesson.class_subject_id == class_subject_id,
                Lesson.date == date_val
            ).first()

            if lesson:
                return {"id": lesson.id, "title": lesson.title, "content": lesson.content, "date": lesson.date.isoformat(), "bncc_codes": lesson.bncc_codes}
            return None

    # --- BNCC Tracking ---

    def get_bncc_coverage(self, class_subject_id: int) -> dict:
        """Calcula a cobertura de habilidades BNCC para uma disciplina de turma."""
        with self._get_db() as db:
            # Carrega a disciplina e o curso
            subject = db.query(ClassSubject).options(joinedload(ClassSubject.course)).filter(ClassSubject.id == class_subject_id).first()
            if not subject:
                return {}

            # 1. Expected Skills
            expected_raw = subject.course.bncc_expected or ""
            # Normaliza: Split por vírgula, strip, upper, remove vazios
            expected_set = {code.strip().upper() for code in expected_raw.split(',') if code.strip()}

            # 2. Covered in Lessons
            lessons = db.query(Lesson).filter(Lesson.class_subject_id == class_subject_id).all()
            covered_lessons_set = set()
            for l in lessons:
                if l.bncc_codes:
                    codes = {code.strip().upper() for code in l.bncc_codes.split(',') if code.strip()}
                    covered_lessons_set.update(codes)

            # 3. Covered in Assessments
            assessments = db.query(Assessment).filter(Assessment.class_subject_id == class_subject_id).all()
            covered_assessments_set = set()
            for a in assessments:
                if a.bncc_codes:
                    codes = {code.strip().upper() for code in a.bncc_codes.split(',') if code.strip()}
                    covered_assessments_set.update(codes)

            # Total Covered (Union)
            total_covered = covered_lessons_set.union(covered_assessments_set)

            # Missing
            missing = expected_set - total_covered

            # Relevant Covered (Intersection with Expected)
            relevant_covered = total_covered.intersection(expected_set)

            return {
                "expected": sorted(list(expected_set)),
                "covered_lessons": sorted(list(covered_lessons_set)),
                "covered_assessments": sorted(list(covered_assessments_set)),
                "total_covered": sorted(list(total_covered)),
                "missing": sorted(list(missing)),
                "coverage_percentage": (len(relevant_covered) / len(expected_set) * 100) if expected_set else 0.0
            }
