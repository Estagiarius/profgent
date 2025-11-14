import customtkinter as ctk
from tkinter import filedialog, messagebox
import csv
from datetime import date, datetime
from app.services import data_service
from app.ui.views.add_dialog import AddDialog
from app.ui.views.edit_dialog import EditDialog
from customtkinter import CTkInputDialog
from app.utils.async_utils import run_async_task
from app.utils.import_utils import async_import_students

class ClassDetailView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.class_id = None
        self.editing_lesson_id = None

        self.status_map = {"Ativo": "Active", "Inativo": "Inactive"}
        self.status_map_rev = {v: k for k, v in self.status_map.items()}

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Detalhes da Turma", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.tab_view.add("Alunos")
        self.tab_view.add("Avaliações")
        self.tab_view.add("Aulas")
        self.tab_view.add("Incidentes")
        self.tab_view.add("Quadro de Notas")

        # --- Students Tab ---
        students_tab = self.tab_view.tab("Alunos")
        students_tab.grid_rowconfigure(1, weight=1)
        students_tab.grid_columnconfigure(0, weight=1)

        self.options_frame = ctk.CTkFrame(students_tab)
        self.options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.show_active_only_checkbox = ctk.CTkCheckBox(self.options_frame, text="Mostrar Apenas Alunos Ativos", command=self.populate_student_list)
        self.show_active_only_checkbox.pack(side="left", padx=10, pady=5)
        self.show_active_only_checkbox.select()

        self.student_list_frame = ctk.CTkScrollableFrame(students_tab)
        self.student_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.controls_frame = ctk.CTkFrame(students_tab)
        self.controls_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.controls_frame.grid_columnconfigure(0, weight=1)
        self.controls_frame.grid_columnconfigure(1, weight=1)

        self.enroll_student_button = ctk.CTkButton(self.controls_frame, text="Matricular Aluno", command=self.enroll_student_popup)
        self.enroll_student_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.import_button = ctk.CTkButton(self.controls_frame, text="Importar Alunos (.csv)", command=self.import_students)
        self.import_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # --- Assessments Tab ---
        assessments_tab = self.tab_view.tab("Avaliações")
        assessments_tab.grid_rowconfigure(0, weight=1)
        assessments_tab.grid_columnconfigure(0, weight=1)

        self.assessment_list_frame = ctk.CTkScrollableFrame(assessments_tab)
        self.assessment_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.add_assessment_button = ctk.CTkButton(assessments_tab, text="Adicionar Nova Avaliação", command=self.add_assessment_popup)
        self.add_assessment_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Lessons Tab ---
        lessons_tab = self.tab_view.tab("Aulas")
        lessons_tab.grid_rowconfigure(0, weight=1)
        lessons_tab.grid_columnconfigure(0, weight=1)

        # Container for list and editor to toggle visibility
        self.lesson_container = ctk.CTkFrame(lessons_tab)
        self.lesson_container.grid(row=0, column=0, sticky="nsew")
        self.lesson_container.grid_rowconfigure(0, weight=1)
        self.lesson_container.grid_columnconfigure(0, weight=1)

        # --- Lesson List View ---
        self.lesson_list_view = ctk.CTkFrame(self.lesson_container)
        self.lesson_list_view.grid(row=0, column=0, sticky="nsew")
        self.lesson_list_view.grid_rowconfigure(0, weight=1)
        self.lesson_list_view.grid_columnconfigure(0, weight=1)

        self.lesson_list_frame = ctk.CTkScrollableFrame(self.lesson_list_view)
        self.lesson_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.add_lesson_button = ctk.CTkButton(self.lesson_list_view, text="Adicionar Nova Aula", command=self.show_lesson_editor)
        self.add_lesson_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Lesson Editor View ---
        self.lesson_editor_view = ctk.CTkFrame(self.lesson_container)
        self.lesson_editor_view.grid_rowconfigure(2, weight=1)
        self.lesson_editor_view.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.lesson_editor_view, text="Título:").grid(row=0, column=0, padx=(10,0), pady=10, sticky="w")
        self.lesson_editor_title_entry = ctk.CTkEntry(self.lesson_editor_view, placeholder_text="Título da Aula")
        self.lesson_editor_title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.lesson_editor_view, text="Data (AAAA-MM-DD):").grid(row=1, column=0, padx=(10,0), pady=10, sticky="w")
        self.lesson_editor_date_entry = ctk.CTkEntry(self.lesson_editor_view)
        self.lesson_editor_date_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.lesson_editor_view, text="Conteúdo:").grid(row=2, column=0, padx=(10,0), pady=10, sticky="nw")
        self.lesson_editor_content_textbox = ctk.CTkTextbox(self.lesson_editor_view)
        self.lesson_editor_content_textbox.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        editor_buttons_frame = ctk.CTkFrame(self.lesson_editor_view)
        editor_buttons_frame.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        self.save_lesson_button = ctk.CTkButton(editor_buttons_frame, text="Salvar", command=self.save_lesson)
        self.save_lesson_button.pack(side="left", padx=5)

        self.cancel_lesson_button = ctk.CTkButton(editor_buttons_frame, text="Cancelar", command=self.hide_lesson_editor)
        self.cancel_lesson_button.pack(side="left", padx=5)

        self.hide_lesson_editor() # Initially hidden

        # --- Incidents Tab ---
        incidents_tab = self.tab_view.tab("Incidentes")
        incidents_tab.grid_rowconfigure(0, weight=1)
        incidents_tab.grid_columnconfigure(0, weight=1)

        self.incident_list_frame = ctk.CTkScrollableFrame(incidents_tab)
        self.incident_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.add_incident_button = ctk.CTkButton(incidents_tab, text="Adicionar Novo Incidente", command=self.add_incident_popup)
        self.add_incident_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Grade Grid Tab ---
        grade_grid_tab = self.tab_view.tab("Quadro de Notas")
        grade_grid_tab.grid_rowconfigure(0, weight=1)
        grade_grid_tab.grid_columnconfigure(0, weight=1)

        self.grade_grid_frame = ctk.CTkScrollableFrame(grade_grid_tab)
        self.grade_grid_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.save_grades_button = ctk.CTkButton(grade_grid_tab, text="Salvar Todas as Alterações", command=self.save_all_grades)
        self.save_grades_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    def save_all_grades(self):
        grades_to_upsert = []
        for (student_id, assessment_id), entry_widget in self.grade_entries.items():
            score_str = entry_widget.get()
            if not score_str:  # Skip empty entries
                continue

            try:
                score = float(score_str)
                if not (0 <= score <= 10):
                    messagebox.showerror("Nota Inválida", f"Nota inválida '{score}'. As notas devem ser entre 0 e 10.")
                    return
                grades_to_upsert.append({'student_id': student_id, 'assessment_id': assessment_id, 'score': score})
            except ValueError:
                messagebox.showerror("Nota Inválida", f"Nota inválida '{score_str}'. As notas devem ser numéricas.")
                return

        if not grades_to_upsert:
            messagebox.showinfo("Nenhuma Mudança", "Nenhuma nota nova ou modificada para salvar.")
            return

        data_service.upsert_grades_for_class(self.class_id, grades_to_upsert)

        messagebox.showinfo("Sucesso", "Todas as notas foram salvas com sucesso.")
        self.populate_grade_grid() # Refresh grid to show updated averages

    def populate_grade_grid(self):
        for widget in self.grade_grid_frame.winfo_children():
            widget.destroy()

        if not self.class_id:
            return

        enrollments = data_service.get_enrollments_for_class(self.class_id)
        class_ = data_service.get_class_by_id(self.class_id)
        assessments = class_.assessments if class_ else []

        # Create Header
        headers = ["Nome do Aluno"] + [a.name for a in assessments] + ["Média Final"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(self.grade_grid_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=col, padx=5, pady=5, sticky="w")

        # Create Rows for each student
        self.grade_entries = {} # To store the entry widgets
        grades = data_service.get_grades_for_class(self.class_id)

        for row, enrollment in enumerate(enrollments, start=1):
            student_name = f"{enrollment.student.first_name} {enrollment.student.last_name}"
            name_label = ctk.CTkLabel(self.grade_grid_frame, text=student_name)
            name_label.grid(row=row, column=0, padx=5, pady=5, sticky="w")

            for col, assessment in enumerate(assessments, start=1):
                entry = ctk.CTkEntry(self.grade_grid_frame, width=80)
                entry.grid(row=row, column=col, padx=5, pady=5)

                # Find the existing grade for this student and assessment
                existing_grade = next((g for g in grades if g.student_id == enrollment.student_id and g.assessment_id == assessment.id), None)
                if existing_grade:
                    entry.insert(0, str(existing_grade.score))

                self.grade_entries[(enrollment.student_id, assessment.id)] = entry

            # Calculate and display final average
            average = data_service.calculate_weighted_average(enrollment.student_id, grades, assessments)
            average_label = ctk.CTkLabel(self.grade_grid_frame, text=f"{average:.2f}")
            average_label.grid(row=row, column=len(assessments) + 1, padx=5, pady=5, sticky="w")


    def add_incident_popup(self):
        if not self.class_id:
            return

        enrollments = data_service.get_enrollments_for_class(self.class_id)
        student_names = [f"{e.student.first_name} {e.student.last_name}" for e in enrollments]

        if not student_names:
            # TODO: Show a proper message dialog
            print("Nenhum aluno nesta turma para registrar um incidente.")
            return

        def save_callback(data):
            student_name = data["student"]
            description = data["description"]

            selected_enrollment = next((e for e in enrollments if f"{e.student.first_name} {e.student.last_name}" == student_name), None)

            if selected_enrollment and description:
                data_service.create_incident(self.class_id, selected_enrollment.student.id, description, date.today())
                self.populate_incident_list()

        fields = {"description": "Descrição"}
        dropdowns = {"student": ("Aluno", student_names)}
        AddDialog(self, "Adicionar Novo Incidente", fields=fields, dropdowns=dropdowns, save_callback=save_callback)

    def populate_incident_list(self):
        for widget in self.incident_list_frame.winfo_children():
            widget.destroy()

        if not self.class_id:
            return

        incidents = data_service.get_incidents_for_class(self.class_id)

        headers = ["Nome do Aluno", "Data", "Descrição"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.incident_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, incident in enumerate(incidents, start=1):
            student_name = f"{incident.student.first_name} {incident.student.last_name}"
            ctk.CTkLabel(self.incident_list_frame, text=student_name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.incident_list_frame, text=str(incident.date)).grid(row=i, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.incident_list_frame, text=incident.description, wraplength=400, justify="left").grid(row=i, column=2, padx=10, pady=5, sticky="w")

    def show_lesson_editor(self, lesson=None):
        self.editing_lesson_id = lesson.id if lesson else None
        self.lesson_list_view.grid_forget()
        self.lesson_editor_view.grid(row=0, column=0, sticky="nsew")

        # Clear fields
        self.lesson_editor_title_entry.delete(0, "end")
        self.lesson_editor_date_entry.delete(0, "end")
        self.lesson_editor_content_textbox.delete("1.0", "end")

        if lesson:
            self.lesson_editor_title_entry.insert(0, lesson.title)
            self.lesson_editor_date_entry.insert(0, lesson.date.isoformat())
            self.lesson_editor_content_textbox.insert("1.0", lesson.content or "")
        else:
            self.lesson_editor_date_entry.insert(0, date.today().isoformat())


    def hide_lesson_editor(self):
        self.editing_lesson_id = None
        self.lesson_editor_view.grid_forget()
        self.lesson_list_view.grid(row=0, column=0, sticky="nsew")

    def save_lesson(self):
        title = self.lesson_editor_title_entry.get()
        content = self.lesson_editor_content_textbox.get("1.0", "end-1c")
        date_str = self.lesson_editor_date_entry.get()

        if not title or not date_str:
            # TODO: Show error dialog
            print("Título e Data são obrigatórios.")
            return

        try:
            lesson_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            # TODO: Show error dialog
            print("Formato de data inválido. Use AAAA-MM-DD.")
            return

        if self.editing_lesson_id:
            data_service.update_lesson(self.editing_lesson_id, title, content, lesson_date)
        else:
            data_service.create_lesson(self.class_id, title, content, lesson_date)

        self.populate_lesson_list()
        self.hide_lesson_editor()
        self.lesson_editor_view.grid_forget()
        self.lesson_list_view.grid(row=0, column=0, sticky="nsew")

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
                    print("Peso inválido. Por favor, insira um número.") # Replace with a proper dialog

        fields = {"name": "Nome da Avaliação", "weight": "Peso"}
        AddDialog(self, "Adicionar Nova Avaliação", fields=fields, save_callback=save_callback)

    def populate_assessment_list(self):
        for widget in self.assessment_list_frame.winfo_children():
            widget.destroy()

        if not self.class_id:
            return

        class_ = data_service.get_class_by_id(self.class_id)
        if not class_:
            return

        headers = ["Nome da Avaliação", "Peso", "Ações"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.assessment_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, assessment in enumerate(class_.assessments, start=1):
            ctk.CTkLabel(self.assessment_list_frame, text=assessment.name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.assessment_list_frame, text=str(assessment.weight)).grid(row=i, column=1, padx=10, pady=5, sticky="w")

            actions_frame = ctk.CTkFrame(self.assessment_list_frame)
            actions_frame.grid(row=i, column=2, padx=5, pady=5, sticky="e")

            edit_button = ctk.CTkButton(actions_frame, text="Editar", command=lambda a=assessment: self.edit_assessment_popup(a))
            edit_button.pack(side="left", padx=5)

            delete_button = ctk.CTkButton(actions_frame, text="Excluir", fg_color="red", command=lambda a_id=assessment.id: self.delete_assessment_action(a_id))
            delete_button.pack(side="left", padx=5)

    def delete_assessment_action(self, assessment_id):
        dialog = CTkInputDialog(text="Digite 'DELETE' para confirmar a exclusão:", title="Confirmar Exclusão")
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
                    print("Peso inválido. Por favor, insira um número.")

        fields = {"name": "Nome da Avaliação", "weight": "Peso"}
        initial_data = {
            "id": assessment.id,
            "name": assessment.name,
            "weight": str(assessment.weight)
        }
        EditDialog(self, "Editar Avaliação", fields, initial_data, save_callback)

    def enroll_student_popup(self):
        if not self.class_id:
            return

        unenrolled_students = data_service.get_unenrolled_students(self.class_id)
        student_names = [f"{s.first_name} {s.last_name}" for s in unenrolled_students]

        if not student_names:
            # You might want to show a proper message dialog here
            print("Nenhum aluno disponível para matricular.")
            return

        def save_callback(data):
            student_name = data["student"]
            student = next((s for s in unenrolled_students if f"{s.first_name} {s.last_name}" == student_name), None)

            if student:
                next_call_number = data_service.get_next_call_number(self.class_id)
                data_service.add_student_to_class(student.id, self.class_id, next_call_number)
                self.populate_student_list()

        dropdowns = {"student": ("Aluno", student_names)}
        AddDialog(self, "Matricular Novo Aluno", fields={}, dropdowns=dropdowns, save_callback=save_callback)


    def populate_student_list(self):
        for widget in self.student_list_frame.winfo_children():
            widget.destroy()

        if not self.class_id:
            return

        enrollments = data_service.get_enrollments_for_class(self.class_id)

        if self.show_active_only_checkbox.get():
            enrollments = [e for e in enrollments if e.status == 'Active']

        headers = ["Nº de Chamada", "Nome do Aluno", "Data de Nascimento", "Status", "Ações"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.student_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, enrollment in enumerate(enrollments, start=1):
            ctk.CTkLabel(self.student_list_frame, text=str(enrollment.call_number)).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.student_list_frame, text=f"{enrollment.student.first_name} {enrollment.student.last_name}").grid(row=i, column=1, padx=10, pady=5, sticky="w")

            birth_date_str = enrollment.student.birth_date.strftime("%d/%m/%Y") if enrollment.student.birth_date else ""
            ctk.CTkLabel(self.student_list_frame, text=birth_date_str).grid(row=i, column=2, padx=10, pady=5, sticky="w")

            display_status = self.status_map_rev.get(enrollment.status, enrollment.status)
            ctk.CTkLabel(self.student_list_frame, text=display_status).grid(row=i, column=3, padx=10, pady=5, sticky="w")

            status_menu = ctk.CTkOptionMenu(self.student_list_frame, values=["Ativo", "Inativo"],
                                            command=lambda status, eid=enrollment.id: self.update_status(eid, status))
            status_menu.set(display_status)
            status_menu.grid(row=i, column=4, padx=10, pady=5, sticky="w")

    def update_status(self, enrollment_id, status):
        db_status = self.status_map.get(status, status)
        data_service.update_enrollment_status(enrollment_id, db_status)
        self.populate_student_list()

    def import_students(self):
        if not self.class_id:
            messagebox.showerror("Erro", "Selecione uma turma antes de importar alunos.")
            return

        filepath = filedialog.askopenfilename(
            title="Selecione um arquivo CSV de Alunos",
            filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*"))
        )
        if not filepath:
            return

        self.import_button.configure(state="disabled", text="Importando...")
        self.enroll_student_button.configure(state="disabled")

        coro = async_import_students(
            filepath,
            self.class_id,
            self.main_app.data_service
        )

        run_async_task(coro, self.main_app.loop, self.main_app.async_queue, self._on_import_complete)

    def _on_import_complete(self, result):
        """
        Callback function executed on the main UI thread after the import task finishes.
        """
        # Re-enable UI elements
        self.import_button.configure(state="normal", text="Importar Alunos (.csv)")
        self.enroll_student_button.configure(state="normal")

        # The result can be either the expected tuple or an exception
        if isinstance(result, Exception):
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro fatal durante a importação:\n\n{result}")
            return

        # Unpack the result and show the final message
        success_count, errors = result
        self.populate_student_list()

        if errors:
            error_message = f"{success_count} alunos importados com sucesso, mas ocorreram os seguintes erros:\n\n" + "\n".join(errors)
            messagebox.showwarning("Importação com Erros", error_message)
        else:
            messagebox.showinfo("Sucesso", f"{success_count} alunos importados com sucesso!")


    def populate_lesson_list(self):
        for widget in self.lesson_list_frame.winfo_children():
            widget.destroy()

        if not self.class_id:
            return

        lessons = data_service.get_lessons_for_class(self.class_id)

        headers = ["Data", "Título", "Ações"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.lesson_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, lesson in enumerate(lessons, start=1):
            ctk.CTkLabel(self.lesson_list_frame, text=str(lesson.date)).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.lesson_list_frame, text=lesson.title).grid(row=i, column=1, padx=10, pady=5, sticky="w")

            edit_button = ctk.CTkButton(self.lesson_list_frame, text="Editar", command=lambda l=lesson: self.show_lesson_editor(l))
            edit_button.grid(row=i, column=2, padx=10, pady=5, sticky="e")


    def on_show(self, class_id=None):
        self.class_id = class_id
        if class_id:
            class_ = data_service.get_class_by_id(self.class_id)
            self.title_label.configure(text=f"Detalhes da Turma: {class_.name}")
            self.populate_student_list()
            self.populate_assessment_list()
            self.populate_lesson_list()
            self.populate_incident_list()
            self.populate_grade_grid()
