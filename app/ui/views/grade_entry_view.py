import customtkinter as ctk
from app.services.data_service import DataService
from app.models.student import Student
from app.models.class_ import Class
from app.models.assessment import Assessment

class GradeEntryView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.data_service = DataService()

        # Data storage
        self.students: list[Student] = []
        self.classes: list[Class] = []
        self.assessments: list[Assessment] = []
        self.selected_student_id: int | None = None
        self.selected_class_id: int | None = None
        self.selected_assessment_id: int | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # --- Title ---
        self.title_label = ctk.CTkLabel(self, text="Grade Entry", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # --- Form Frame ---
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        self.form_frame.grid_columnconfigure(1, weight=1)

        # Student Dropdown
        self.student_label = ctk.CTkLabel(self.form_frame, text="Select Student")
        self.student_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.student_menu = ctk.CTkOptionMenu(self.form_frame, values=[], command=self.on_student_select)
        self.student_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Class Dropdown
        self.class_label = ctk.CTkLabel(self.form_frame, text="Select Class")
        self.class_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.class_menu = ctk.CTkOptionMenu(self.form_frame, values=[], command=self.on_class_select)
        self.class_menu.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Assessment Dropdown
        self.assessment_label = ctk.CTkLabel(self.form_frame, text="Select Assessment")
        self.assessment_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.assessment_menu = ctk.CTkOptionMenu(self.form_frame, values=[], command=self.on_assessment_select)
        self.assessment_menu.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Score Entry
        self.score_label = ctk.CTkLabel(self.form_frame, text="Score")
        self.score_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.score_entry = ctk.CTkEntry(self.form_frame, placeholder_text="e.g., 85.5")
        self.score_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # --- Submit Button ---
        self.submit_button = ctk.CTkButton(self, text="Submit Grade", command=self.submit_grade)
        self.submit_button.grid(row=2, column=0, padx=20, pady=20, sticky="e")

        # --- Feedback Label ---
        self.feedback_label = ctk.CTkLabel(self, text="")
        self.feedback_label.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Bind the visibility event to reload data
        self.bind("<Visibility>", self.on_show)


    def on_show(self, event):
        self.load_data()

    def load_data(self):
        """Loads students and classes into the dropdowns."""
        self.students = self.data_service.get_all_students()
        self.classes = self.data_service.get_all_classes()

        student_names = [f"{s.first_name} {s.last_name}" for s in self.students]
        class_names = [f"{c.course.course_code} - {c.name}" for c in self.classes]

        self.student_menu.configure(values=student_names if student_names else ["No students"])
        self.class_menu.configure(values=class_names if class_names else ["No classes"])

        # Reset selections
        if student_names:
            self.student_menu.set(student_names[0])
            self.on_student_select(student_names[0])
        if class_names:
            self.class_menu.set(class_names[0])
            self.on_class_select(class_names[0])
        else: # If no classes, clear assessment menu
            self.on_class_select(None)

    def on_student_select(self, selected_name: str):
        self.selected_student_id = next((s.id for s in self.students if f"{s.first_name} {s.last_name}" == selected_name), None)

    def on_class_select(self, selected_name: str | None):
        if selected_name is None:
            self.selected_class_id = None
            self.assessments = []
            self.assessment_menu.configure(values=["Select class first"])
            self.assessment_menu.set("Select class first")
            return

        self.selected_class_id = next((c.id for c in self.classes if f"{c.course.course_code} - {c.name}" == selected_name), None)

        if self.selected_class_id:
            # SQLAlchemy relationships make this easy
            selected_class = self.data_service.get_class_by_id(self.selected_class_id)
            self.assessments = selected_class.assessments if selected_class else []
            assessment_names = [a.name for a in self.assessments]
            self.assessment_menu.configure(values=assessment_names if assessment_names else ["No assessments"])
            if assessment_names:
                self.assessment_menu.set(assessment_names[0])
                self.on_assessment_select(assessment_names[0])
            else:
                self.assessment_menu.set("No assessments")
                self.selected_assessment_id = None

    def on_assessment_select(self, selected_name: str):
        self.selected_assessment_id = next((a.id for a in self.assessments if a.name == selected_name), None)

    def submit_grade(self):
        score_str = self.score_entry.get()

        # --- Validation ---
        if self.selected_student_id is None:
            self.feedback_label.configure(text="Please select a student.", text_color="red")
            return
        if self.selected_class_id is None:
            self.feedback_label.configure(text="Please select a class.", text_color="red")
            return
        if self.selected_assessment_id is None:
            self.feedback_label.configure(text="Please select an assessment.", text_color="red")
            return
        if not score_str:
            self.feedback_label.configure(text="Please enter a score.", text_color="red")
            return
        try:
            score = float(score_str)
        except ValueError:
            self.feedback_label.configure(text="Score must be a valid number.", text_color="red")
            return

        # --- Submission ---
        self.data_service.add_grade(self.selected_student_id, self.selected_assessment_id, score)
        self.feedback_label.configure(text=f"Grade added successfully!", text_color="green")

        # Clear score
        self.score_entry.delete(0, "end")
