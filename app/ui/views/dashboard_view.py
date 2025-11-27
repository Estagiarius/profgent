# Importa a biblioteca 'customtkinter' para os componentes da interface.
import customtkinter as ctk
# Importa a função utilitária que gera o gráfico de distribuição de notas.
from app.utils.charts import create_grade_distribution_chart
# Importa a biblioteca Pillow (PIL) para manipulação de imagens.
from PIL import Image
# Importa o módulo 'os' para interagir com o sistema de arquivos (verificar se o arquivo do gráfico existe).
import os

# Define a classe para a tela do Dashboard.
class DashboardView(ctk.CTkFrame):
    # Método construtor.
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        # Obtém a instância do DataService a partir da aplicação principal.
        self.data_service = self.main_app.data_service
        # Lista para armazenar os cursos carregados do banco.
        self.courses = []
        # ID do curso atualmente selecionado no dropdown.
        self.selected_course_id = None

        # Configura o layout de grade da view.
        self.grid_columnconfigure(0, weight=3) # Coluna do gráfico (maior)
        self.grid_columnconfigure(1, weight=1) # Coluna dos aniversariantes (menor)
        self.grid_rowconfigure(2, weight=1) # A linha 2 (onde fica o gráfico) se expande.

        # --- Título ---
        self.title_label = ctk.CTkLabel(self, text="Dashboard de Análises", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        # --- Frame de Controles ---
        # Frame para agrupar o rótulo e o menu de seleção de curso.
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.course_label = ctk.CTkLabel(self.controls_frame, text="Selecione a Disciplina para Análise:")
        self.course_label.pack(side="left", padx=10, pady=10)

        # Menu dropdown para selecionar o curso.
        self.course_menu = ctk.CTkOptionMenu(self.controls_frame, values=[], command=self.on_course_select)
        self.course_menu.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        # --- Frame de Exibição do Gráfico ---
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

        # Rótulo que exibirá a imagem do gráfico ou uma mensagem de texto.
        self.chart_label = ctk.CTkLabel(self.chart_frame, text="Selecione um curso para ver a distribuição de notas.")
        self.chart_label.pack(expand=True)
        # Referência para a imagem do gráfico para evitar que seja coletada pelo garbage collector.
        self.chart_image = None

        # --- Frame de Aniversariantes ---
        self.birthdays_frame_container = ctk.CTkFrame(self)
        self.birthdays_frame_container.grid(row=1, column=1, rowspan=2, padx=(0, 20), pady=10, sticky="nsew")
        self.birthdays_frame_container.grid_rowconfigure(1, weight=1)
        self.birthdays_frame_container.grid_columnconfigure(0, weight=1)

        self.birthdays_title = ctk.CTkLabel(self.birthdays_frame_container, text="Aniversariantes do Dia", font=ctk.CTkFont(size=16, weight="bold"))
        self.birthdays_title.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.birthdays_scrollable_frame = ctk.CTkScrollableFrame(self.birthdays_frame_container, label_text="")
        self.birthdays_scrollable_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    # Método chamado sempre que a view é exibida.
    def on_show(self, **kwargs):
        _ = kwargs
        # Carrega (ou recarrega) a lista de cursos.
        self.load_courses()
        # Atualiza o gráfico com base na seleção atual.
        self.update_chart()
        # Atualiza a lista de aniversariantes.
        self.update_birthdays()

    # Carrega os cursos do banco de dados e preenche o menu dropdown.
    def load_courses(self):
        """Carrega os cursos no menu dropdown."""
        self.courses = self.data_service.get_all_courses()
        course_names = [c['course_name'] for c in self.courses]

        # Se houver cursos...
        if course_names:
            # Configura o menu com os nomes dos cursos.
            self.course_menu.configure(values=course_names)
            # Se nenhum curso estiver selecionado, seleciona o primeiro da lista por padrão.
            if not self.selected_course_id:
                self.course_menu.set(course_names[0])
                self.on_course_select(course_names[0])
        # Se não houver cursos...
        else:
            self.course_menu.configure(values=["Nenhum curso disponível"])
            self.course_menu.set("Nenhum curso disponível")
            self.selected_course_id = None

    # Método chamado quando um curso é selecionado no menu.
    def on_course_select(self, selected_name: str):
        self.selected_course_id = None
        # Encontra o ID do curso correspondente ao nome selecionado.
        for course in self.courses:
            if course['course_name'] == selected_name:
                self.selected_course_id = course['id']
                break
        # Atualiza o gráfico com base na nova seleção.
        self.update_chart()

    # Gera e exibe o gráfico para o curso selecionado.
    def update_chart(self):
        """Gera e exibe o gráfico para o curso selecionado."""
        # Se nenhum curso estiver selecionado, exibe uma mensagem.
        if self.selected_course_id is None:
            self.chart_label.configure(text="Nenhum curso selecionado ou disponível.", image=None)
            return

        # Busca os detalhes do curso selecionado, incluindo suas turmas.
        selected_course = self.data_service.get_course_by_id(self.selected_course_id)
        if not selected_course:
            self.chart_label.configure(text=f"Não foi possível encontrar o curso com ID: {self.selected_course_id}", image=None)
            return

        # Agrega as notas de todas as turmas dentro do curso selecionado.
        all_grades = []
        for class_data in selected_course.get('classes', []):
            # Usa o ID do ClassSubject para buscar notas específicas desta disciplina nesta turma
            if 'class_subject_id' in class_data:
                grades_in_class = self.data_service.get_grades_for_subject(class_data['class_subject_id'])
                all_grades.extend(grades_in_class)

        # Chama a função utilitária para gerar o gráfico e obter o caminho do arquivo de imagem temporário.
        chart_path = create_grade_distribution_chart(all_grades, selected_course['course_name'])

        # Se o arquivo de imagem do gráfico foi criado com sucesso...
        if os.path.exists(chart_path):
            # Abre a imagem usando a biblioteca Pillow.
            img = Image.open(chart_path)
            # Cria um objeto de imagem compatível com o customtkinter.
            self.chart_image = ctk.CTkImage(light_image=img, size=img.size)
            # Configura o rótulo para exibir a imagem do gráfico.
            self.chart_label.configure(image=self.chart_image, text="")
        # Se o arquivo não foi criado...
        else:
            self.chart_label.configure(image=None, text="Não foi possível gerar o gráfico.")

    # Atualiza a lista de aniversariantes do dia.
    def update_birthdays(self):
        # Limpa os widgets anteriores no frame de scroll.
        for widget in self.birthdays_scrollable_frame.winfo_children():
            widget.destroy()

        # Busca os aniversariantes do dia.
        birthdays = self.data_service.get_students_with_birthday_today()

        if not birthdays:
            ctk.CTkLabel(self.birthdays_scrollable_frame, text="Nenhum aniversariante hoje.", text_color="gray").pack(pady=20)
            return

        # Cria um card para cada aniversariante.
        for student in birthdays:
            card = ctk.CTkFrame(self.birthdays_scrollable_frame, fg_color=("gray85", "gray25"))
            card.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(card, text=student["name"], font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5, 0))
            ctk.CTkLabel(card, text=f"Completando {student['age']} anos").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"{student['class_name']}", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=10, pady=(0, 5))
