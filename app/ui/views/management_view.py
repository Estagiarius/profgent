import customtkinter as ctk
from app.services.data_service import DataService
from app.ui.views.edit_dialog import EditDialog
from customtkinter import CTkInputDialog

class ManagementView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.data_service = DataService()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title ---
        self.title_label = ctk.CTkLabel(self, text="Data Management", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # --- Tab View ---
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.tab_view.add("Students")
        self.tab_view.add("Courses")
        self.tab_view.add("Grades")

        # --- Create Scrollable Frames for each tab ---
        self.students_frame = ctk.CTkScrollableFrame(self.tab_view.tab("Students"))
        self.students_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.courses_frame = ctk.CTkScrollableFrame(self.tab_view.tab("Courses"))
        self.courses_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.grades_frame = ctk.CTkScrollableFrame(self.tab_view.tab("Grades"))
        self.grades_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.bind("<Visibility>", self.on_show)


    def on_show(self, event):
        self.populate_data()

    def populate_data(self):
        """Clears and repopulates all data tabs."""
        self._populate_students()
        self._populate_courses()
        self._populate_grades()

    def _clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _populate_students(self):
        self._clear_frame(self.students_frame)
        for student in self.data_service.get_all_students():
            item_frame = ctk.CTkFrame(self.students_frame)
            item_frame.pack(fill="x", pady=5)

            label_text = f"ID: {student.id} | Name: {student.first_name} {student.last_name}"
            ctk.CTkLabel(item_frame, text=label_text).pack(side="left", padx=10, pady=5)

            delete_button = ctk.CTkButton(item_frame, text="Delete", fg_color="red", command=lambda s=student: self.delete_student(s.id))
            delete_button.pack(side="right", padx=10, pady=5)

            edit_button = ctk.CTkButton(item_frame, text="Edit", command=lambda s=student: self.edit_student(s))
            edit_button.pack(side="right", padx=10, pady=5)

    def _populate_courses(self):
        self._clear_frame(self.courses_frame)
        for course in self.data_service.get_all_courses():
            item_frame = ctk.CTkFrame(self.courses_frame)
            item_frame.pack(fill="x", pady=5)

            label_text = f"ID: {course.id} | Name: {course.course_name} | Code: {course.course_code}"
            ctk.CTkLabel(item_frame, text=label_text).pack(side="left", padx=10, pady=5)

            delete_button = ctk.CTkButton(item_frame, text="Delete", fg_color="red", command=lambda c=course: self.delete_course(c.id))
            delete_button.pack(side="right", padx=10, pady=5)

            edit_button = ctk.CTkButton(item_frame, text="Edit", command=lambda c=course: self.edit_course(c))
            edit_button.pack(side="right", padx=10, pady=5)


    def _populate_grades(self):
        self._clear_frame(self.grades_frame)
        students = {s.id: f"{s.first_name} {s.last_name}" for s in self.data_service.get_all_students()}
        courses = {c.id: c.course_name for c in self.data_service.get_all_courses()}

        for grade in self.data_service.get_all_grades():
            item_frame = ctk.CTkFrame(self.grades_frame)
            item_frame.pack(fill="x", pady=5)

            student_name = students.get(grade.student_id, "Unknown")
            course_name = courses.get(grade.course_id, "Unknown")
            label_text = f"ID: {grade.id} | {student_name} | {course_name} | {grade.assignment_name} | Score: {grade.score}"
            ctk.CTkLabel(item_frame, text=label_text).pack(side="left", padx=10, pady=5)

            delete_button = ctk.CTkButton(item_frame, text="Delete", fg_color="red", command=lambda g=grade: self.delete_grade(g.id))
            delete_button.pack(side="right", padx=10, pady=5)

            # Note: Editing grades is more complex due to dropdowns for student/course.
            # We will only allow editing assignment name and score for now.
            edit_button = ctk.CTkButton(item_frame, text="Edit", command=lambda g=grade: self.edit_grade(g))
            edit_button.pack(side="right", padx=10, pady=5)


    def _confirm_delete(self, item_type: str) -> bool:
        dialog = CTkInputDialog(text=f"Are you sure you want to delete this {item_type}?\nType 'DELETE' to confirm.", title="Confirm Deletion")
        result = dialog.get_input()
        return result == "DELETE"

    def delete_student(self, student_id: int):
        if self._confirm_delete("student"):
            self.data_service.delete_student(student_id)
            self.populate_data()

    def delete_course(self, course_id: int):
        if self._confirm_delete("course"):
            self.data_service.delete_course(course_id)
            self.populate_data()

    def delete_grade(self, grade_id: int):
        if self._confirm_delete("grade"):
            self.data_service.delete_grade(grade_id)
            self.populate_data()

    def edit_student(self, student):
        fields = {"first_name": "First Name", "last_name": "Last Name"}
        data = {"id": student.id, "first_name": student.first_name, "last_name": student.last_name}

        def save_callback(student_id, updated_data):
            self.data_service.update_student(student_id, updated_data['first_name'], updated_data['last_name'])
            self.populate_data()

        EditDialog(self, "Edit Student", fields, data, save_callback)

    def edit_course(self, course):
        fields = {"course_name": "Course Name", "course_code": "Course Code"}
        data = {"id": course.id, "course_name": course.course_name, "course_code": course.course_code}

        def save_callback(course_id, updated_data):
            self.data_service.update_course(course_id, updated_data['course_name'], updated_data['course_code'])
            self.populate_data()

        EditDialog(self, "Edit Course", fields, data, save_callback)

    def edit_grade(self, grade):
        fields = {"assignment_name": "Assignment", "score": "Score"}
        data = {"id": grade.id, "assignment_name": grade.assignment_name, "score": grade.score}

        def save_callback(grade_id, updated_data):
            try:
                score = float(updated_data['score'])
                self.data_service.update_grade(grade_id, updated_data['assignment_name'], score)
                self.populate_data()
            except ValueError:
                # Handle error - maybe show a message box
                print("Invalid score format")

        EditDialog(self, "Edit Grade", fields, data, save_callback)
