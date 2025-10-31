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

        self.bind("<Visibility>", self.on_show)

    def on_show(self, event=None): self.populate_data()
    def populate_data(self): self._populate_students(); self._populate_courses(); self._populate_grades()
    def _clear_frame(self, frame): [w.destroy() for w in frame.winfo_children()]

    def _populate_students(self):
        self._clear_frame(self.students_frame)
        students = data_service.get_all_students()

        if self.show_active_only.get():
            students = [s for s in students if s.status and s.status.lower() == "active"]

        for student in students:
            f = ctk.CTkFrame(self.students_frame); f.pack(fill="x", pady=5)
            label_text = f"ID: {student.id} | {student.first_name} {student.last_name} | Status: {student.status or 'N/A'}"
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
        students = {s.id: f"{s.first_name} {s.last_name}" for s in data_service.get_all_students()}
        courses = {c.id: c.course_name for c in data_service.get_all_courses()}
        for grade in data_service.get_all_grades():
            f = ctk.CTkFrame(self.grades_frame); f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=f"ID: {grade.id} | {students.get(grade.student_id)} | {courses.get(grade.course_id)} | {grade.assignment_name}: {grade.score}").pack(side="left", padx=10)
            ctk.CTkButton(f, text="Delete", fg_color="red", command=lambda g=grade.id: self.delete_grade(g)).pack(side="right", padx=5)
            ctk.CTkButton(f, text="Edit", command=lambda g=grade: self.edit_grade(g)).pack(side="right", padx=5)

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
            data_service.update_student(id, data['first_name'], data['last_name'], data['status'])
            self.populate_data()
        EditDialog(self, "Edit Student", {"first_name":"First Name", "last_name":"Last Name", "status": "Status (e.g., Active)"}, {
            "id": s.id, "first_name": s.first_name, "last_name": s.last_name, "status": s.status or ""
        }, cb)

    def edit_course(self, c):
        def cb(id, data): data_service.update_course(id, data['course_name'], data['course_code']); self.populate_data()
        EditDialog(self, "Edit Course", {"course_name":"Name", "course_code":"Code"}, vars(c), cb)

    def edit_grade(self, g):
        def cb(id, data):
            try: data_service.update_grade(id, data['assignment_name'], float(data['score'])); self.populate_data()
            except ValueError: pass
        EditDialog(self, "Edit Grade", {"assignment_name":"Assignment", "score":"Score"}, vars(g), cb)

    def add_student_popup(self):
        def cb(data):
            data_service.add_student(data['first_name'], data['last_name'], data.get('status', 'Active'))
            self.populate_data()
        AddDialog(self, "Add Student", {"first_name":"First Name", "last_name":"Last Name", "status": "Status"}, save_callback=cb)

    def add_course_popup(self):
        def cb(data): data_service.add_course(data['course_name'], data['course_code']); self.populate_data()
        AddDialog(self, "Add Course", {"course_name":"Name", "course_code":"Code"}, save_callback=cb)
