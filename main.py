from app.ui.main_app import MainApp
from alembic.config import Config
from alembic import command
import os
import sys
import sqlite3

def check_and_prepare_database():
    """
    Ensures the database is compatible. If an old schema is detected
    (missing the 'classes' table), the old database file is deleted.
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, "academic_management.db")

    if os.path.exists(db_path):
        try:
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classes';")
            if cur.fetchone() is None:
                print("Old database schema detected. Deleting for recreation.")
                con.close()
                os.remove(db_path)
            else:
                con.close()
        except Exception as e:
            print(f"Database check failed, deleting for safety: {e}")
            os.remove(db_path)

def run_migrations():
    """Applies any pending Alembic migrations."""
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))
        alembic_ini_path = os.path.join(project_root, "alembic.ini")

        if not os.path.exists(alembic_ini_path):
            print(f"Error: alembic.ini not found at {alembic_ini_path}")
            sys.exit(1)

        alembic_cfg = Config(alembic_ini_path)
        alembic_cfg.set_main_option("script_location", project_root)

        print("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("Migrations complete.")
    except Exception as e:
        print(f"FATAL: Database migration failed: {e}")
        sys.exit(1)

def main():
    check_and_prepare_database()
    run_migrations()

    app = MainApp()
    app.mainloop()

if __name__ == "__main__":
    main()
