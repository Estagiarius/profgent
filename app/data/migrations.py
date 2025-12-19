from sqlalchemy import text, inspect
import logging

def migrate_database(engine):
    """
    Checks for necessary schema migrations and applies them.
    Currently handles:
    1. Adding 'grading_period' to the 'assessments' table.
    2. Adding performance indexes to the 'grades' table.
    3. Adding performance indexes to the 'incidents' table.
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

    except Exception as e:
        logging.error(f"Migration failed: {e}")
        raise e
