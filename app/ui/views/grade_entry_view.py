import customtkinter as ctk
from app.services.data_service import DataService
from app.models.student import Student
from app.models.course import Course

class GradeEntryView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.data_service = DataService()

        # Data storage
        self.students: list[Student] = []
        self.courses: list[Course] = []
        self.selected_student_id: int | None = None
        self.selected_course_id: int | None = None

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

        # Course Dropdown
        self.course_label = ctk.CTkLabel(self.form_frame, text="Select Course")
        self.course_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.course_menu = ctk.CTkOptionMenu(self.form_frame, values=[], command=self.on_course_select)
        self.course_menu.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Assignment Name Entry
        self.assignment_label = ctk.CTkLabel(self.form_frame, text="Assignment Name")
        self.assignment_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.assignment_entry = ctk.CTkEntry(self.form_frame, placeholder_text="e.g., Midterm Exam")
        self.assignment_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

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
        """Loads students and courses into the dropdowns."""
        self.students = self.data_service.get_all_students()
        self.courses = self.data_service.get_all_courses()

        student_names = [f"{s.first_name} {s.last_name}" for s in self.students]
        course_names = [c.course_name for c in self.courses]

        self.student_menu.configure(values=student_names if student_names else ["No students available"])
        self.course_menu.configure(values=course_names if course_names else ["No courses available"])

        # Reset selections
        self.student_menu.set(student_names[0] if student_names else "No students available")
        self.course_menu.set(course_names[0] if course_names else "No courses available")
        self.on_student_select(student_names[0] if student_names else None)
        self.on_course_select(course_names[0] if course_names else None)

    def on_student_select(self, selected_name: str):
        self.selected_student_id = None
        for student in self.students:
            if f"{student.first_name} {student.last_name}" == selected_name:
                self.selected_student_id = student.id
                break

    def on_course_select(self, selected_name: str):
        self.selected_course_id = None
        for course in self.courses:
            if course.course_name == selected_name:
                self.selected_course_id = course.id
                break

    def submit_grade(self):
        assignment = self.assignment_entry.get()
        score_str = self.score_entry.get()

        # --- Validation ---
        if self.selected_student_id is None or self.selected_course_id is None:
            self.feedback_label.configure(text="Please ensure a student and course are selected.", text_color="red")
            return
        if not assignment:
            self.feedback_label.configure(text="Please enter an assignment name.", text_color="red")
            return
        try:
            score = float(score_str)
        except ValueError:
            self.feedback_label.configure(text="Score must be a valid number.", text_color="red")
            return

        # --- Submission ---
        self.data_service.add_grade(self.selected_student_id, self.selected_course_id, assignment, score)
        self.feedback_label.configure(text=f"Grade for assignment '{assignment}' added successfully!", text_color="green")

        # Clear inputs
        self.assignment_entry.delete(0, "end")
        self.score_entry.delete(0, "end")
