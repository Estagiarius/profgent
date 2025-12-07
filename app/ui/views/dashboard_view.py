# Importa a biblioteca 'customtkinter' para os componentes da interface.
import customtkinter as ctk
# Importa a função utilitária que gera o gráfico de distribuição de notas.
from app.utils.charts import create_grade_distribution_chart, create_approval_pie_chart
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

        # --- Sistema de Abas (Visão Geral e Por Disciplina) ---
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, rowspan=2, padx=20, pady=10, sticky="nsew")

        # Aba de Visão Geral
        self.tab_overview = self.tabview.add("Visão Geral")
        self.setup_overview_tab()

        # Aba de Análise por Disciplina
        self.tab_analysis = self.tabview.add("Por Disciplina")
        self.setup_analysis_tab()

        # --- Frame de Aniversariantes ---
        self.birthdays_frame_container = ctk.CTkFrame(self)
        self.birthdays_frame_container.grid(row=1, column=1, rowspan=2, padx=(0, 20), pady=10, sticky="nsew")
        self.birthdays_frame_container.grid_rowconfigure(1, weight=1)
        self.birthdays_frame_container.grid_columnconfigure(0, weight=1)

        self.birthdays_title = ctk.CTkLabel(self.birthdays_frame_container, text="Aniversariantes do Dia", font=ctk.CTkFont(size=16, weight="bold"))
        self.birthdays_title.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.birthdays_scrollable_frame = ctk.CTkScrollableFrame(self.birthdays_frame_container, label_text="")
        self.birthdays_scrollable_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def setup_overview_tab(self):
        """Configura os elementos da aba Visão Geral."""
        self.tab_overview.grid_columnconfigure(0, weight=1)
        self.tab_overview.grid_columnconfigure(1, weight=1)
        self.tab_overview.grid_rowconfigure(1, weight=1)

        # Cards de Estatísticas
        self.stats_frame = ctk.CTkFrame(self.tab_overview)
        self.stats_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Grid para os cards dentro do frame
        self.stats_frame.grid_columnconfigure((0, 1), weight=1)

        self.card_students = self._create_stat_card(self.stats_frame, "Alunos Ativos", "0", 0, 0)
        self.card_classes = self._create_stat_card(self.stats_frame, "Turmas", "0", 0, 1)
        self.card_courses = self._create_stat_card(self.stats_frame, "Disciplinas", "0", 1, 0)
        self.card_incidents = self._create_stat_card(self.stats_frame, "Incidentes", "0", 1, 1)

        # Seção de Aprovação Global
        self.approval_frame = ctk.CTkFrame(self.tab_overview)
        self.approval_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=20, sticky="nsew")

        # Layout: Coluna 0 (Texto), Coluna 1 (Gráfico Pizza)
        self.approval_frame.grid_columnconfigure(0, weight=1)
        self.approval_frame.grid_columnconfigure(1, weight=1)

        # -- Coluna 0: Texto e Botão --
        text_container = ctk.CTkFrame(self.approval_frame, fg_color="transparent")
        text_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(text_container, text="Índice Global de Aprovação\n(Média >= 5.0)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))

        self.approval_label = ctk.CTkLabel(text_container, text="--%", font=ctk.CTkFont(size=40, weight="bold"))
        self.approval_label.pack(pady=10)

        self.approval_detail_label = ctk.CTkLabel(text_container, text="Aprovados: 0 | Abaixo da Média: 0", text_color="gray")
        self.approval_detail_label.pack(pady=(0, 20))

        self.btn_details = ctk.CTkButton(text_container, text="Ver Alunos em Risco", command=self.open_risk_details_dialog, fg_color="red", hover_color="#d32f2f")
        self.btn_details.pack(pady=10)

        # -- Coluna 1: Gráfico Pizza --
        self.pie_chart_container = ctk.CTkFrame(self.approval_frame, fg_color="transparent")
        self.pie_chart_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.pie_chart_label = ctk.CTkLabel(self.pie_chart_container, text="")
        self.pie_chart_label.pack(expand=True)
        self.pie_chart_image = None # Prevent GC

        # Armazena os dados detalhados para o modal
        self.failed_details_data = []

    def open_risk_details_dialog(self):
        """Abre um modal com a lista de alunos abaixo da média."""
        if not self.failed_details_data:
            from tkinter import messagebox
            messagebox.showinfo("Informação", "Não há alunos abaixo da média no momento.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Alunos em Risco (Média < 5.0)")
        dialog.geometry("500x400")
        dialog.transient(self) # Faz a janela ser filha da principal
        dialog.grab_set() # Foca na janela

        # Cabeçalho
        ctk.CTkLabel(dialog, text="Alunos Abaixo da Média", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        # Scrollable list
        scroll_frame = ctk.CTkScrollableFrame(dialog)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        for i, item in enumerate(self.failed_details_data):
            row_frame = ctk.CTkFrame(scroll_frame)
            row_frame.pack(fill="x", pady=2)

            # Format: Nome - Disciplina (Turma): Nota
            text = f"{item['student_name']} - {item['course_name']} ({item['class_name']})"
            score_text = f"Média: {item['average']}"

            ctk.CTkLabel(row_frame, text=text, anchor="w").pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(row_frame, text=score_text, text_color="red", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10, pady=5)

    def _create_stat_card(self, parent, title, value, row, col):
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(pady=(10, 0))
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold"))
        value_label.pack(pady=(0, 10))
        return value_label

    def setup_analysis_tab(self):
        """Configura os elementos da aba Análise por Disciplina."""
        self.tab_analysis.grid_columnconfigure(0, weight=1)
        self.tab_analysis.grid_rowconfigure(1, weight=1)

        # Frame de Controles
        self.controls_frame = ctk.CTkFrame(self.tab_analysis)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.course_label = ctk.CTkLabel(self.controls_frame, text="Selecione a Disciplina:")
        self.course_label.pack(side="left", padx=10, pady=10)

        self.course_menu = ctk.CTkOptionMenu(self.controls_frame, values=[], command=self.on_course_select)
        self.course_menu.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        # Frame do Gráfico
        self.chart_frame = ctk.CTkFrame(self.tab_analysis)
        self.chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.chart_label = ctk.CTkLabel(self.chart_frame, text="Selecione um curso para ver a distribuição de médias.")
        self.chart_label.pack(expand=True, fill="both")
        self.chart_image = None

    # Método chamado sempre que a view é exibida.
    def on_show(self, **kwargs):
        _ = kwargs
        # Carrega dados globais
        self.update_global_stats()
        # Carrega (ou recarrega) a lista de cursos.
        self.load_courses()
        # Atualiza o gráfico com base na seleção atual.
        self.update_chart()
        # Atualiza a lista de aniversariantes.
        self.update_birthdays()

    def update_global_stats(self):
        """Atualiza os cards e estatísticas da aba Visão Geral."""
        stats = self.data_service.get_global_dashboard_stats()
        self.card_students.configure(text=str(stats.get('active_students', 0)))
        self.card_classes.configure(text=str(stats.get('total_classes', 0)))
        self.card_courses.configure(text=str(stats.get('total_courses', 0)))
        self.card_incidents.configure(text=str(stats.get('total_incidents', 0)))

        perf = self.data_service.get_global_performance_stats()
        approval_rate = perf.get('approval_rate', 0.0)
        approved = perf.get('approved', 0)
        failed = perf.get('failed', 0)
        self.failed_details_data = perf.get('failed_details', [])

        color = "green" if approval_rate >= 70 else "orange" if approval_rate >= 50 else "red"
        self.approval_label.configure(text=f"{approval_rate:.1f}%", text_color=color)
        self.approval_detail_label.configure(text=f"Aprovados: {approved} | Abaixo da Média: {failed}")

        # Atualiza o gráfico de Pizza
        pie_chart_path = create_approval_pie_chart(approved, failed)
        if os.path.exists(pie_chart_path):
            img = Image.open(pie_chart_path)
            self.pie_chart_image = ctk.CTkImage(light_image=img, size=img.size)
            self.pie_chart_label.configure(image=self.pie_chart_image, text="")
        else:
             self.pie_chart_label.configure(image=None, text="Erro no Gráfico")

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
        """Gera e exibe o gráfico com as médias finais dos alunos para o curso selecionado."""
        # Se nenhum curso estiver selecionado, exibe uma mensagem.
        if self.selected_course_id is None:
            self.chart_label.configure(text="Nenhum curso selecionado ou disponível.", image=None)
            return

        # Busca os detalhes do curso selecionado
        selected_course = self.data_service.get_course_by_id(self.selected_course_id)
        if not selected_course:
            self.chart_label.configure(text=f"Não foi possível encontrar o curso com ID: {self.selected_course_id}", image=None)
            return

        # Busca as médias calculadas (ao invés de notas brutas)
        averages = self.data_service.get_course_averages(self.selected_course_id)

        # Chama a função utilitária para gerar o gráfico de médias.
        chart_path = create_grade_distribution_chart(averages, selected_course['course_name'])

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
            card = ctk.CTkFrame(self.birthdays_scrollable_frame)
            card.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(card, text=student["name"], font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5, 0))
            ctk.CTkLabel(card, text=f"Completando {student['age']} anos").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"{student['class_name']}", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=10, pady=(0, 5))
