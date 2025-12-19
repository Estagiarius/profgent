from sqlalchemy import create_engine, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = "sqlite:///academic_management.db"

def run_migration():
    engine = create_engine(DB_URL)

    with engine.connect() as conn:
        # 1. Check Course table
        try:
            # Check if column exists
            result = conn.execute(text("PRAGMA table_info(courses)")).fetchall()
            columns = [row[1] for row in result]
            if 'bncc_expected' not in columns:
                logger.info("Adding bncc_expected to courses...")
                conn.execute(text("ALTER TABLE courses ADD COLUMN bncc_expected TEXT"))
            else:
                logger.info("courses.bncc_expected already exists.")
        except Exception as e:
            logger.error(f"Error updating courses: {e}")

        # 2. Check Lesson table
        try:
            result = conn.execute(text("PRAGMA table_info(lessons)")).fetchall()
            columns = [row[1] for row in result]
            if 'bncc_codes' not in columns:
                logger.info("Adding bncc_codes to lessons...")
                conn.execute(text("ALTER TABLE lessons ADD COLUMN bncc_codes TEXT"))
            else:
                logger.info("lessons.bncc_codes already exists.")
        except Exception as e:
            logger.error(f"Error updating lessons: {e}")

        # 3. Check Assessment table
        try:
            result = conn.execute(text("PRAGMA table_info(assessments)")).fetchall()
            columns = [row[1] for row in result]
            if 'bncc_codes' not in columns:
                logger.info("Adding bncc_codes to assessments...")
                conn.execute(text("ALTER TABLE assessments ADD COLUMN bncc_codes TEXT"))
            else:
                logger.info("assessments.bncc_codes already exists.")
        except Exception as e:
            logger.error(f"Error updating assessments: {e}")

    logger.info("Migration complete.")

if __name__ == "__main__":
    run_migration()
