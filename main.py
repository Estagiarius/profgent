from app.ui.main_app import MainApp
from alembic.config import Config
from alembic import command
import os

def run_migrations():
    """Applies any pending Alembic migrations."""
    # Alembic needs to be run from the project root to find alembic.ini
    # This ensures that the script can be run from anywhere.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    alembic_cfg = Config("alembic.ini")
    print("Running database migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Migrations complete.")

def main():
    # Ensure the database schema is up-to-date before running the app
    run_migrations()

    # Create and run the application
    app = MainApp()
    app.mainloop()

if __name__ == "__main__":
    main()
