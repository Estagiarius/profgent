from app.ui.main_app import MainApp
from app.data.database import engine, Base
# Import all models to ensure they are registered with SQLAlchemy's metadata
from app.models import student, course, class_, class_enrollment, assessment, grade
import os

def initialize_database():
    """Creates the database and tables if they don't already exist."""
    db_path = engine.url.database
    if not os.path.exists(db_path):
        print("Database not found. Creating a new database and all tables...")
        # The 'Base' object contains metadata about all our tables.
        # create_all checks for table existence before creating, so it's safe.
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully.")
    else:
        print("Database already exists. Skipping creation.")


def main():
    initialize_database()

    app = MainApp()
    app.mainloop()

if __name__ == "__main__":
    main()
