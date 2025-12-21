
import customtkinter as ctk
import sys
import os

# Add repo root to path
sys.path.append(os.getcwd())

from app.ui.widgets.scrollable_canvas_frame import ScrollableCanvasFrame

def test_widget_init():
    try:
        app = ctk.CTk()
        # This triggers the problematic __init__ -> super().__init__ -> _apply_appearance_mode cycle
        widget = ScrollableCanvasFrame(app)
        print("Widget initialized successfully.")

        # Test scroll binding on internal canvas
        if hasattr(widget, "canvas"):
            print("Canvas attribute exists.")

        app.destroy()
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_widget_init()
