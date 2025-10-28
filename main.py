from app.ui.main_app import MainApp
from app.data.database import init_db

def main():
    # Initialize the database
    init_db()

    # Create and run the application
    app = MainApp()
    app.mainloop()

if __name__ == "__main__":
    main()
