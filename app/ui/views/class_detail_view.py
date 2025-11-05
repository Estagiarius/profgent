import customtkinter as ctk
from tkinter import filedialog
import csv
from app.services import data_service
from app.ui.views.add_dialog import AddDialog

class ClassDetailView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.class_id = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Class Details", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.student_list_frame = ctk.CTkFrame(self)
        self.student_list_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.controls_frame.grid_columnconfigure(0, weight=1)
        self.controls_frame.grid_columnconfigure(1, weight=1)

        self.enroll_student_button = ctk.CTkButton(self.controls_frame, text="Enroll Student", command=self.enroll_student_popup)
        self.enroll_student_button.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="ew")

        self.import_button = ctk.CTkButton(self.controls_frame, text="Import Students (.csv)", command=self.import_students)
        self.import_button.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="ew")

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
            call_number = data["call_number"]

            student = next((s for s in unenrolled_students if f"{s.first_name} {s.last_name}" == student_name), None)

            if student and call_number:
                try:
                    call_number_int = int(call_number)
                    data_service.add_student_to_class(student.id, self.class_id, call_number_int)
                    self.populate_student_list()
                except ValueError:
                    # Handle non-integer call number
                    print("Invalid call number.")

        fields = {"call_number": "Call Number"}
        dropdowns = {"student": ("Student", student_names)}
        AddDialog(self, "Enroll New Student", fields=fields, dropdowns=dropdowns, save_callback=save_callback)


    def populate_student_list(self):
        for widget in self.student_list_frame.winfo_children():
            widget.destroy()

        if not self.class_id:
            return

        enrollments = data_service.get_enrollments_for_class(self.class_id)
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
        class_ = data_service.get_class_by_id(self.class_id)
        self.title_label.configure(text=f"Class Details: {class_.name}")
        self.populate_student_list()
