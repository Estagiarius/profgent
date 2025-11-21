# Importa componentes e utilitários do tkinter e customtkinter.
import customtkinter as ctk
from tkinter import filedialog, messagebox
import csv
from datetime import date, datetime
# Importa o serviço de dados para interagir com o banco de dados.
from app.services import data_service
# Importa as janelas de diálogo personalizadas para adicionar e editar registros.
from app.ui.views.add_dialog import AddDialog
from app.ui.views.edit_dialog import EditDialog
from customtkinter import CTkInputDialog
# Importa utilitários para tarefas assíncronas e de importação.
from app.utils.async_utils import run_async_task
from app.utils.import_utils import async_import_students

# Define a classe para a tela de detalhes da turma.
class ClassDetailView(ctk.CTkFrame):
    # Método construtor.
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        # ID da turma que está sendo visualizada. Inicialmente nulo.
        self.class_id = None
        # ID da aula que está sendo editada. Inicialmente nulo.
        self.editing_lesson_id = None

        # Mapeamento entre o status exibido na UI (português) e o armazenado no banco (inglês).
        self.status_map = {"Ativo": "Active", "Inativo": "Inactive"}
        # Mapeamento reverso para exibir o status do banco na UI.
        self.status_map_rev = {v: k for k, v in self.status_map.items()}

        # Configuração do layout de grade da view.
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Rótulo do título principal da tela.
        self.title_label = ctk.CTkLabel(self, text="Detalhes da Turma", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Cria o widget de abas (Tabview) para organizar o conteúdo.
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        # Adiciona as abas.
        self.tab_view.add("Alunos")
        self.tab_view.add("Avaliações")
        self.tab_view.add("Aulas")
        self.tab_view.add("Incidentes")
        self.tab_view.add("Quadro de Notas")

        # --- Aba de Alunos ---
        # Obtém a referência à aba "Alunos".
        students_tab = self.tab_view.tab("Alunos")
        students_tab.grid_rowconfigure(1, weight=1)
        students_tab.grid_columnconfigure(0, weight=1)

        # Frame para opções, como o checkbox de filtro.
        self.options_frame = ctk.CTkFrame(students_tab)
        self.options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Checkbox para filtrar e mostrar apenas alunos ativos.
        self.show_active_only_checkbox = ctk.CTkCheckBox(self.options_frame, text="Mostrar Apenas Alunos Ativos", command=self.populate_student_list)
        self.show_active_only_checkbox.pack(side="left", padx=10, pady=5)
        self.show_active_only_checkbox.select() # Marcado por padrão.

        # Frame com rolagem para exibir a lista de alunos.
        self.student_list_frame = ctk.CTkScrollableFrame(students_tab)
        self.student_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Frame para os botões de controle (matricular, importar).
        self.controls_frame = ctk.CTkFrame(students_tab)
        self.controls_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.controls_frame.grid_columnconfigure(0, weight=1)
        self.controls_frame.grid_columnconfigure(1, weight=1)

        # Botão para abrir o pop-up de matrícula de aluno.
        self.enroll_student_button = ctk.CTkButton(self.controls_frame, text="Matricular Aluno", command=self.enroll_student_popup)
        self.enroll_student_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # Botão para iniciar a importação de alunos via arquivo CSV.
        self.import_button = ctk.CTkButton(self.controls_frame, text="Importar Alunos (.csv)", command=self.import_students)
        self.import_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # --- Aba de Avaliações ---
        assessments_tab = self.tab_view.tab("Avaliações")
        assessments_tab.grid_rowconfigure(0, weight=1)
        assessments_tab.grid_columnconfigure(0, weight=1)

        # Frame com rolagem para a lista de avaliações.
        self.assessment_list_frame = ctk.CTkScrollableFrame(assessments_tab)
        self.assessment_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Botão para adicionar uma nova avaliação.
        self.add_assessment_button = ctk.CTkButton(assessments_tab, text="Adicionar Nova Avaliação", command=self.add_assessment_popup)
        self.add_assessment_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Aba de Aulas ---
        lessons_tab = self.tab_view.tab("Aulas")
        lessons_tab.grid_rowconfigure(0, weight=1)
        lessons_tab.grid_columnconfigure(0, weight=1)

        # Container principal para a aba de aulas, para alternar entre a lista e o editor.
        self.lesson_container = ctk.CTkFrame(lessons_tab)
        self.lesson_container.grid(row=0, column=0, sticky="nsew")
        self.lesson_container.grid_rowconfigure(0, weight=1)
        self.lesson_container.grid_columnconfigure(0, weight=1)

        # --- Sub-view: Lista de Aulas ---
        self.lesson_list_view = ctk.CTkFrame(self.lesson_container)
        self.lesson_list_view.grid(row=0, column=0, sticky="nsew")
        self.lesson_list_view.grid_rowconfigure(0, weight=1)
        self.lesson_list_view.grid_columnconfigure(0, weight=1)

        self.lesson_list_frame = ctk.CTkScrollableFrame(self.lesson_list_view)
        self.lesson_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.add_lesson_button = ctk.CTkButton(self.lesson_list_view, text="Adicionar Nova Aula", command=self.show_lesson_editor)
        self.add_lesson_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Sub-view: Editor de Aulas ---
        self.lesson_editor_view = ctk.CTkFrame(self.lesson_container)
        self.lesson_editor_view.grid_rowconfigure(2, weight=1) # O campo de conteúdo (linha 2) se expande.
        self.lesson_editor_view.grid_columnconfigure(1, weight=1) # A coluna dos inputs se expande.

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

        self.hide_lesson_editor() # Editor começa escondido.

        # --- Aba de Incidentes ---
        incidents_tab = self.tab_view.tab("Incidentes")
        incidents_tab.grid_rowconfigure(0, weight=1)
        incidents_tab.grid_columnconfigure(0, weight=1)

        self.incident_list_frame = ctk.CTkScrollableFrame(incidents_tab)
        self.incident_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.add_incident_button = ctk.CTkButton(incidents_tab, text="Adicionar Novo Incidente", command=self.add_incident_popup)
        self.add_incident_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Aba do Quadro de Notas ---
        grade_grid_tab = self.tab_view.tab("Quadro de Notas")
        grade_grid_tab.grid_rowconfigure(1, weight=1)
        grade_grid_tab.grid_columnconfigure(0, weight=1)

        # Frame para opções (filtro).
        self.grade_options_frame = ctk.CTkFrame(grade_grid_tab)
        self.grade_options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Checkbox para filtrar e mostrar apenas alunos ativos no quadro de notas.
        self.show_active_only_grades_checkbox = ctk.CTkCheckBox(
            self.grade_options_frame,
            text="Mostrar Apenas Alunos Ativos",
            command=self.populate_grade_grid
        )
        self.show_active_only_grades_checkbox.pack(side="left", padx=10, pady=5)
        self.show_active_only_grades_checkbox.select() # Marcado por padrão.

        self.grade_grid_frame = ctk.CTkScrollableFrame(grade_grid_tab)
        self.grade_grid_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.save_grades_button = ctk.CTkButton(grade_grid_tab, text="Salvar Todas as Alterações", command=self.save_all_grades)
        self.save_grades_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    # Método para salvar todas as notas inseridas ou alteradas no quadro de notas.
    def save_all_grades(self):
        # Lista para armazenar os dados das notas a serem salvas (upsert).
        grades_to_upsert = []
        # Itera sobre os widgets de entrada de nota que foram criados.
        for (student_id, assessment_id), entry_widget in self.grade_entries.items():
            score_str = entry_widget.get()
            # Ignora campos de nota vazios.
            if not score_str:
                continue

            try:
                # Tenta converter o valor para um número float.
                score = float(score_str)
                # Valida se a nota está no intervalo permitido (0 a 10).
                if not (0 <= score <= 10):
                    messagebox.showerror("Nota Inválida", f"Nota inválida '{score}'. As notas devem ser entre 0 e 10.")
                    return # Interrompe a operação se uma nota for inválida.
                # Adiciona a nota válida à lista.
                grades_to_upsert.append({'student_id': student_id, 'assessment_id': assessment_id, 'score': score})
            except ValueError:
                # Se a conversão para float falhar.
                messagebox.showerror("Nota Inválida", f"Nota inválida '{score_str}'. As notas devem ser numéricas.")
                return

        # Se não houver notas para salvar, informa o usuário.
        if not grades_to_upsert:
            messagebox.showinfo("Nenhuma Mudança", "Nenhuma nota nova ou modificada para salvar.")
            return

        # Chama o DataService para salvar os dados em lote.
        data_service.upsert_grades_for_class(self.class_id, grades_to_upsert)

        messagebox.showinfo("Sucesso", "Todas as notas foram salvas com sucesso.")
        # Atualiza o quadro de notas para recalcular e exibir as médias.
        self.populate_grade_grid()

    # Método para construir e preencher o quadro de notas.
    def populate_grade_grid(self):
        # Limpa todos os widgets existentes no frame do quadro.
        for widget in self.grade_grid_frame.winfo_children():
            widget.destroy()

        if not self.class_id: return

        # Busca os dados necessários do banco.
        enrollments = data_service.get_enrollments_for_class(self.class_id)

        # Filtra por alunos ativos se o checkbox estiver marcado.
        if self.show_active_only_grades_checkbox.get():
            enrollments = [e for e in enrollments if e['status'] == 'Active']

        class_data = data_service.get_class_by_id(self.class_id)
        assessments = class_data['assessments'] if class_data else []

        # Cria o cabeçalho da tabela.
        headers = ["Nome do Aluno"] + [a['name'] for a in assessments] + ["Média Final"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(self.grade_grid_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=col, padx=5, pady=5, sticky="w")

        # Cria as linhas, uma para cada aluno.
        # Dicionário para guardar a referência dos widgets de entrada de nota.
        self.grade_entries = {}
        grades = data_service.get_grades_for_class(self.class_id)

        for row, enrollment in enumerate(enrollments, start=1):
            student_name = f"{enrollment['student_first_name']} {enrollment['student_last_name']}"
            name_label = ctk.CTkLabel(self.grade_grid_frame, text=student_name)
            name_label.grid(row=row, column=0, padx=5, pady=5, sticky="w")

            # Cria os campos de entrada para cada avaliação.
            for col, assessment in enumerate(assessments, start=1):
                entry = ctk.CTkEntry(self.grade_grid_frame, width=80)
                entry.grid(row=row, column=col, padx=5, pady=5)

                # Procura a nota existente para este aluno e avaliação.
                existing_grade = next((g for g in grades if g['student_id'] == enrollment['student_id'] and g['assessment_id'] == assessment['id']), None)
                if existing_grade:
                    # Se existir, preenche o campo com o valor.
                    entry.insert(0, str(existing_grade['score']))

                # Armazena a referência do widget de entrada.
                self.grade_entries[(enrollment['student_id'], assessment['id'])] = entry

            # Calcula e exibe a média final ponderada do aluno.
            average = data_service.calculate_weighted_average(enrollment['student_id'], grades, assessments)
            average_label = ctk.CTkLabel(self.grade_grid_frame, text=f"{average:.2f}")
            average_label.grid(row=row, column=len(assessments) + 1, padx=5, pady=5, sticky="w")

    # Abre o pop-up para adicionar um novo incidente.
    def add_incident_popup(self):
        if not self.class_id: return

        # Busca os alunos matriculados para preencher o dropdown.
        enrollments = data_service.get_enrollments_for_class(self.class_id)
        student_names = [f"{e['student_first_name']} {e['student_last_name']}" for e in enrollments]

        if not student_names:
            messagebox.showwarning("Aviso", "Nenhum aluno nesta turma para registrar um incidente.")
            return

        # Função de callback que será chamada pelo diálogo ao salvar.
        def save_callback(data):
            student_name = data["student"]
            description = data["description"]
            # Encontra o objeto de matrícula correspondente ao nome do aluno selecionado.
            selected_enrollment = next((e for e in enrollments if f"{e['student_first_name']} {e['student_last_name']}" == student_name), None)

            if selected_enrollment and description:
                # Chama o serviço para criar o incidente no banco de dados.
                data_service.create_incident(self.class_id, selected_enrollment['student_id'], description, date.today())
                # Atualiza a lista de incidentes na tela.
                self.populate_incident_list()

        # Configuração dos campos para o diálogo genérico.
        fields = {"description": "Descrição"}
        dropdowns = {"student": ("Aluno", student_names)}
        AddDialog(self, "Adicionar Novo Incidente", fields=fields, dropdowns=dropdowns, save_callback=save_callback)

    # Preenche a lista de incidentes na respectiva aba.
    def populate_incident_list(self):
        for widget in self.incident_list_frame.winfo_children(): widget.destroy()
        if not self.class_id: return

        incidents = data_service.get_incidents_for_class(self.class_id)

        # Cria cabeçalhos.
        headers = ["Nome do Aluno", "Data", "Descrição"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.incident_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        # Cria as linhas com os dados dos incidentes.
        for i, incident in enumerate(incidents, start=1):
            student_name = f"{incident['student_first_name']} {incident['student_last_name']}"
            ctk.CTkLabel(self.incident_list_frame, text=student_name).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.incident_list_frame, text=incident['date']).grid(row=i, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.incident_list_frame, text=incident['description'], wraplength=400, justify="left").grid(row=i, column=2, padx=10, pady=5, sticky="w")

    # Mostra a view de edição/criação de aula.
    def show_lesson_editor(self, lesson=None):
        # Armazena o ID da aula se estiver em modo de edição.
        self.editing_lesson_id = lesson['id'] if lesson else None
        # Esconde a lista de aulas e mostra o editor.
        self.lesson_list_view.grid_forget()
        self.lesson_editor_view.grid(row=0, column=0, sticky="nsew")

        # Limpa os campos do editor.
        self.lesson_editor_title_entry.delete(0, "end")
        self.lesson_editor_date_entry.delete(0, "end")
        self.lesson_editor_content_textbox.delete("1.0", "end")

        # Se estiver editando, preenche os campos com os dados da aula.
        if lesson:
            self.lesson_editor_title_entry.insert(0, lesson['title'])
            self.lesson_editor_date_entry.insert(0, lesson['date'])
            self.lesson_editor_content_textbox.insert("1.0", lesson['content'] or "")
        # Se estiver criando, preenche a data com o dia de hoje.
        else:
            self.lesson_editor_date_entry.insert(0, date.today().isoformat())

    # Esconde a view de edição de aula e volta para a lista.
    def hide_lesson_editor(self):
        self.editing_lesson_id = None
        self.lesson_editor_view.grid_forget()
        self.lesson_list_view.grid(row=0, column=0, sticky="nsew")

    # Salva os dados da aula (criação ou atualização).
    def save_lesson(self):
        title = self.lesson_editor_title_entry.get()
        content = self.lesson_editor_content_textbox.get("1.0", "end-1c")
        date_str = self.lesson_editor_date_entry.get()

        if not title or not date_str:
            messagebox.showerror("Erro", "Título e Data são obrigatórios.")
            return

        try:
            lesson_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use AAAA-MM-DD.")
            return

        # Se estiver editando, chama o método de atualização.
        if self.editing_lesson_id:
            data_service.update_lesson(self.editing_lesson_id, title, content, lesson_date)
        # Caso contrário, chama o método de criação.
        else:
            data_service.create_lesson(self.class_id, title, content, lesson_date)

        # Atualiza a lista de aulas e esconde o editor.
        self.populate_lesson_list()
        self.hide_lesson_editor()

    # Abre o pop-up para adicionar uma nova avaliação.
    def add_assessment_popup(self):
        if not self.class_id: return

        def save_callback(data):
            name = data.get("name")
            weight_str = data.get("weight")
            if name and weight_str:
                try:
                    weight = float(weight_str)
                    data_service.add_assessment(self.class_id, name, weight)
                    self.populate_assessment_list()
                except ValueError:
                    messagebox.showerror("Erro", "Peso inválido. Por favor, insira um número.")

        fields = {"name": "Nome da Avaliação", "weight": "Peso"}
        AddDialog(self, "Adicionar Nova Avaliação", fields=fields, save_callback=save_callback)

    # Preenche a lista de avaliações.
    def populate_assessment_list(self):
        for widget in self.assessment_list_frame.winfo_children(): widget.destroy()
        if not self.class_id: return

        class_data = data_service.get_class_by_id(self.class_id)
        if not class_data: return

        headers = ["Nome da Avaliação", "Peso", "Ações"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.assessment_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, assessment in enumerate(class_data['assessments'], start=1):
            ctk.CTkLabel(self.assessment_list_frame, text=assessment['name']).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.assessment_list_frame, text=str(assessment['weight'])).grid(row=i, column=1, padx=10, pady=5, sticky="w")

            actions_frame = ctk.CTkFrame(self.assessment_list_frame)
            actions_frame.grid(row=i, column=2, padx=5, pady=5, sticky="e")

            edit_button = ctk.CTkButton(actions_frame, text="Editar", command=lambda a=assessment: self.edit_assessment_popup(a))
            edit_button.pack(side="left", padx=5)

            delete_button = ctk.CTkButton(actions_frame, text="Excluir", fg_color="red", command=lambda a_id=assessment['id']: self.delete_assessment_action(a_id))
            delete_button.pack(side="left", padx=5)

    # Ação de deletar uma avaliação após confirmação.
    def delete_assessment_action(self, assessment_id):
        dialog = CTkInputDialog(text="Digite 'DELETE' para confirmar a exclusão:", title="Confirmar Exclusão")
        user_input = dialog.get_input()
        if user_input == "DELETE":
            data_service.delete_assessment(assessment_id)
            self.populate_assessment_list()

    # Abre o pop-up para editar uma avaliação.
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
                    messagebox.showerror("Erro", "Peso inválido. Por favor, insira um número.")

        fields = {"name": "Nome da Avaliação", "weight": "Peso"}
        initial_data = {"id": assessment['id'], "name": assessment['name'], "weight": str(assessment['weight'])}
        EditDialog(self, "Editar Avaliação", fields, initial_data, save_callback)

    # Abre o pop-up para matricular um aluno existente na turma.
    def enroll_student_popup(self):
        if not self.class_id: return

        unenrolled_students = data_service.get_unenrolled_students(self.class_id)
        student_names = [f"{s['first_name']} {s['last_name']}" for s in unenrolled_students]

        if not student_names:
            messagebox.showinfo("Aviso", "Nenhum aluno disponível para matricular.")
            return

        def save_callback(data):
            student_name = data["student"]
            student = next((s for s in unenrolled_students if f"{s['first_name']} {s['last_name']}" == student_name), None)

            if student:
                next_call_number = data_service.get_next_call_number(self.class_id)
                data_service.add_student_to_class(student['id'], self.class_id, next_call_number)
                self.populate_student_list()

        dropdowns = {"student": ("Aluno", student_names)}
        AddDialog(self, "Matricular Novo Aluno", fields={}, dropdowns=dropdowns, save_callback=save_callback)

    # Preenche a lista de alunos matriculados.
    def populate_student_list(self):
        for widget in self.student_list_frame.winfo_children(): widget.destroy()
        if not self.class_id: return

        enrollments = data_service.get_enrollments_for_class(self.class_id)

        # Filtra por alunos ativos se o checkbox estiver marcado.
        if self.show_active_only_checkbox.get():
            enrollments = [e for e in enrollments if e['status'] == 'Active']

        headers = ["Nº de Chamada", "Nome do Aluno", "Data de Nascimento", "Status", "Ações"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.student_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, enrollment in enumerate(enrollments, start=1):
            ctk.CTkLabel(self.student_list_frame, text=str(enrollment['call_number'])).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.student_list_frame, text=f"{enrollment['student_first_name']} {enrollment['student_last_name']}").grid(row=i, column=1, padx=10, pady=5, sticky="w")

            birth_date_str = ""
            if enrollment['student_birth_date']:
                try:
                    birth_date = datetime.strptime(enrollment['student_birth_date'], '%Y-%m-%d')
                    birth_date_str = birth_date.strftime("%d/%m/%Y")
                except (ValueError, TypeError):
                    birth_date_str = "Data Inválida"
            ctk.CTkLabel(self.student_list_frame, text=birth_date_str).grid(row=i, column=2, padx=10, pady=5, sticky="w")

            display_status = self.status_map_rev.get(enrollment['status'], enrollment['status'])
            ctk.CTkLabel(self.student_list_frame, text=display_status).grid(row=i, column=3, padx=10, pady=5, sticky="w")

            status_menu = ctk.CTkOptionMenu(self.student_list_frame, values=["Ativo", "Inativo"],
                                            command=lambda status, eid=enrollment['id']: self.update_status(eid, status))
            status_menu.set(display_status)
            status_menu.grid(row=i, column=4, padx=10, pady=5, sticky="w")

    # Atualiza o status de uma matrícula.
    def update_status(self, enrollment_id, status):
        db_status = self.status_map.get(status, status)
        data_service.update_enrollment_status(enrollment_id, db_status)
        self.populate_student_list()

    # Inicia o processo de importação de alunos via CSV.
    def import_students(self):
        if not self.class_id:
            messagebox.showerror("Erro", "Selecione uma turma antes de importar alunos.")
            return

        filepath = filedialog.askopenfilename(
            title="Selecione um arquivo CSV de Alunos",
            filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*"))
        )
        if not filepath: return

        # Desabilita botões e mostra feedback de "importando...".
        self.import_button.configure(state="disabled", text="Importando...")
        self.enroll_student_button.configure(state="disabled")

        # Cria a coroutine para a importação assíncrona.
        coro = async_import_students(filepath, self.class_id, self.main_app.data_service)
        # Executa a coroutine em segundo plano.
        run_async_task(coro, self.main_app.loop, self.main_app.async_queue, self._on_import_complete)

    # Callback executado na thread principal após a conclusão da importação.
    def _on_import_complete(self, result):
        """Callback executado na thread principal da UI após a conclusão da tarefa de importação."""
        # Reabilita os botões.
        self.import_button.configure(state="normal", text="Importar Alunos (.csv)")
        self.enroll_student_button.configure(state="normal")

        # Se o resultado for uma exceção, mostra um erro.
        if isinstance(result, Exception):
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro fatal durante a importação:\n\n{result}")
            return

        # Desempacota o resultado.
        success_count, errors = result
        # Atualiza a lista de alunos na tela.
        self.populate_student_list()

        # Mostra um relatório de sucesso ou de erros.
        if errors:
            error_message = f"{success_count} alunos importados com sucesso, mas ocorreram os seguintes erros:\n\n" + "\n".join(errors)
            messagebox.showwarning("Importação com Erros", error_message)
        else:
            messagebox.showinfo("Sucesso", f"{success_count} alunos importados com sucesso!")

    # Preenche a lista de aulas.
    def populate_lesson_list(self):
        for widget in self.lesson_list_frame.winfo_children(): widget.destroy()
        if not self.class_id: return

        lessons = data_service.get_lessons_for_class(self.class_id)

        headers = ["Data", "Título", "Ações"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.lesson_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for i, lesson in enumerate(lessons, start=1):
            ctk.CTkLabel(self.lesson_list_frame, text=lesson['date']).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.lesson_list_frame, text=lesson['title']).grid(row=i, column=1, padx=10, pady=5, sticky="w")
            edit_button = ctk.CTkButton(self.lesson_list_frame, text="Editar", command=lambda l=lesson: self.show_lesson_editor(l))
            edit_button.grid(row=i, column=2, padx=10, pady=5, sticky="e")

    # Método chamado quando esta view é exibida.
    def on_show(self, class_id=None):
        self.class_id = class_id
        if class_id:
            # Atualiza o título e preenche todas as listas/quadros com os dados da turma selecionada.
            class_data = data_service.get_class_by_id(self.class_id)
            self.title_label.configure(text=f"Detalhes da Turma: {class_data['name']}")
            self.populate_student_list()
            self.populate_assessment_list()
            self.populate_lesson_list()
            self.populate_incident_list()
            self.populate_grade_grid()
