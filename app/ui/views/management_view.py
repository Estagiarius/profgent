# Importa a biblioteca 'customtkinter' para os componentes da interface.
import customtkinter as ctk
# Importa as janelas de diálogo personalizadas para edição e adição.
from app.ui.views.edit_dialog import EditDialog
from app.ui.views.add_dialog import AddDialog
# Importa o diálogo de entrada de texto padrão para confirmação de exclusão.
from customtkinter import CTkInputDialog
from tkinter import messagebox
from app.utils.async_utils import run_async_task

# Define a classe para a tela de Gestão de Dados.
class ManagementView(ctk.CTkFrame):
    # Método construtor.
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        # Obtém a instância do DataService a partir da aplicação principal.
        self.data_service = self.main_app.data_service

        # Inicializa as variáveis de dados para evitar AttributeError antes do carregamento.
        self.all_students_data = []
        self.active_students_data = []

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

        # Frame de carregamento com um indicador de progresso.
        self.loading_frame = ctk.CTkFrame(self)
        ctk.CTkLabel(self.loading_frame, text="Carregando dados...").pack(pady=(20, 10))
        self.progress_bar = ctk.CTkProgressBar(self.loading_frame, mode='indeterminate')
        self.progress_bar.pack(pady=10, padx=20, fill="x")

    def _show_loading(self):
        """Mostra o indicador de carregamento e esconde o conteúdo principal."""
        self.tab_view.grid_forget()
        self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.progress_bar.start()

    def _hide_loading(self):
        """Esconde o indicador de carregamento e mostra o conteúdo principal."""
        self.progress_bar.stop()
        self.loading_frame.place_forget()
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    # Método chamado sempre que a view é exibida.
    def on_show(self, **kwargs):
        self.populate_data()

    # Método para preencher os dados de todas as abas de uma vez.
    def populate_data(self):
        self._clear_frame(self.students_frame)
        self._clear_frame(self.courses_frame)
        self._clear_frame(self.grades_frame)
        self._show_loading()
        # Executa a busca de dados em segundo plano e define o callback para atualizar a UI.
        run_async_task(
            self._load_data_async(),
            self.main_app.loop,
            self.main_app.thread_queue,
            self._populate_data_callback
        )

    async def _load_data_async(self):
        """Busca todos os dados necessários do banco de dados de forma assíncrona."""
        # Nota: O DataService em si não é async, mas run_async_task executa isso em um thread.
        all_students = self.data_service.get_all_students()
        active_students = self.data_service.get_students_with_active_enrollment()
        courses = self.data_service.get_all_courses()
        grades = self.data_service.get_all_grades_with_details()
        return {
            "all_students": all_students,
            "active_students": active_students,
            "courses": courses,
            "grades": grades
        }

    def _populate_data_callback(self, future):
        """Callback executado quando os dados assíncronos são carregados."""
        self._hide_loading()
        try:
            data = future.result()
            self.all_students_data = data["all_students"]
            self.active_students_data = data["active_students"]

            self._populate_students() # Popula com base no estado do checkbox
            self._populate_courses(data["courses"])
            self._populate_grades(data["grades"])
        except Exception as e:
            messagebox.showerror("Erro ao Carregar Dados", f"Não foi possível carregar os dados: {e}")

    # Método utilitário para limpar todos os widgets de um frame.
    def _clear_frame(self, frame): [w.destroy() for w in frame.winfo_children()]

    # Preenche a lista de alunos na aba "Alunos".
    def _populate_students(self):
        self._clear_frame(self.students_frame)
        # Usa os dados já carregados na memória.
        students_to_show = self.active_students_data if self.show_active_only.get() else self.all_students_data

        # Itera sobre os alunos e cria uma linha para cada um.
        for student in students_to_show:
            f = ctk.CTkFrame(self.students_frame); f.pack(fill="x", pady=5)
            label_text = f"ID: {student['id']} | {student['first_name']} {student['last_name']}"
            ctk.CTkLabel(f, text=label_text).pack(side="left", padx=10)
            ctk.CTkButton(f, text="Excluir", fg_color="red", command=lambda s_id=student['id']: self.delete_student(s_id)).pack(side="right", padx=5)
            ctk.CTkButton(f, text="Editar", command=lambda s=student: self.edit_student(s)).pack(side="right", padx=5)

    # Preenche a lista de cursos na aba "Disciplinas".
    def _populate_courses(self, courses):
        self._clear_frame(self.courses_frame)
        for course in courses:
            f = ctk.CTkFrame(self.courses_frame); f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=f"ID: {course['id']} | {course['course_name']} ({course['course_code']})").pack(side="left", padx=10)
            ctk.CTkButton(f, text="Excluir", fg_color="red", command=lambda c_id=course['id']: self.delete_course(c_id)).pack(side="right", padx=5)
            ctk.CTkButton(f, text="Editar", command=lambda c=course: self.edit_course(c)).pack(side="right", padx=5)

    # Preenche a lista de notas na aba "Notas".
    def _populate_grades(self, grades):
        self._clear_frame(self.grades_frame)
        # Itera sobre as notas e cria uma linha para cada uma.
        for grade in grades:
            f = ctk.CTkFrame(self.grades_frame)
            f.pack(fill="x", pady=5)

            label_text = (
                f"ID: {grade['id']} | {grade['student_first_name']} {grade['student_last_name']} | "
                f"{grade['class_name']} - {grade['course_name']} | {grade['assessment_name']}: {grade['score']}"
            )

            ctk.CTkLabel(f, text=label_text).pack(side="left", padx=10)
            ctk.CTkButton(f, text="Excluir", fg_color="red", command=lambda g_id=grade['id']: self.delete_grade(g_id)).pack(side="right", padx=5)

    # Método auxiliar para exibir um diálogo de confirmação de exclusão.
    def _confirm_delete(self):
        d = CTkInputDialog(text="Digite 'DELETE' para confirmar.", title="Confirmar Exclusão"); return d.get_input() == "DELETE"

    # Métodos de exclusão que chamam o diálogo de confirmação antes de agir.
    def delete_student(self, sid):
        if self._confirm_delete():
            try:
                self.data_service.delete_student(sid)
                self.populate_data()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir aluno: {e}")

    def delete_course(self, cid):
        if self._confirm_delete():
            try:
                self.data_service.delete_course(cid)
                self.populate_data()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir disciplina: {e}")

    def delete_grade(self, gid):
        if self._confirm_delete():
            try:
                self.data_service.delete_grade(gid)
                self.populate_data()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir nota: {e}")

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
