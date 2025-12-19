from sqlalchemy import text, inspect
import logging

def migrate_database(engine):
    """
    Checks for necessary schema migrations and applies them.
    Currently handles:
    1. Adding 'grading_period' to the 'assessments' table.
    2. Adding performance indexes to the 'grades' table.
    """
    try:
        inspector = inspect(engine)

        # --- 1. Migration for 'grading_period' in 'assessments' ---
        # Checks if the 'assessments' table has the 'grading_period' column.
        columns = [col['name'] for col in inspector.get_columns('assessments')]

        if 'grading_period' not in columns:
            logging.info("Applying migration: Adding 'grading_period' column to 'assessments' table.")
            with engine.begin() as conn:
                # Add the column with a default value of 1 (1st Bimester)
                conn.execute(text("ALTER TABLE assessments ADD COLUMN grading_period INTEGER DEFAULT 1 NOT NULL"))
            logging.info("Migration applied successfully.")
        else:
            logging.info("Schema check: 'grading_period' column already exists.")

        # --- 2. Migration for Indexes on 'grades' table ---
        # Checks if 'student_id' and 'assessment_id' are indexed in the 'grades' table.
        # This improves performance for global statistics and student grade lookups.

        # Get all indexes for the 'grades' table
        indexes = inspector.get_indexes('grades')

        # Helper lambda to check if an index exists for a specific list of columns
        has_index_on = lambda col_name: any(ix['column_names'] == [col_name] for ix in indexes)

        with engine.begin() as conn:
            if not has_index_on('student_id'):
                logging.info("Applying migration: Adding index to 'grades.student_id'.")
                # Name the index explicitly to match standard conventions (ix_table_column)
                conn.execute(text("CREATE INDEX ix_grades_student_id ON grades (student_id)"))
                logging.info("Index 'ix_grades_student_id' created.")
            else:
                logging.info("Schema check: Index on 'grades.student_id' already exists.")

            if not has_index_on('assessment_id'):
                logging.info("Applying migration: Adding index to 'grades.assessment_id'.")
                conn.execute(text("CREATE INDEX ix_grades_assessment_id ON grades (assessment_id)"))
                logging.info("Index 'ix_grades_assessment_id' created.")
            else:
                logging.info("Schema check: Index on 'grades.assessment_id' already exists.")

    except Exception as e:
        logging.error(f"Migration failed: {e}")
        raise e
