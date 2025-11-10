import customtkinter as ctk
from app.services import data_service
from app.ui.views.edit_dialog import EditDialog
from app.ui.views.add_dialog import AddDialog
from customtkinter import CTkInputDialog

class ManagementView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Data Management", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.tab_view.add("Students")
        self.tab_view.add("Courses")
        self.tab_view.add("Grades")

        # --- Students Tab ---
        students_tab = self.tab_view.tab("Students")
        students_tab.grid_rowconfigure(1, weight=1)
        students_tab.grid_columnconfigure(0, weight=1)

        student_controls_frame = ctk.CTkFrame(students_tab)
        student_controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.add_student_button = ctk.CTkButton(student_controls_frame, text="Add New Student", command=self.add_student_popup)
        self.add_student_button.pack(side="left", padx=(0, 10))

        self.show_active_only = ctk.CTkCheckBox(student_controls_frame, text="Show Active Students Only", command=self._populate_students)
        self.show_active_only.pack(side="left")

        self.students_frame = ctk.CTkScrollableFrame(students_tab)
        self.students_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Courses Tab ---
        courses_tab = self.tab_view.tab("Courses")
        courses_tab.grid_rowconfigure(1, weight=1)
        courses_tab.grid_columnconfigure(0, weight=1)
        self.add_course_button = ctk.CTkButton(courses_tab, text="Add New Course", command=self.add_course_popup)
        self.add_course_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.courses_frame = ctk.CTkScrollableFrame(courses_tab)
        self.courses_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Grades Tab ---
        grades_tab = self.tab_view.tab("Grades")
        grades_tab.grid_rowconfigure(1, weight=1)
        grades_tab.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(grades_tab, text="Use the 'Grade Entry' screen to add new grades.").grid(row=0, column=0, padx=10, pady=10)
        self.grades_frame = ctk.CTkScrollableFrame(grades_tab)
        self.grades_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def on_show(self, **kwargs): self.populate_data()
    def populate_data(self): self._populate_students(); self._populate_courses(); self._populate_grades()
    def _clear_frame(self, frame): [w.destroy() for w in frame.winfo_children()]

    def _populate_students(self):
        self._clear_frame(self.students_frame)
        if self.show_active_only.get():
            students = data_service.get_students_with_active_enrollment()
        else:
            students = data_service.get_all_students()

        for student in students:
            f = ctk.CTkFrame(self.students_frame); f.pack(fill="x", pady=5)
            label_text = f"ID: {student.id} | {student.first_name} {student.last_name}"
            ctk.CTkLabel(f, text=label_text).pack(side="left", padx=10)
            ctk.CTkButton(f, text="Delete", fg_color="red", command=lambda s=student.id: self.delete_student(s)).pack(side="right", padx=5)
            ctk.CTkButton(f, text="Edit", command=lambda s=student: self.edit_student(s)).pack(side="right", padx=5)

    def _populate_courses(self):
        self._clear_frame(self.courses_frame)
        for course in data_service.get_all_courses():
            f = ctk.CTkFrame(self.courses_frame); f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=f"ID: {course.id} | {course.course_name} ({course.course_code})").pack(side="left", padx=10)
            ctk.CTkButton(f, text="Delete", fg_color="red", command=lambda c=course.id: self.delete_course(c)).pack(side="right", padx=5)
            ctk.CTkButton(f, text="Edit", command=lambda c=course: self.edit_course(c)).pack(side="right", padx=5)

    def _populate_grades(self):
        self._clear_frame(self.grades_frame)
        grades = data_service.get_all_grades_with_details()

        for grade in grades:
            f = ctk.CTkFrame(self.grades_frame)
            f.pack(fill="x", pady=5)

            student_name = f"{grade.student.first_name} {grade.student.last_name}"
            course_name = grade.assessment.class_.course.course_name
            assessment_name = grade.assessment.name

            label_text = f"ID: {grade.id} | {student_name} | {course_name} | {assessment_name}: {grade.score}"

            ctk.CTkLabel(f, text=label_text).pack(side="left", padx=10)
            ctk.CTkButton(f, text="Delete", fg_color="red", command=lambda g=grade.id: self.delete_grade(g)).pack(side="right", padx=5)
            # Edit functionality for grades in this view is complex due to the new structure and has been removed.
            # The Grade Grid is the primary place for editing.

    def _confirm_delete(self):
        d = CTkInputDialog(text="Type 'DELETE' to confirm.", title="Confirm Deletion"); return d.get_input() == "DELETE"

    def delete_student(self, sid):
        if self._confirm_delete(): data_service.delete_student(sid); self.populate_data()
    def delete_course(self, cid):
        if self._confirm_delete(): data_service.delete_course(cid); self.populate_data()
    def delete_grade(self, gid):
        if self._confirm_delete(): data_service.delete_grade(gid); self.populate_data()

    def edit_student(self, s):
        def cb(id, data):
            data_service.update_student(id, data['first_name'], data['last_name'])
            self.populate_data()
        EditDialog(self, "Edit Student", {"first_name":"First Name", "last_name":"Last Name"}, {
            "id": s.id, "first_name": s.first_name, "last_name": s.last_name
        }, cb)

    def edit_course(self, c):
        def cb(id, data): data_service.update_course(id, data['course_name'], data['course_code']); self.populate_data()
        EditDialog(self, "Edit Course", {"course_name":"Name", "course_code":"Code"}, vars(c), cb)

    def add_student_popup(self):
        def cb(data):
            data_service.add_student(data['first_name'], data['last_name'])
            self.populate_data()
        AddDialog(self, "Add Student", {"first_name":"First Name", "last_name":"Last Name"}, save_callback=cb)

    def add_course_popup(self):
        def cb(data): data_service.add_course(data['course_name'], data['course_code']); self.populate_data()
        AddDialog(self, "Add Course", {"course_name":"Name", "course_code":"Code"}, save_callback=cb)
