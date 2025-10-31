from app.ui.main_app import MainApp
from alembic.config import Config
from alembic import command
import os
import sys
import sqlite3

def run_migrations():
    """Applies any pending Alembic migrations."""
    try:
        # Get the absolute path to the project root directory
        project_root = os.path.dirname(os.path.abspath(__file__))

        # Alembic config file path
        alembic_ini_path = os.path.join(project_root, "alembic.ini")

        if not os.path.exists(alembic_ini_path):
            print(f"Error: alembic.ini not found at {alembic_ini_path}")
            sys.exit(1)

        alembic_cfg = Config(alembic_ini_path)

        # Tell Alembic where to find its env.py and versions/ directory
        alembic_script_location = os.path.join(project_root, "alembic")
        alembic_cfg.set_main_option("script_location", alembic_script_location)

        print("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("Migrations complete.")
    except Exception as e:
        print(f"FATAL: Database migration failed: {e}")
        sys.exit(1)

def check_and_prepare_database():
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
            if 'con' in locals() and con:
                con.close()
            os.remove(db_path)

def main():
    check_and_prepare_database()
    run_migrations()

    app = MainApp()
    app.mainloop()

if __name__ == "__main__":
    main()
