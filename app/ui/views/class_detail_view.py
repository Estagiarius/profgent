import customtkinter as ctk
from tkinter import filedialog
import csv
from app.services import data_service

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

        self.import_button = ctk.CTkButton(self, text="Import Students (.csv)", command=self.import_students)
        self.import_button.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")

    def populate_student_list(self):
        for widget in self.student_list_frame.winfo_children():
            widget.destroy()

        if not self.class_id:
            return

        enrollments = data_service.get_enrollments_for_class(self.class_id)
        headers = ["Call #", "Student Name", "Status"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.student_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, enrollment in enumerate(enrollments, start=1):
            ctk.CTkLabel(self.student_list_frame, text=str(enrollment.call_number)).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.student_list_frame, text=f"{enrollment.student.first_name} {enrollment.student.last_name}").grid(row=i, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.student_list_frame, text=enrollment.student.status).grid(row=i, column=2, padx=10, pady=5, sticky="w")

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
                        student = data_service.add_student(first_name, last_name, status)
                    else:
                        # Update status if it has changed
                        if student.status != status:
                            data_service.update_student(student.id, student.first_name, student.last_name, status)

                    # Enroll student in the class
                    data_service.add_student_to_class(student.id, self.class_id, call_number)

            self.populate_student_list() # Refresh the list
        except Exception as e:
            # Simple error handling for now
            print(f"Error importing students: {e}")


    def on_show(self, class_id=None):
        self.class_id = class_id
        class_ = data_service.get_class_by_id(self.class_id)
        self.title_label.configure(text=f"Class Details: {class_.name}")
        self.populate_student_list()
