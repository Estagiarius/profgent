import customtkinter as ctk
from app.services import data_service
from app.ui.views.add_dialog import AddDialog

class ClassManagementView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Class Management", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.class_list_frame = ctk.CTkFrame(self)
        self.class_list_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.class_list_frame.grid_columnconfigure(2, weight=1)

        self.add_class_button = ctk.CTkButton(self, text="Add New Class", command=self.add_class_popup)
        self.add_class_button.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")

        self.populate_class_list()

    def populate_class_list(self):
        for widget in self.class_list_frame.winfo_children():
            widget.destroy()

        headers = ["Class Name", "Course", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.class_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        classes = data_service.get_all_classes()
        for i, class_ in enumerate(classes, start=1):
            ctk.CTkLabel(self.class_list_frame, text=class_.name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.class_list_frame, text=class_.course.course_name).grid(row=i, column=1, padx=10, pady=5, sticky="w")

            view_button = ctk.CTkButton(self.class_list_frame, text="View Details", command=lambda c=class_.id: self.view_class_details(c))
            view_button.grid(row=i, column=2, padx=10, pady=5, sticky="e")

    def view_class_details(self, class_id):
        self.main_app.show_view("class_detail", class_id=class_id)

    def add_class_popup(self):
        courses = data_service.get_all_courses()
        course_names = [c.course_name for c in courses]

        if not course_names:
            print("Error: No courses available. Please add a course first.")
            return

        def save_callback(data):
            class_name = data["name"]
            selected_course_name = data["course"]

            selected_course = next((c for c in courses if c.course_name == selected_course_name), None)

            if class_name and selected_course:
                data_service.create_class(name=class_name, course_id=selected_course.id)
                self.populate_class_list()

        fields = {"name": "Class Name"}
        dropdowns = {"course": ("Course", course_names)}

        AddDialog(self, "Add New Class", fields=fields, dropdowns=dropdowns, save_callback=save_callback)


    def on_show(self, _=None):
        self.populate_class_list()
