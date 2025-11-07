import customtkinter as ctk
from tkinter import filedialog
import csv
from datetime import date, datetime
from app.services import data_service
from app.ui.views.add_dialog import AddDialog
from app.ui.views.edit_dialog import EditDialog
from customtkinter import CTkInputDialog

class ClassDetailView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.class_id = None
        self.editing_lesson_id = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Class Details", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.tab_view.add("Students")
        self.tab_view.add("Assessments")

        # --- Students Tab ---
        students_tab = self.tab_view.tab("Students")
        students_tab.grid_rowconfigure(1, weight=1)
        students_tab.grid_columnconfigure(0, weight=1)

        self.options_frame = ctk.CTkFrame(students_tab)
        self.options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.show_active_only_checkbox = ctk.CTkCheckBox(self.options_frame, text="Show Active Students Only", command=self.populate_student_list)
        self.show_active_only_checkbox.pack(side="left", padx=10, pady=5)
        self.show_active_only_checkbox.select()

        self.student_list_frame = ctk.CTkScrollableFrame(students_tab)
        self.student_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.controls_frame = ctk.CTkFrame(students_tab)
        self.controls_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.controls_frame.grid_columnconfigure(0, weight=1)
        self.controls_frame.grid_columnconfigure(1, weight=1)

        self.enroll_student_button = ctk.CTkButton(self.controls_frame, text="Enroll Student", command=self.enroll_student_popup)
        self.enroll_student_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.import_button = ctk.CTkButton(self.controls_frame, text="Import Students (.csv)", command=self.import_students)
        self.import_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # --- Assessments Tab ---
        assessments_tab = self.tab_view.tab("Assessments")
        assessments_tab.grid_rowconfigure(0, weight=1)
        assessments_tab.grid_columnconfigure(0, weight=1)

        self.assessment_list_frame = ctk.CTkScrollableFrame(assessments_tab)
        self.assessment_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.add_assessment_button = ctk.CTkButton(assessments_tab, text="Add New Assessment", command=self.add_assessment_popup)
        self.add_assessment_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Lessons Tab ---
        lessons_tab = self.tab_view.tab("Lessons")
        lessons_tab.grid_rowconfigure(0, weight=1)
        lessons_tab.grid_columnconfigure(0, weight=1)

        # Container for list and editor to toggle visibility
        self.lesson_container = ctk.CTkFrame(lessons_tab)
        self.lesson_container.grid(row=0, column=0, sticky="nsew")
        self.lesson_container.grid_rowconfigure(0, weight=1)
        self.lesson_container.grid_columnconfigure(0, weight=1)

        # --- Lesson List View ---
        self.lesson_list_view = ctk.CTkFrame(self.lesson_container)
        self.lesson_list_view.grid(row=0, column=0, sticky="nsew")
        self.lesson_list_view.grid_rowconfigure(0, weight=1)
        self.lesson_list_view.grid_columnconfigure(0, weight=1)

        self.lesson_list_frame = ctk.CTkScrollableFrame(self.lesson_list_view)
        self.lesson_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.add_lesson_button = ctk.CTkButton(self.lesson_list_view, text="Add New Lesson", command=self.show_lesson_editor)
        self.add_lesson_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Lesson Editor View ---
        self.lesson_editor_view = ctk.CTkFrame(self.lesson_container)
        self.lesson_editor_view.grid_rowconfigure(2, weight=1)
        self.lesson_editor_view.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.lesson_editor_view, text="Title:").grid(row=0, column=0, padx=(10,0), pady=10, sticky="w")
        self.lesson_editor_title_entry = ctk.CTkEntry(self.lesson_editor_view, placeholder_text="Lesson Title")
        self.lesson_editor_title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.lesson_editor_view, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=(10,0), pady=10, sticky="w")
        self.lesson_editor_date_entry = ctk.CTkEntry(self.lesson_editor_view)
        self.lesson_editor_date_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.lesson_editor_view, text="Content:").grid(row=2, column=0, padx=(10,0), pady=10, sticky="nw")
        self.lesson_editor_content_textbox = ctk.CTkTextbox(self.lesson_editor_view)
        self.lesson_editor_content_textbox.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        editor_buttons_frame = ctk.CTkFrame(self.lesson_editor_view)
        editor_buttons_frame.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        self.save_lesson_button = ctk.CTkButton(editor_buttons_frame, text="Save", command=self.save_lesson)
        self.save_lesson_button.pack(side="left", padx=5)

        self.cancel_lesson_button = ctk.CTkButton(editor_buttons_frame, text="Cancel", command=self.hide_lesson_editor)
        self.cancel_lesson_button.pack(side="left", padx=5)

        self.hide_lesson_editor() # Initially hidden

        # --- Incidents Tab ---
        incidents_tab = self.tab_view.tab("Incidents")
        incidents_tab.grid_rowconfigure(0, weight=1)
        incidents_tab.grid_columnconfigure(0, weight=1)

        self.incident_list_frame = ctk.CTkScrollableFrame(incidents_tab)
        self.incident_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.add_incident_button = ctk.CTkButton(incidents_tab, text="Add New Incident", command=self.add_incident_popup)
        self.add_incident_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    def add_incident_popup(self):
        if not self.class_id:
            return

        enrollments = data_service.get_enrollments_for_class(self.class_id)
        student_names = [f"{e.student.first_name} {e.student.last_name}" for e in enrollments]

        if not student_names:
            # TODO: Show a proper message dialog
            print("No students in this class to assign an incident to.")
            return

        def save_callback(data):
            student_name = data["student"]
            description = data["description"]

            selected_enrollment = next((e for e in enrollments if f"{e.student.first_name} {e.student.last_name}" == student_name), None)

            if selected_enrollment and description:
                data_service.create_incident(self.class_id, selected_enrollment.student.id, description, date.today())
                self.populate_incident_list()

        fields = {"description": "Description"}
        dropdowns = {"student": ("Student", student_names)}
        AddDialog(self, "Add New Incident", fields=fields, dropdowns=dropdowns, save_callback=save_callback)

    def populate_incident_list(self):
        for widget in self.incident_list_frame.winfo_children():
            widget.destroy()

        if not self.class_id:
            return

        incidents = data_service.get_incidents_for_class(self.class_id)

        headers = ["Student Name", "Date", "Description"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.incident_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, incident in enumerate(incidents, start=1):
            student_name = f"{incident.student.first_name} {incident.student.last_name}"
            ctk.CTkLabel(self.incident_list_frame, text=student_name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.incident_list_frame, text=str(incident.date)).grid(row=i, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.incident_list_frame, text=incident.description, wraplength=400, justify="left").grid(row=i, column=2, padx=10, pady=5, sticky="w")

    def show_lesson_editor(self, lesson=None):
        self.editing_lesson_id = lesson.id if lesson else None
        self.lesson_list_view.grid_forget()
        self.lesson_editor_view.grid(row=0, column=0, sticky="nsew")

        # Clear fields
        self.lesson_editor_title_entry.delete(0, "end")
        self.lesson_editor_date_entry.delete(0, "end")
        self.lesson_editor_content_textbox.delete("1.0", "end")

        if lesson:
            self.lesson_editor_title_entry.insert(0, lesson.title)
            self.lesson_editor_date_entry.insert(0, lesson.date.isoformat())
            self.lesson_editor_content_textbox.insert("1.0", lesson.content or "")
        else:
            self.lesson_editor_date_entry.insert(0, date.today().isoformat())


    def hide_lesson_editor(self):
        self.editing_lesson_id = None
        self.lesson_editor_view.grid_forget()
        self.lesson_list_view.grid(row=0, column=0, sticky="nsew")

    def save_lesson(self):
        title = self.lesson_editor_title_entry.get()
        content = self.lesson_editor_content_textbox.get("1.0", "end-1c")
        date_str = self.lesson_editor_date_entry.get()

        if not title or not date_str:
            # TODO: Show error dialog
            print("Title and Date are required.")
            return

        try:
            lesson_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            # TODO: Show error dialog
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

        if self.editing_lesson_id:
            data_service.update_lesson(self.editing_lesson_id, title, content, lesson_date)
        else:
            data_service.create_lesson(self.class_id, title, content, lesson_date)

        self.populate_lesson_list()
        self.hide_lesson_editor()
        self.lesson_editor_view.grid_forget()
        self.lesson_list_view.grid(row=0, column=0, sticky="nsew")

    def add_assessment_popup(self):
        if not self.class_id:
            return

        def save_callback(data):
            name = data.get("name")
            weight_str = data.get("weight")
            if name and weight_str:
                try:
                    weight = float(weight_str)
                    data_service.add_assessment(self.class_id, name, weight)
                    self.populate_assessment_list()
                except ValueError:
                    print("Invalid weight. Please enter a number.") # Replace with a proper dialog

        fields = {"name": "Assessment Name", "weight": "Weight"}
        AddDialog(self, "Add New Assessment", fields=fields, save_callback=save_callback)

    def populate_assessment_list(self):
        for widget in self.assessment_list_frame.winfo_children():
            widget.destroy()

        if not self.class_id:
            return

        class_ = data_service.get_class_by_id(self.class_id)
        if not class_:
            return

        headers = ["Assessment Name", "Weight", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.assessment_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, assessment in enumerate(class_.assessments, start=1):
            ctk.CTkLabel(self.assessment_list_frame, text=assessment.name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.assessment_list_frame, text=str(assessment.weight)).grid(row=i, column=1, padx=10, pady=5, sticky="w")

            actions_frame = ctk.CTkFrame(self.assessment_list_frame)
            actions_frame.grid(row=i, column=2, padx=5, pady=5, sticky="e")

            edit_button = ctk.CTkButton(actions_frame, text="Edit", command=lambda a=assessment: self.edit_assessment_popup(a))
            edit_button.pack(side="left", padx=5)

            delete_button = ctk.CTkButton(actions_frame, text="Delete", fg_color="red", command=lambda a_id=assessment.id: self.delete_assessment_action(a_id))
            delete_button.pack(side="left", padx=5)

    def delete_assessment_action(self, assessment_id):
        dialog = CTkInputDialog(text="Type 'DELETE' to confirm deletion:", title="Confirm Deletion")
        user_input = dialog.get_input()
        if user_input == "DELETE":
            data_service.delete_assessment(assessment_id)
            self.populate_assessment_list()

    def edit_assessment_popup(self, assessment):
        def save_callback(assessment_id, data):
            name = data.get("name")
            weight_str = data.get("weight")
            if name and weight_str:
                try:
                    weight = float(weight_str)
                    data_service.update_assessment(assessment_id, name, weight)
                    self.populate_assessment_list()
                except ValueError:
                    print("Invalid weight. Please enter a number.")

        fields = {"name": "Assessment Name", "weight": "Weight"}
        initial_data = {
            "id": assessment.id,
            "name": assessment.name,
            "weight": str(assessment.weight)
        }
        EditDialog(self, "Edit Assessment", fields, initial_data, save_callback)

    def enroll_student_popup(self):
        if not self.class_id:
            return

        unenrolled_students = data_service.get_unenrolled_students(self.class_id)
        student_names = [f"{s.first_name} {s.last_name}" for s in unenrolled_students]

        if not student_names:
            # You might want to show a proper message dialog here
            print("No students available to enroll.")
            return

        def save_callback(data):
            student_name = data["student"]
            student = next((s for s in unenrolled_students if f"{s.first_name} {s.last_name}" == student_name), None)

            if student:
                next_call_number = data_service.get_next_call_number(self.class_id)
                data_service.add_student_to_class(student.id, self.class_id, next_call_number)
                self.populate_student_list()

        dropdowns = {"student": ("Student", student_names)}
        AddDialog(self, "Enroll New Student", fields={}, dropdowns=dropdowns, save_callback=save_callback)


    def populate_student_list(self):
        for widget in self.student_list_frame.winfo_children():
            widget.destroy()

        if not self.class_id:
            return

        enrollments = data_service.get_enrollments_for_class(self.class_id)

        if self.show_active_only_checkbox.get():
            enrollments = [e for e in enrollments if e.status == 'Active']

        headers = ["Call #", "Student Name", "Status", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.student_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, enrollment in enumerate(enrollments, start=1):
            ctk.CTkLabel(self.student_list_frame, text=str(enrollment.call_number)).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.student_list_frame, text=f"{enrollment.student.first_name} {enrollment.student.last_name}").grid(row=i, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.student_list_frame, text=enrollment.status).grid(row=i, column=2, padx=10, pady=5, sticky="w")

            status_menu = ctk.CTkOptionMenu(self.student_list_frame, values=["Active", "Inactive"],
                                            command=lambda status, eid=enrollment.id: self.update_status(eid, status))
            status_menu.set(enrollment.status)
            status_menu.grid(row=i, column=3, padx=10, pady=5, sticky="w")

    def update_status(self, enrollment_id, status):
        data_service.update_enrollment_status(enrollment_id, status)
        self.populate_student_list()

    def import_students(self):
        if not self.class_id:
            return

        filepath = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if not filepath:
            return

        try:
            with open(filepath, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Assuming CSV has columns: 'call_number', 'student_name', 'status'
                    call_number = int(row['call_number'])
                    full_name = row['student_name'].split()
                    first_name = full_name[0]
                    last_name = " ".join(full_name[1:])
                    status = row['status']

                    # Find or create student
                    student = data_service.get_student_by_name(f"{first_name} {last_name}")
                    if not student:
                        student = data_service.add_student(first_name, last_name)

                    # Enroll student in the class
                    data_service.add_student_to_class(student.id, self.class_id, call_number, status)

            self.populate_student_list() # Refresh the list
        except Exception as e:
            # Simple error handling for now
            print(f"Error importing students: {e}")


    def populate_lesson_list(self):
        for widget in self.lesson_list_frame.winfo_children():
            widget.destroy()

        if not self.class_id:
            return

        lessons = data_service.get_lessons_for_class(self.class_id)

        headers = ["Date", "Title", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.lesson_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, lesson in enumerate(lessons, start=1):
            ctk.CTkLabel(self.lesson_list_frame, text=str(lesson.date)).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.lesson_list_frame, text=lesson.title).grid(row=i, column=1, padx=10, pady=5, sticky="w")

            edit_button = ctk.CTkButton(self.lesson_list_frame, text="Edit", command=lambda l=lesson: self.show_lesson_editor(l))
            edit_button.grid(row=i, column=2, padx=10, pady=5, sticky="e")


    def on_show(self, class_id=None):
        self.class_id = class_id
        if class_id:
            class_ = data_service.get_class_by_id(self.class_id)
            self.title_label.configure(text=f"Class Details: {class_.name}")
            self.populate_student_list()
            self.populate_assessment_list()
            self.populate_lesson_list()
            self.populate_incident_list()
