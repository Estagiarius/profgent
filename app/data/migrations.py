from sqlalchemy import text, inspect
import logging

def migrate_database(engine):
    """
    Checks for necessary schema migrations and applies them.
    Currently handles:
    1. Adding 'grading_period' to the 'assessments' table.
    2. Adding performance indexes to the 'grades' table.
    3. Adding performance indexes to the 'incidents' table.
    4. Adding performance indexes to 'class_enrollments' and 'class_subjects'.
    5. Adding performance indexes to 'attendance', 'assessments', and 'lessons'.
    """
    try:
        inspector = inspect(engine)

        # --- 1. Migration for 'grading_period' in 'assessments' ---
        columns = [col['name'] for col in inspector.get_columns('assessments')]

        if 'grading_period' not in columns:
            logging.info("Applying migration: Adding 'grading_period' column to 'assessments' table.")
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE assessments ADD COLUMN grading_period INTEGER DEFAULT 1 NOT NULL"))
            logging.info("Migration applied successfully.")
        else:
            logging.info("Schema check: 'grading_period' column already exists.")

        # --- 2. Migration for Indexes on 'grades' table ---
        indexes_grades = inspector.get_indexes('grades')
        has_grade_index = lambda col_name: any(ix['column_names'] == [col_name] for ix in indexes_grades)

        with engine.begin() as conn:
            if not has_grade_index('student_id'):
                logging.info("Applying migration: Adding index to 'grades.student_id'.")
                conn.execute(text("CREATE INDEX ix_grades_student_id ON grades (student_id)"))
                logging.info("Index 'ix_grades_student_id' created.")
            else:
                logging.info("Schema check: Index on 'grades.student_id' already exists.")

            if not has_grade_index('assessment_id'):
                logging.info("Applying migration: Adding index to 'grades.assessment_id'.")
                conn.execute(text("CREATE INDEX ix_grades_assessment_id ON grades (assessment_id)"))
                logging.info("Index 'ix_grades_assessment_id' created.")
            else:
                logging.info("Schema check: Index on 'grades.assessment_id' already exists.")

        # --- 3. Migration for Indexes on 'incidents' table ---
        indexes_incidents = inspector.get_indexes('incidents')
        has_incident_index = lambda col_name: any(ix['column_names'] == [col_name] for ix in indexes_incidents)

        with engine.begin() as conn:
            if not has_incident_index('class_id'):
                logging.info("Applying migration: Adding index to 'incidents.class_id'.")
                conn.execute(text("CREATE INDEX ix_incidents_class_id ON incidents (class_id)"))
                logging.info("Index 'ix_incidents_class_id' created.")
            else:
                logging.info("Schema check: Index on 'incidents.class_id' already exists.")

            if not has_incident_index('student_id'):
                logging.info("Applying migration: Adding index to 'incidents.student_id'.")
                conn.execute(text("CREATE INDEX ix_incidents_student_id ON incidents (student_id)"))
                logging.info("Index 'ix_incidents_student_id' created.")
            else:
                logging.info("Schema check: Index on 'incidents.student_id' already exists.")

        # --- 4. Migration for Indexes on 'class_enrollments' and 'class_subjects' ---
        # Checks if secondary foreign keys are indexed for reverse lookups.

        # ClassEnrollment
        indexes_enrollments = inspector.get_indexes('class_enrollments')
        has_enroll_index = lambda col_name: any(ix['column_names'] == [col_name] for ix in indexes_enrollments)

        with engine.begin() as conn:
            if not has_enroll_index('student_id'):
                logging.info("Applying migration: Adding index to 'class_enrollments.student_id'.")
                conn.execute(text("CREATE INDEX ix_class_enrollments_student_id ON class_enrollments (student_id)"))
                logging.info("Index 'ix_class_enrollments_student_id' created.")
            else:
                 logging.info("Schema check: Index on 'class_enrollments.student_id' already exists.")

        # ClassSubject
        indexes_subjects = inspector.get_indexes('class_subjects')
        has_subject_index = lambda col_name: any(ix['column_names'] == [col_name] for ix in indexes_subjects)

        with engine.begin() as conn:
             if not has_subject_index('course_id'):
                logging.info("Applying migration: Adding index to 'class_subjects.course_id'.")
                conn.execute(text("CREATE INDEX ix_class_subjects_course_id ON class_subjects (course_id)"))
                logging.info("Index 'ix_class_subjects_course_id' created.")
             else:
                 logging.info("Schema check: Index on 'class_subjects.course_id' already exists.")

        # --- 5. Migration for Attendance, Assessment, Lesson ---

        # Attendance: student_id
        indexes_attendance = inspector.get_indexes('attendance')
        has_att_index = lambda col_name: any(ix['column_names'] == [col_name] for ix in indexes_attendance)

        with engine.begin() as conn:
            if not has_att_index('student_id'):
                logging.info("Applying migration: Adding index to 'attendance.student_id'.")
                conn.execute(text("CREATE INDEX ix_attendance_student_id ON attendance (student_id)"))
                logging.info("Index 'ix_attendance_student_id' created.")
            else:
                 logging.info("Schema check: Index on 'attendance.student_id' already exists.")

        # Assessment: class_subject_id
        indexes_assessments = inspector.get_indexes('assessments')
        has_ass_index = lambda col_name: any(ix['column_names'] == [col_name] for ix in indexes_assessments)

        with engine.begin() as conn:
             if not has_ass_index('class_subject_id'):
                logging.info("Applying migration: Adding index to 'assessments.class_subject_id'.")
                conn.execute(text("CREATE INDEX ix_assessments_class_subject_id ON assessments (class_subject_id)"))
                logging.info("Index 'ix_assessments_class_subject_id' created.")
             else:
                 logging.info("Schema check: Index on 'assessments.class_subject_id' already exists.")

        # Lesson: class_subject_id
        indexes_lessons = inspector.get_indexes('lessons')
        has_lesson_index = lambda col_name: any(ix['column_names'] == [col_name] for ix in indexes_lessons)

        with engine.begin() as conn:
             if not has_lesson_index('class_subject_id'):
                logging.info("Applying migration: Adding index to 'lessons.class_subject_id'.")
                conn.execute(text("CREATE INDEX ix_lessons_class_subject_id ON lessons (class_subject_id)"))
                logging.info("Index 'ix_lessons_class_subject_id' created.")
             else:
                 logging.info("Schema check: Index on 'lessons.class_subject_id' already exists.")

    except Exception as e:
        logging.error(f"Migration failed: {e}")
        raise e
