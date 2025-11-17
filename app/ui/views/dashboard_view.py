import customtkinter as ctk
from app.utils.charts import create_grade_distribution_chart
from PIL import Image
import os

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.data_service = self.main_app.data_service
        self.courses = []
        self.selected_course_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Title ---
        self.title_label = ctk.CTkLabel(self, text="Dashboard de Análises", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # --- Controls Frame ---
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.course_label = ctk.CTkLabel(self.controls_frame, text="Selecione o Curso para Análise:")
        self.course_label.pack(side="left", padx=10, pady=10)

        self.course_menu = ctk.CTkOptionMenu(self.controls_frame, values=[], command=self.on_course_select)
        self.course_menu.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        # --- Chart Display Frame ---
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

        self.chart_label = ctk.CTkLabel(self.chart_frame, text="Selecione um curso para ver a distribuição de notas.")
        self.chart_label.pack(expand=True)
        self.chart_image = None

    def on_show(self, **kwargs):
        self.load_courses()
        self.update_chart()

    def load_courses(self):
        """Loads courses into the dropdown menu."""
        self.courses = self.data_service.get_all_courses()
        course_names = [c['course_name'] for c in self.courses]

        if course_names:
            self.course_menu.configure(values=course_names)
            if not self.selected_course_id:
                self.course_menu.set(course_names[0])
                self.on_course_select(course_names[0])
        else:
            self.course_menu.configure(values=["Nenhum curso disponível"])
            self.course_menu.set("Nenhum curso disponível")
            self.selected_course_id = None

    def on_course_select(self, selected_name: str):
        self.selected_course_id = None
        for course in self.courses:
            if course['course_name'] == selected_name:
                self.selected_course_id = course['id']
                break
        self.update_chart()

    def update_chart(self):
        """Generates and displays the chart for the selected course."""
        if self.selected_course_id is None:
            self.chart_label.configure(text="Nenhum curso selecionado ou disponível.", image=None)
            return

        selected_course = self.data_service.get_course_by_id(self.selected_course_id)
        if not selected_course:
            self.chart_label.configure(text=f"Não foi possível encontrar o curso com ID: {self.selected_course_id}", image=None)
            return

        # Aggregate grades from all classes within the selected course
        all_grades = []
        for class_data in selected_course['classes']:
            grades_in_class = self.data_service.get_grades_for_class(class_data['id'])
            all_grades.extend(grades_in_class)

        # Generate the chart and get the path to the temporary file
        chart_path = create_grade_distribution_chart(all_grades, selected_course['course_name'])

        if os.path.exists(chart_path):
            img = Image.open(chart_path)
            self.chart_image = ctk.CTkImage(light_image=img, size=img.size)
            self.chart_label.configure(image=self.chart_image, text="")
        else:
            self.chart_label.configure(image=None, text="Não foi possível gerar o gráfico.")
