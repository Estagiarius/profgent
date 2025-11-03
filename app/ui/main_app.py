import asyncio
import customtkinter as ctk
from queue import Queue, Empty
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.grade_entry_view import GradeEntryView
from app.ui.views.assistant_view import AssistantView
from app.ui.views.settings_view import SettingsView
from app.ui.views.management_view import ManagementView
from app.ui.views.class_management_view import ClassManagementView
from app.ui.views.class_detail_view import ClassDetailView
from app.ui.views.grade_grid_view import GradeGridView

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Academic Management")
        self.geometry("1100x800")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.loop = asyncio.get_event_loop()

        self.async_queue = Queue()
        self._process_queue()

        self.update_asyncio()

        # Set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(8, weight=1) # Adjusted for the new button

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="Navigation",
                                                  font=ctk.CTkFont(size=20, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Add navigation buttons
        self.dashboard_button = ctk.CTkButton(self.navigation_frame, text="Dashboard", command=lambda: self.show_view("dashboard"))
        self.dashboard_button.grid(row=1, column=0, padx=20, pady=10)

        self.management_button = ctk.CTkButton(self.navigation_frame, text="Data Management", command=lambda: self.show_view("management"))
        self.management_button.grid(row=2, column=0, padx=20, pady=10)

        self.class_management_button = ctk.CTkButton(self.navigation_frame, text="Class Management", command=lambda: self.show_view("class_management"))
        self.class_management_button.grid(row=3, column=0, padx=20, pady=10)

        self.grade_entry_button = ctk.CTkButton(self.navigation_frame, text="Grade Entry", command=lambda: self.show_view("grade_entry"))
        self.grade_entry_button.grid(row=4, column=0, padx=20, pady=10)

        self.grade_grid_button = ctk.CTkButton(self.navigation_frame, text="Grade Grid", command=lambda: self.show_view("grade_grid"))
        self.grade_grid_button.grid(row=5, column=0, padx=20, pady=10)

        self.assistant_button = ctk.CTkButton(self.navigation_frame, text="AI Assistant", command=lambda: self.show_view("assistant"))
        self.assistant_button.grid(row=6, column=0, padx=20, pady=10)

        self.settings_button = ctk.CTkButton(self.navigation_frame, text="Settings", command=lambda: self.show_view("settings"))
        self.settings_button.grid(row=7, column=0, padx=20, pady=10)


        # Create main content frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Create views and store them in a dictionary
        self.views = {
            "dashboard": DashboardView(self.main_frame),
            "grade_entry": GradeEntryView(self.main_frame),
            "grade_grid": GradeGridView(self.main_frame),
            "management": ManagementView(self.main_frame),
            "class_management": ClassManagementView(self.main_frame, self),
            "class_detail": ClassDetailView(self.main_frame, self),
            "assistant": AssistantView(self.main_frame),
            "settings": SettingsView(self.main_frame, self)
        }

        # Show the dashboard view by default
        self.show_view("dashboard")

    def _process_queue(self):
        try:
            # Get a task from the queue without blocking
            callable, args = self.async_queue.get_nowait()
            callable(*args)
        except Empty:
            pass  # Do nothing if the queue is empty
        finally:
            # Schedule the next check
            self.after(100, self._process_queue)

    def show_view(self, view_name, **kwargs):
        # Hide all views
        for view in self.views.values():
            view.grid_forget()

        # Show the requested view
        selected_view = self.views[view_name]
        selected_view.grid(row=0, column=0, sticky="nsew")

        # Trigger the 'on_show' event if the view has one
        if hasattr(selected_view, 'on_show'):
            selected_view.on_show(**kwargs)

    def update_asyncio(self):
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()
        self.after(1, self.update_asyncio)

    def on_closing(self):
        tasks = asyncio.all_tasks(loop=self.loop)
        for task in tasks:
            task.cancel()

        async def gather_tasks():
            await asyncio.gather(*tasks, return_exceptions=True)

        self.loop.run_until_complete(gather_tasks())
        self.loop.close()
        self.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
