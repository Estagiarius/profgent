# Importa a biblioteca 'customtkinter' para os componentes da interface.
import customtkinter as ctk
# Importa as janelas de diálogo personalizadas para edição e adição.
from app.ui.views.edit_dialog import EditDialog
from app.ui.views.add_dialog import AddDialog
# Importa o diálogo de entrada de texto padrão para confirmação de exclusão.
from customtkinter import CTkInputDialog

# Define a classe para a tela de Gestão de Dados.
class ManagementView(ctk.CTkFrame):
    # Método construtor.
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        # Obtém a instância do DataService a partir da aplicação principal.
        self.data_service = self.main_app.data_service

        # Configura o layout de grade da view.
        self.grid_rowconfigure(1, weight=1) # A linha 1 (com as abas) se expande.
        self.grid_columnconfigure(0, weight=1) # A coluna 0 se expande.

        # Rótulo do título da tela.
        self.title_label = ctk.CTkLabel(self, text="Gestão de Dados", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Cria o widget de abas para organizar a gestão de Alunos, Disciplinas e Notas.
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Adiciona as abas.
        self.tab_view.add("Alunos")
        self.tab_view.add("Disciplinas")
        self.tab_view.add("Notas")

        # --- Aba de Alunos ---
        students_tab = self.tab_view.tab("Alunos")
        students_tab.grid_rowconfigure(1, weight=1)
        students_tab.grid_columnconfigure(0, weight=1)

        # Frame para os botões de controle da aba de alunos.
        student_controls_frame = ctk.CTkFrame(students_tab)
        student_controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.add_student_button = ctk.CTkButton(student_controls_frame, text="Adicionar Novo Aluno", command=self.add_student_popup)
        self.add_student_button.pack(side="left", padx=(0, 10))

        # Checkbox para filtrar e mostrar apenas alunos com matrículas ativas.
        self.show_active_only = ctk.CTkCheckBox(student_controls_frame, text="Mostrar Apenas Alunos Ativos", command=self._populate_students)
        self.show_active_only.pack(side="left")

        # Frame com rolagem para a lista de alunos.
        self.students_frame = ctk.CTkScrollableFrame(students_tab)
        self.students_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Aba de Disciplinas ---
        courses_tab = self.tab_view.tab("Disciplinas")
        courses_tab.grid_rowconfigure(1, weight=1)
        courses_tab.grid_columnconfigure(0, weight=1)
        self.add_course_button = ctk.CTkButton(courses_tab, text="Adicionar Nova Disciplina", command=self.add_course_popup)
        self.add_course_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.courses_frame = ctk.CTkScrollableFrame(courses_tab)
        self.courses_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Aba de Notas ---
        grades_tab = self.tab_view.tab("Notas")
        grades_tab.grid_rowconfigure(1, weight=1)
        grades_tab.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(grades_tab, text="Use a tela 'Quadro de Notas' na visualização da turma para adicionar novas notas.").grid(row=0, column=0, padx=10, pady=10)
        self.grades_frame = ctk.CTkScrollableFrame(grades_tab)
        self.grades_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Método chamado sempre que a view é exibida.
    def on_show(self, **kwargs): self.populate_data()
    # Método para preencher os dados de todas as abas de uma vez.
    def populate_data(self): self._populate_students(); self._populate_courses(); self._populate_grades()
    # Método utilitário para limpar todos os widgets de um frame.
    def _clear_frame(self, frame): [w.destroy() for w in frame.winfo_children()]

    # Preenche a lista de alunos na aba "Alunos".
    def _populate_students(self):
        self._clear_frame(self.students_frame)
        # Verifica se o checkbox de filtro está marcado.
        if self.show_active_only.get():
            students = self.data_service.get_students_with_active_enrollment()
        else:
            students = self.data_service.get_all_students()

        # Itera sobre os alunos e cria uma linha para cada um.
        for student in students:
            f = ctk.CTkFrame(self.students_frame); f.pack(fill="x", pady=5)
            label_text = f"ID: {student['id']} | {student['first_name']} {student['last_name']}"
            ctk.CTkLabel(f, text=label_text).pack(side="left", padx=10)
            ctk.CTkButton(f, text="Excluir", fg_color="red", command=lambda s_id=student['id']: self.delete_student(s_id)).pack(side="right", padx=5)
            ctk.CTkButton(f, text="Editar", command=lambda s=student: self.edit_student(s)).pack(side="right", padx=5)

    # Preenche a lista de cursos na aba "Disciplinas".
    def _populate_courses(self):
        self._clear_frame(self.courses_frame)
        for course in self.data_service.get_all_courses():
            f = ctk.CTkFrame(self.courses_frame); f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=f"ID: {course['id']} | {course['course_name']} ({course['course_code']})").pack(side="left", padx=10)
            ctk.CTkButton(f, text="Excluir", fg_color="red", command=lambda c_id=course['id']: self.delete_course(c_id)).pack(side="right", padx=5)
            ctk.CTkButton(f, text="Editar", command=lambda c=course: self.edit_course(c)).pack(side="right", padx=5)

    # Preenche a lista de notas na aba "Notas".
    def _populate_grades(self):
        self._clear_frame(self.grades_frame)
        # Busca todas as notas com detalhes (nome do aluno, curso, etc.).
        grades = self.data_service.get_all_grades_with_details()

        for grade in grades:
            f = ctk.CTkFrame(self.grades_frame)
            f.pack(fill="x", pady=5)

            # Atualizado para mostrar Turma e Disciplina
            label_text = (
                f"ID: {grade['id']} | {grade['student_first_name']} {grade['student_last_name']} | "
                f"{grade['class_name']} - {grade['course_name']} | {grade['assessment_name']}: {grade['score']}"
            )

            ctk.CTkLabel(f, text=label_text).pack(side="left", padx=10)
            ctk.CTkButton(f, text="Excluir", fg_color="red", command=lambda g_id=grade['id']: self.delete_grade(g_id)).pack(side="right", padx=5)
            # A funcionalidade de edição de notas nesta tela foi removida, pois
            # o Quadro de Notas é o local principal para isso.

    # Método auxiliar para exibir um diálogo de confirmação de exclusão.
    def _confirm_delete(self):
        d = CTkInputDialog(text="Digite 'DELETE' para confirmar.", title="Confirmar Exclusão"); return d.get_input() == "DELETE"

    # Métodos de exclusão que chamam o diálogo de confirmação antes de agir.
    def delete_student(self, sid):
        if self._confirm_delete(): self.data_service.delete_student(sid); self.populate_data()
    def delete_course(self, cid):
        if self._confirm_delete(): self.data_service.delete_course(cid); self.populate_data()
    def delete_grade(self, gid):
        if self._confirm_delete(): self.data_service.delete_grade(gid); self.populate_data()

    # Abre o diálogo de edição para um aluno.
    def edit_student(self, s):
        # Define o callback que será executado ao salvar no diálogo.
        def cb(id, data):
            self.data_service.update_student(id, data['first_name'], data['last_name'])
            self.populate_data()
        initial_data = { "id": s['id'], "first_name": s['first_name'], "last_name": s['last_name'] }
        EditDialog(self, "Editar Aluno", {"first_name":"Nome", "last_name":"Sobrenome"}, initial_data, cb)

    # Abre o diálogo de edição para um curso.
    def edit_course(self, c):
        def cb(id, data): self.data_service.update_course(id, data['course_name'], data['course_code']); self.populate_data()
        EditDialog(self, "Editar Disciplina", {"course_name":"Nome", "course_code":"Código"}, c, cb)

    # Abre o diálogo de adição para um novo aluno.
    def add_student_popup(self):
        def cb(data):
            self.data_service.add_student(data['first_name'], data['last_name'])
            self.populate_data()
        AddDialog(self, "Adicionar Aluno", {"first_name":"Nome", "last_name":"Sobrenome"}, save_callback=cb)

    # Abre o diálogo de adição para um novo curso.
    def add_course_popup(self):
        def cb(data): self.data_service.add_course(data['course_name'], data['course_code']); self.populate_data()
        AddDialog(self, "Adicionar Disciplina", {"course_name":"Nome", "course_code":"Código"}, save_callback=cb)
