from sqlalchemy import text, inspect
import logging

def migrate_database(engine):
    """
    Checks for necessary schema migrations and applies them.
    Currently handles adding 'grading_period' to the 'assessments' table.
    """
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('assessments')]

        if 'grading_period' not in columns:
            logging.info("Applying migration: Adding 'grading_period' column to 'assessments' table.")
            with engine.begin() as conn:
                # Add the column with a default value of 1 (1st Bimester)
                conn.execute(text("ALTER TABLE assessments ADD COLUMN grading_period INTEGER DEFAULT 1 NOT NULL"))
            logging.info("Migration applied successfully.")
        else:
            logging.info("Schema check: 'grading_period' column already exists.")

    except Exception as e:
        logging.error(f"Migration failed: {e}")
        raise e
