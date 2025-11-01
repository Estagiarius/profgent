import customtkinter as ctk
from app.services.data_service import DataService
from app.models.class_ import Class

class GradeGridView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.data_service = DataService()

        self.classes: list[Class] = []
        self.selected_class_id: int | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Title ---
        self.title_label = ctk.CTkLabel(self, text="Grade Grid", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # --- Class Selector ---
        self.class_frame = ctk.CTkFrame(self)
        self.class_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.class_frame.grid_columnconfigure(1, weight=1)

        self.class_label = ctk.CTkLabel(self.class_frame, text="Select Class")
        self.class_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.class_menu = ctk.CTkOptionMenu(self.class_frame, values=[], command=self.on_class_select)
        self.class_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # --- Grade Grid Frame ---
        self.grid_frame = ctk.CTkFrame(self)
        self.grid_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        self.bind("<Visibility>", self.on_show)

    def on_show(self, event):
        self.load_classes()

    def load_classes(self):
        self.classes = self.data_service.get_all_classes()
        class_names = [f"{c.course.course_code} - {c.name}" for c in self.classes]
        self.class_menu.configure(values=class_names if class_names else ["No classes"])
        if class_names:
            self.class_menu.set(class_names[0])
            self.on_class_select(class_names[0])

    def on_class_select(self, selected_name: str):
        self.selected_class_id = next((c.id for c in self.classes if f"{c.course.course_code} - {c.name}" == selected_name), None)
        self.display_grid()

    def display_grid(self):
        # Clear existing grid
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        if self.selected_class_id is None:
            return

        selected_class = self.data_service.get_class_by_id(self.selected_class_id)
        if not selected_class:
            return

        enrollments = self.data_service.get_enrollments_for_class(self.selected_class_id)
        assessments = selected_class.assessments

        # Create header
        ctk.CTkLabel(self.grid_frame, text="Student Name", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5)
        for j, assessment in enumerate(assessments):
            ctk.CTkLabel(self.grid_frame, text=f"{assessment.name}\n(Weight: {assessment.weight})", font=ctk.CTkFont(weight="bold")).grid(row=0, column=j + 1, padx=5, pady=5)

        # Create student rows
        self.grade_entries = {} # To store the entry widgets
        for i, enrollment in enumerate(enrollments):
            student_name = f"{enrollment.student.first_name} {enrollment.student.last_name}"
            ctk.CTkLabel(self.grid_frame, text=student_name).grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")

            for j, assessment in enumerate(assessments):
                grade = next((g for g in enrollment.student.grades if g.assessment_id == assessment.id), None)
                score = str(grade.score) if grade else ""
                entry = ctk.CTkEntry(self.grid_frame, placeholder_text="N/A")
                entry.insert(0, score)
                entry.grid(row=i + 1, column=j + 1, padx=5, pady=5)
                self.grade_entries[(enrollment.student.id, assessment.id)] = entry

        # Save Button
        self.save_button = ctk.CTkButton(self.grid_frame, text="Save Grades", command=self.save_grades)
        self.save_button.grid(row=len(enrollments) + 1, column=len(assessments), padx=10, pady=10, sticky="e")

    def save_grades(self):
        for (student_id, assessment_id), entry in self.grade_entries.items():
            score_str = entry.get()
            if score_str:
                try:
                    score = float(score_str)
                    # This is not the most efficient way to do this, but it's fine for now
                    # A better way would be to have a dedicated update_or_create_grade method

                    # Find if a grade already exists
                    student = self.data_service.get_student_by_name(
                        next(e.student.first_name + " " + e.student.last_name for e in self.data_service.get_enrollments_for_class(self.selected_class_id) if e.student.id == student_id)
                    )
                    existing_grade = next((g for g in student.grades if g.assessment_id == assessment_id), None)

                    if existing_grade:
                        if existing_grade.score != score:
                            # We don't have an update_grade method anymore, so we'll delete and re-add
                            self.data_service.delete_grade(existing_grade.id)
                            self.data_service.add_grade(student_id, assessment_id, score)
                    else:
                        self.data_service.add_grade(student_id, assessment_id, score)
                except ValueError:
                    # Handle invalid input if necessary
                    pass

        # Add feedback to the user
        feedback_label = ctk.CTkLabel(self.grid_frame, text="Grades saved successfully!", text_color="green")
        feedback_label.grid(row=len(self.grade_entries) + 2, column=len(assessments), padx=10, pady=10, sticky="e")
