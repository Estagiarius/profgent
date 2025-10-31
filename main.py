from app.ui.main_app import MainApp

def main():
    # The database is now managed by Alembic migrations.
    # init_db() is no longer needed on startup.

    # Create and run the application
    app = MainApp()
    app.mainloop()

if __name__ == "__main__":
    main()
