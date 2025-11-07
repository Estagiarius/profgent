import customtkinter as ctk
from tkinter import filedialog
import csv
from app.services import data_service
from app.ui.views.add_dialog import AddDialog
from app.ui.views.edit_dialog import EditDialog
from customtkinter import CTkInputDialog

class ClassDetailView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.class_id = None

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


    def on_show(self, class_id=None):
        self.class_id = class_id
        if class_id:
            class_ = data_service.get_class_by_id(self.class_id)
            self.title_label.configure(text=f"Class Details: {class_.name}")
            self.populate_student_list()
            self.populate_assessment_list()
