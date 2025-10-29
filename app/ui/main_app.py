import customtkinter as ctk
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.grade_entry_view import GradeEntryView
from app.ui.views.assistant_view import AssistantView
from app.ui.views.settings_view import SettingsView
from app.ui.views.management_view import ManagementView

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Academic Management")
        self.geometry("1100x800")

        # Set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(6, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="Navigation",
                                                  font=ctk.CTkFont(size=20, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.dashboard_button = ctk.CTkButton(self.navigation_frame, text="Dashboard",
                                               command=self.dashboard_button_event)
        self.dashboard_button.grid(row=1, column=0, padx=20, pady=10)

        self.grade_entry_button = ctk.CTkButton(self.navigation_frame, text="Grade Entry",
                                                 command=self.grade_entry_button_event)
        self.grade_entry_button.grid(row=2, column=0, padx=20, pady=10)

        self.management_button = ctk.CTkButton(self.navigation_frame, text="Management",
                                               command=self.management_button_event)
        self.management_button.grid(row=3, column=0, padx=20, pady=10)

        self.assistant_button = ctk.CTkButton(self.navigation_frame, text="AI Assistant",
                                               command=self.assistant_button_event)
        self.assistant_button.grid(row=4, column=0, padx=20, pady=10)

        self.settings_button = ctk.CTkButton(self.navigation_frame, text="Settings",
                                              command=self.settings_button_event)
        self.settings_button.grid(row=5, column=0, padx=20, pady=10)

        # Create main content frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)


        # Create views and store them in a dictionary
        self.views = {
            "dashboard": DashboardView(self.main_frame),
            "grade_entry": GradeEntryView(self.main_frame),
            "management": ManagementView(self.main_frame),
            "assistant": AssistantView(self.main_frame),
            "settings": SettingsView(self.main_frame)
        }

        # Show the dashboard view by default
        self.show_view("dashboard")


    def show_view(self, view_name):
        # Hide all views
        for view in self.views.values():
            view.grid_forget()

        # Show the requested view
        selected_view = self.views[view_name]
        selected_view.grid(row=0, column=0, sticky="nsew")

        # Trigger the 'on_show' event if the view has one
        if hasattr(selected_view, 'on_show'):
            selected_view.on_show(None)


    def dashboard_button_event(self):
        self.show_view("dashboard")

    def grade_entry_button_event(self):
        self.show_view("grade_entry")

    def management_button_event(self):
        self.show_view("management")

    def assistant_button_event(self):
        self.show_view("assistant")

    def settings_button_event(self):
        self.show_view("settings")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
