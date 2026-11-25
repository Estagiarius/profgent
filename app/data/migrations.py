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
from sqlalchemy import text, inspect
import logging


def migrate_database(engine):
    """
    Verifica e aplica migrações necessárias no schema do banco de dados de forma idempotente.
    Atualmente gerencia:
    1. Adição da coluna 'grading_period' na tabela 'assessments'.
    2. Adição das colunas da BNCC em 'courses', 'lessons' e 'assessments'.
    3. Criação idempotente de índices de performance em 'grades', 'incidents',
       'class_enrollments', 'class_subjects', 'attendance', 'assessments',
       'lessons' e 'weekly_schedule'.
    """
    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())

        # --- 1. Migrações de colunas em 'assessments' ---
        if 'assessments' in existing_tables:
            columns_assessments = {col['name'] for col in inspector.get_columns('assessments')}

            if 'grading_period' not in columns_assessments:
                logging.info("Aplicando migração: adicionando coluna 'grading_period' na tabela 'assessments'.")
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE assessments ADD COLUMN grading_period INTEGER DEFAULT 1 NOT NULL"))
                logging.info("Migração 'grading_period' aplicada com sucesso.")

            if 'bncc_codes' not in columns_assessments:
                logging.info("Aplicando migração: adicionando coluna 'bncc_codes' na tabela 'assessments'.")
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE assessments ADD COLUMN bncc_codes TEXT"))
                logging.info("Migração 'assessments.bncc_codes' aplicada com sucesso.")

        # --- 2. Migrações de colunas BNCC em 'courses' e 'lessons' ---
        if 'courses' in existing_tables:
            columns_courses = {col['name'] for col in inspector.get_columns('courses')}
            if 'bncc_expected' not in columns_courses:
                logging.info("Aplicando migração: adicionando coluna 'bncc_expected' na tabela 'courses'.")
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE courses ADD COLUMN bncc_expected TEXT"))
                logging.info("Migração 'courses.bncc_expected' aplicada com sucesso.")

        if 'lessons' in existing_tables:
            columns_lessons = {col['name'] for col in inspector.get_columns('lessons')}
            if 'bncc_codes' not in columns_lessons:
                logging.info("Aplicando migração: adicionando coluna 'bncc_codes' na tabela 'lessons'.")
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE lessons ADD COLUMN bncc_codes TEXT"))
                logging.info("Migração 'lessons.bncc_codes' aplicada com sucesso.")

        # --- 3. Índices de performance (idempotentes via IF NOT EXISTS) ---
        index_definitions = [
            ('grades', 'ix_grades_student_id', 'student_id'),
            ('grades', 'ix_grades_assessment_id', 'assessment_id'),
            ('incidents', 'ix_incidents_class_id', 'class_id'),
            ('incidents', 'ix_incidents_student_id', 'student_id'),
            ('class_enrollments', 'ix_class_enrollments_student_id', 'student_id'),
            ('class_subjects', 'ix_class_subjects_course_id', 'course_id'),
            ('attendance', 'ix_attendance_student_id', 'student_id'),
            ('assessments', 'ix_assessments_class_subject_id', 'class_subject_id'),
            ('lessons', 'ix_lessons_class_subject_id', 'class_subject_id'),
            ('weekly_schedule', 'ix_weekly_schedule_class_subject_id', 'class_subject_id'),
        ]

        with engine.begin() as conn:
            for table_name, index_name, column_name in index_definitions:
                if table_name in existing_tables:
                    conn.execute(
                        text(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_name})")
                    )

        logging.info("Verificação e migração do banco de dados concluídas com sucesso.")
    except Exception as e:
        logging.error(f"Falha na migração do banco de dados: {e}")
        raise
