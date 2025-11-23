import sys
import os
from unittest.mock import MagicMock

# Mock tkinter and customtkinter
sys.modules['tkinter'] = MagicMock()
sys.modules['customtkinter'] = MagicMock()

# Don't mock PIL as it is used by matplotlib and works headless.

try:
    print("Step 1: Importing main...")
    import main
    print("Success: main imported.")

    print("Step 2: Initializing Database...")
    main.initialize_database()
    print("Success: Database initialized.")

    print("Step 3: Instantiating DataService...")
    from app.services.data_service import DataService
    ds = DataService()
    print("Success: DataService instantiated.")

    print("Step 4: Instantiating AssistantService...")
    from app.services.assistant_service import AssistantService
    as_ = AssistantService()
    print("Success: AssistantService instantiated.")

    print("Step 5: Importing and Instantiating MainApp...")
    from app.ui.main_app import MainApp
    app = MainApp(ds, as_)
    print("Success: MainApp instantiated.")

    print("Startup verification PASSED.")

except Exception as e:
    print(f"Startup verification FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
