import customtkinter as ctk
from app.services.data_service import DataService

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.data_service = DataService()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Title ---
        self.title_label = ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        # --- Statistics Frame ---
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(1, weight=1)

        self.total_students_label = ctk.CTkLabel(self.stats_frame, text="Total Students: 0", font=ctk.CTkFont(size=16))
        self.total_students_label.grid(row=0, column=0, padx=20, pady=10)

        self.total_courses_label = ctk.CTkLabel(self.stats_frame, text="Total Courses: 0", font=ctk.CTkFont(size=16))
        self.total_courses_label.grid(row=0, column=1, padx=20, pady=10)

        # --- Add Student Frame ---
        self.add_student_frame = ctk.CTkFrame(self)
        self.add_student_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.add_student_frame.grid_columnconfigure(0, weight=1)

        self.add_student_label = ctk.CTkLabel(self.add_student_frame, text="Add New Student", font=ctk.CTkFont(size=16, weight="bold"))
        self.add_student_label.grid(row=0, column=0, padx=10, pady=10)

        self.student_firstname_entry = ctk.CTkEntry(self.add_student_frame, placeholder_text="First Name")
        self.student_firstname_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.student_lastname_entry = ctk.CTkEntry(self.add_student_frame, placeholder_text="Last Name")
        self.student_lastname_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.add_student_button = ctk.CTkButton(self.add_student_frame, text="Add Student", command=self.add_student)
        self.add_student_button.grid(row=3, column=0, padx=10, pady=10)

        # --- Add Course Frame ---
        self.add_course_frame = ctk.CTkFrame(self)
        self.add_course_frame.grid(row=2, column=1, padx=20, pady=20, sticky="nsew")
        self.add_course_frame.grid_columnconfigure(0, weight=1)

        self.add_course_label = ctk.CTkLabel(self.add_course_frame, text="Add New Course", font=ctk.CTkFont(size=16, weight="bold"))
        self.add_course_label.grid(row=0, column=0, padx=10, pady=10)

        self.course_name_entry = ctk.CTkEntry(self.add_course_frame, placeholder_text="Course Name")
        self.course_name_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.course_code_entry = ctk.CTkEntry(self.add_course_frame, placeholder_text="Course Code")
        self.course_code_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.add_course_button = ctk.CTkButton(self.add_course_frame, text="Add Course", command=self.add_course)
        self.add_course_button.grid(row=3, column=0, padx=10, pady=10)

        # --- Feedback Label ---
        self.feedback_label = ctk.CTkLabel(self, text="")
        self.feedback_label.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        self.bind("<Visibility>", self.on_show)

    def on_show(self, event):
        self.update_stats()

    def update_stats(self):
        """Fetches and displays the latest statistics."""
        student_count = self.data_service.get_student_count()
        course_count = self.data_service.get_course_count()
        self.total_students_label.configure(text=f"Total Students: {student_count}")
        self.total_courses_label.configure(text=f"Total Courses: {course_count}")
        self.feedback_label.configure(text="") # Clear feedback

    def add_student(self):
        """Handles the add student button click."""
        first_name = self.student_firstname_entry.get()
        last_name = self.student_lastname_entry.get()

        if first_name and last_name:
            self.data_service.add_student(first_name, last_name)
            self.feedback_label.configure(text=f"Student '{first_name} {last_name}' added successfully!", text_color="green")
            self.student_firstname_entry.delete(0, "end")
            self.student_lastname_entry.delete(0, "end")
            self.update_stats()
        else:
            self.feedback_label.configure(text="Please provide both first and last names for the student.", text_color="red")

    def add_course(self):
        """Handles the add course button click."""
        course_name = self.course_name_entry.get()
        course_code = self.course_code_entry.get()

        if course_name and course_code:
            self.data_service.add_course(course_name, course_code)
            self.feedback_label.configure(text=f"Course '{course_name}' added successfully!", text_color="green")
            self.course_name_entry.delete(0, "end")
            self.course_code_entry.delete(0, "end")
            self.update_stats()
        else:
            self.feedback_label.configure(text="Please provide both a name and a code for the course.", text_color="red")
