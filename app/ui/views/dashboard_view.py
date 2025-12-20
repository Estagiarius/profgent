import customtkinter as ctk # Importa a biblioteca 'customtkinter' para os componentes da interface.
import asyncio
# Importa utilitário de rolagem
from app.ui.ui_utils import bind_global_mouse_scroll
from app.utils.async_utils import run_async_task
from app.utils.charts import create_grade_distribution_chart, create_approval_pie_chart # Importa a função utilitária que gera o gráfico de distribuição de notas.
from PIL import Image # Importa a biblioteca Pillow (PIL) para manipulação de imagens.
import os # Importa o módulo 'os' para interagir com o sistema de arquivos (verificar se o arquivo do gráfico existe).

# Define a classe para a tela do Dashboard.
class DashboardView(ctk.CTkFrame):
    # Método construtor.
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.data_service = self.main_app.data_service # Obtém a instância do DataService a partir da aplicação principal.
        self.courses = [] # Lista para armazenar os cursos carregados do banco.
        self.selected_course_id = None # ID do curso atualmente selecionado no dropdown.

        # Configura o layout de grade da view.
        self.grid_columnconfigure(0, weight=3) # Coluna do gráfico (maior)
        self.grid_columnconfigure(1, weight=1) # Coluna dos aniversariantes (menor)
        self.grid_rowconfigure(1, weight=1) # Linha 1 (Abas) se expande
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

        # Aba de Rankings e Destaques (Nova)
        self.tab_rankings = self.tabview.add("Destaques & Alertas")
        self.setup_rankings_tab()

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
        bind_global_mouse_scroll(self.birthdays_scrollable_frame)

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
        self.honor_roll_data = []

    def setup_rankings_tab(self):
        """Configura os elementos da aba de Destaques e Alertas."""
        self.tab_rankings.grid_columnconfigure(0, weight=1)
        self.tab_rankings.grid_columnconfigure(1, weight=1)
        self.tab_rankings.grid_rowconfigure(0, weight=1)

        # --- Quadro de Honra (Coluna 0) ---
        self.honor_frame = ctk.CTkFrame(self.tab_rankings)
        self.honor_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.honor_frame, text="Quadro de Honra (Média >= 9.0)", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=10)

        self.honor_count_label = ctk.CTkLabel(self.honor_frame, text="0 Alunos Destaque", font=ctk.CTkFont(size=14), text_color="#FFD700")
        self.honor_count_label.pack(pady=5)

        # Lista de Alunos Destaque (Embedded)
        self.honor_list_frame = ctk.CTkScrollableFrame(self.honor_frame)
        self.honor_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        bind_global_mouse_scroll(self.honor_list_frame)

        # --- Ranking de Incidentes (Coluna 1) ---
        self.incidents_frame = ctk.CTkFrame(self.tab_rankings)
        self.incidents_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.incidents_frame, text="Top Incidentes por Turma", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=10)

        # Lista de Incidentes (Embedded)
        self.incidents_list_frame = ctk.CTkScrollableFrame(self.incidents_frame)
        self.incidents_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        bind_global_mouse_scroll(self.incidents_list_frame)


    def open_risk_details_dialog(self):
        """Abre um modal com a lista de alunos abaixo da média."""
        self._show_student_list_modal("Alunos em Risco (Média < 5.0)", self.failed_details_data, "red")

    def _show_student_list_modal(self, title, data, score_color):
        if not data:
            from tkinter import messagebox
            messagebox.showinfo("Informação", "Nenhum aluno nesta categoria no momento.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("500x400")
        dialog.transient(self)
        
        # Aguarda a janela estar pronta
        dialog.wait_visibility()
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(dialog)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        bind_global_mouse_scroll(scroll_frame)

        for item in data:
            row_frame = ctk.CTkFrame(scroll_frame)
            row_frame.pack(fill="x", pady=2)

            text = f"{item['student_name']} - {item['course_name']} ({item['class_name']})"
            score_text = f"Média: {item['average']}"

            ctk.CTkLabel(row_frame, text=text, anchor="w").pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(row_frame, text=score_text, text_color=score_color, font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10, pady=5)

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
        self.pie_chart_container = ctk.CTkFrame(self.approval_frame, fg_color="#DCB538")
        self.pie_chart_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.pie_chart_label = ctk.CTkLabel(self.pie_chart_container, text="")
        self.pie_chart_label.pack(expand=True)
        self.pie_chart_image = None # Prevent GC

        # Armazena os dados detalhados para o modal
        self.failed_details_data = []
        self.honor_roll_data = []
    # Método chamado sempre que a view é exibida.
    def on_show(self, **kwargs):
        _ = kwargs
        # Carrega dados globais de forma assíncrona
        self.update_global_stats()
        # Carrega (ou recarrega) a lista de cursos.
        self.load_courses()
        # Atualiza o gráfico com base na seleção atual (assíncrono).
        self.update_chart()
        # Atualiza a lista de aniversariantes (assíncrono).
        self.update_birthdays()

    def update_global_stats(self):
        """Dispara a atualização assíncrona dos cards e estatísticas."""
        # Feedback visual de carregamento
        self.approval_label.configure(text="...", text_color="gray")
        self.honor_count_label.configure(text="Carregando...")
        self.pie_chart_label.configure(image=None, text="Carregando...")

        async def fetch_task():
            # Executa as operações pesadas em threads separadas para não travar a UI
            stats = await asyncio.to_thread(self.data_service.get_global_dashboard_stats)
            perf = await asyncio.to_thread(self.data_service.get_global_performance_stats)

            approved = perf.get('approved', 0)
            failed = perf.get('failed', 0)
            # Geração do gráfico de pizza é pesada (matplotlib)
            pie_path = await asyncio.to_thread(create_approval_pie_chart, approved, failed)

            ranking = await asyncio.to_thread(self.data_service.get_class_incident_ranking)

            return {
                "stats": stats,
                "perf": perf,
                "pie_path": pie_path,
                "ranking": ranking
            }

        run_async_task(fetch_task(), self.main_app.loop, self.main_app.async_queue, self._on_global_stats_loaded)

    def _on_global_stats_loaded(self, result):
        """Callback executado na thread principal com os dados globais."""
        if isinstance(result, Exception):
            print(f"Erro ao carregar stats: {result}")
            self.approval_label.configure(text="Erro")
            return

        stats = result['stats']
        perf = result['perf']
        pie_path = result['pie_path']
        ranking = result['ranking']

        # Atualiza Cards
        self.card_students.configure(text=str(stats.get('active_students', 0)))
        self.card_classes.configure(text=str(stats.get('total_classes', 0)))
        self.card_courses.configure(text=str(stats.get('total_courses', 0)))
        self.card_incidents.configure(text=str(stats.get('total_incidents', 0)))

        # Atualiza Aprovação
        approval_rate = perf.get('approval_rate', 0.0)
        approved = perf.get('approved', 0)
        failed = perf.get('failed', 0)
        self.failed_details_data = perf.get('failed_details', [])
        self.honor_roll_data = perf.get('honor_roll_details', [])

        color = "green" if approval_rate >= 70 else "orange" if approval_rate >= 50 else "red"
        self.approval_label.configure(text=f"{approval_rate:.1f}%", text_color=color)
        self.approval_detail_label.configure(text=f"Aprovados: {approved} | Abaixo da Média: {failed}")

        # Atualiza Honor Roll (Aba Destaques)
        self.honor_count_label.configure(text=f"{len(self.honor_roll_data)} Alunos Destaque")

        # Limpa e popula lista de Honra
        for widget in self.honor_list_frame.winfo_children():
            widget.destroy()

        if not self.honor_roll_data:
             ctk.CTkLabel(self.honor_list_frame, text="Nenhum aluno em destaque.", text_color="gray").pack(pady=5)
        else:
            for item in self.honor_roll_data:
                row = ctk.CTkFrame(self.honor_list_frame)
                row.pack(fill="x", pady=2)
                text = f"{item['student_name']} - {item['course_name']}"
                score_text = f"{item['average']}"
                ctk.CTkLabel(row, text=text, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=score_text, text_color="#FFD700", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=5)

        # Atualiza o gráfico de Pizza
        if os.path.exists(pie_path):
            img = Image.open(pie_path)
            self.pie_chart_image = ctk.CTkImage(light_image=img, size=img.size)
            self.pie_chart_label.configure(image=self.pie_chart_image, text="")
        else:
             self.pie_chart_label.configure(image=None, text="Erro no Gráfico")

        # Atualiza Ranking de Incidentes
        # Clear previous widgets
        for widget in self.incidents_list_frame.winfo_children():
            widget.destroy()

        if not ranking:
             ctk.CTkLabel(self.incidents_list_frame, text="Nenhum incidente registrado.", text_color="gray").pack(pady=5)
        else:
            for i, item in enumerate(ranking):
                row = ctk.CTkFrame(self.incidents_list_frame)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=f"{i+1}. {item['class_name']}", anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=f"{item['count']} incidentes", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=5)

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

    # Gera e exibe o gráfico para o curso selecionado (Assíncrono).
    def update_chart(self):
        """Gera e exibe o gráfico com as médias finais dos alunos para o curso selecionado."""
        if self.selected_course_id is None:
            self.chart_label.configure(text="Nenhum curso selecionado ou disponível.", image=None)
            return

        self.chart_label.configure(image=None, text="Gerando gráfico...")

        async def chart_task():
            # Busca os detalhes do curso selecionado (DB Call)
            selected_course = await asyncio.to_thread(self.data_service.get_course_by_id, self.selected_course_id)
            if not selected_course: return None

            # Busca as médias calculadas (DB Call)
            averages = await asyncio.to_thread(self.data_service.get_course_averages, self.selected_course_id)

            # Chama a função utilitária para gerar o gráfico de médias (Matplotlib - Slow)
            chart_path = await asyncio.to_thread(create_grade_distribution_chart, averages, selected_course['course_name'])
            return chart_path

        run_async_task(chart_task(), self.main_app.loop, self.main_app.async_queue, self._on_chart_loaded)

    def _on_chart_loaded(self, chart_path):
        if not chart_path:
            self.chart_label.configure(text="Erro ao carregar curso.", image=None)
            return

        if isinstance(chart_path, Exception):
             self.chart_label.configure(text=f"Erro: {chart_path}", image=None)
             return

        if os.path.exists(chart_path):
            img = Image.open(chart_path)
            self.chart_image = ctk.CTkImage(light_image=img, size=img.size)
            self.chart_label.configure(image=self.chart_image, text="")
        else:
            self.chart_label.configure(image=None, text="Não foi possível gerar o gráfico.")

    # Atualiza a lista de aniversariantes do dia (Assíncrono).
    def update_birthdays(self):
        # Limpa os widgets anteriores no frame de scroll.
        for widget in self.birthdays_scrollable_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.birthdays_scrollable_frame, text="Carregando...").pack(pady=10)

        async def birthday_task():
            return await asyncio.to_thread(self.data_service.get_students_with_birthday_today)

        run_async_task(birthday_task(), self.main_app.loop, self.main_app.async_queue, self._on_birthdays_loaded)

    def _on_birthdays_loaded(self, birthdays):
        # Limpa o loading
        for widget in self.birthdays_scrollable_frame.winfo_children():
            widget.destroy()

        if isinstance(birthdays, Exception):
             ctk.CTkLabel(self.birthdays_scrollable_frame, text="Erro ao carregar.", text_color="red").pack(pady=20)
             return

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