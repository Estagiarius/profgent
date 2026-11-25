# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
import csv
import json
import os
from datetime import datetime
import matplotlib
# Configura backend Agg para geração em background sem travar a GUI
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from app.services.data_service import DataService
from app.services.data.grade_service import GradeService


class ReportService:
    """
    Serviço responsável pela geração de relatórios, gráficos e exportações.
    Centraliza a lógica utilizada tanto pela UI quanto pelo Assistente de IA.
    """

    REPORTS_DIR = "reports"

    def __init__(self, data_service: DataService = None, reports_dir: str = None):
        if data_service is None:
            from app.services import data_service as default_data_service
            self.data_service = default_data_service
        else:
            self.data_service = data_service
        self.reports_dir = reports_dir or self.REPORTS_DIR

    def _ensure_reports_dir(self):
        """Garante que o diretório de relatórios exista."""
        os.makedirs(self.reports_dir, exist_ok=True)

    def _get_file_path(self, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de relatório."""
        self._ensure_reports_dir()
        return os.path.join(self.reports_dir, filename)

    def generate_seating_chart(self, chart_id: int, fmt: str = "pdf") -> str:
        """
        Gera uma representação visual do mapa de sala no formato especificado ('pdf' ou 'svg').
        """
        return self._generate_seating_chart_plot(chart_id, fmt)

    def generate_seating_chart_pdf(self, chart_id: int) -> str:
        """Gera a visualização do mapa de sala em PDF."""
        return self.generate_seating_chart(chart_id, "pdf")

    def generate_seating_chart_svg(self, chart_id: int) -> str:
        """Gera a visualização do mapa de sala em SVG."""
        return self.generate_seating_chart(chart_id, "svg")

    def _generate_seating_chart_plot(self, chart_id: int, format: str) -> str:
        chart_details = self.data_service.get_seating_chart_details(chart_id)
        if not chart_details:
            raise ValueError("Mapa de sala não encontrado.")

        rows = chart_details['rows']
        cols = chart_details['columns']
        assignments = chart_details['assignments']
        try:
            layout_config = json.loads(chart_details.get('layout_config', '{}'))
        except json.JSONDecodeError:
            layout_config = {}

        assigned_map = {(a['row_index'], a['col_index']): a for a in assignments}

        fig, ax = plt.subplots(figsize=(cols * 2, rows * 1.4))
        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect('equal')
        ax.invert_yaxis()
        ax.axis('off')

        for r in range(rows):
            for c in range(cols):
                cell_key = f"{r},{c}"
                cell_type = layout_config.get(cell_key, "student_seat")

                if cell_type == "void":
                    continue

                facecolor = 'white'
                edgecolor = 'black'
                label = ""

                if cell_type == "teacher_desk":
                    facecolor = '#D3D3D3'
                    label = "Mesa Prof."
                elif cell_type == "door":
                    facecolor = '#8B4513'
                    label = "Porta"
                elif cell_type == "student_seat":
                    facecolor = 'white'
                    assignment_data = assigned_map.get((r, c))
                    if assignment_data:
                        student_name = assignment_data['student_name']
                        call_num = assignment_data.get('call_number')
                        call_str = f"{call_num}" if call_num is not None else "?"
                        ax.text(c + 0.06, r + 0.14, call_str, ha='left', va='top', fontsize=8, fontweight='bold', color='blue')
                        label = student_name
                    else:
                        label = "Vazio"

                rect = Rectangle((c + 0.02, r + 0.05), 0.96, 0.9, facecolor=facecolor, edgecolor=edgecolor)
                ax.add_patch(rect)

                if label != "Vazio":
                    display_label = label
                    if len(label) > 15:
                        parts = label.split()
                        if len(parts) > 1:
                            display_label = f"{parts[0]}\n{parts[-1]}"
                        else:
                            display_label = label[:15] + "..."
                    ax.text(c + 0.5, r + 0.52, display_label, ha='center', va='center', fontsize=10, color='white' if cell_type == 'door' else 'black')
                else:
                    ax.text(c + 0.5, r + 0.5, "Vazio", ha='center', va='center', fontsize=8, color='#AAAAAA')

        plt.title(f"Mapa de Sala: {chart_details['name']}", fontsize=16)

        filename = f"seating_chart_{chart_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        filepath = self._get_file_path(filename)
        plt.savefig(filepath, format=format, bbox_inches='tight')
        plt.close(fig)
        return filepath

    def generate_student_grade_chart(self, student_id: int, class_id: int) -> str:
        """
        Generates a bar chart of a student's grades in a specific class, separated by Subject.

        :param student_id: ID of the student.
        :param class_id: ID of the class.
        :return: Path to the generated image file.
        """
        # Otimização 1: Usar o helper get_class_report_data para evitar queries em loop
        report_data = self.data_service.get_class_report_data(class_id)

        # Encontra o aluno na lista de dados retornada (evita query extra)
        student_data = next((s for s in report_data['students'] if s['student_id'] == student_id), None)
        class_info = self.data_service.get_class_by_id(class_id) # Mantendo query leve por ID

        if not student_data or not class_info:
             # Fallback caso o aluno não esteja na lista (ex: foi deletado mas id passado)
             # Mas report_data['students'] pega enrollments.
             raise ValueError("Student or Class not found (or student not enrolled).")

        subjects_data = report_data['subjects']
        grades_map = report_data['grades_map']

        if not subjects_data:
            raise ValueError(f"No subjects found for {class_info['name']}.")

        # Prepare data
        subject_names = []
        averages = []

        for subject in subjects_data:
            assessments = subject['assessments']

            student_grades = {}
            for assessment in assessments:
                score = grades_map.get((student_id, assessment['id']))
                if score is not None:
                    student_grades[assessment['id']] = score

            avg = GradeService.calculate_subject_final_average(student_id, student_grades, assessments)
            subject_names.append(subject['course_name'])
            averages.append(avg)

        # Plotting
        plt.figure(figsize=(12, 6))
        plt.bar(subject_names, averages, color='skyblue')
        plt.xlabel('Disciplinas')
        plt.ylabel('Média')
        plt.title(f"Desempenho de {student_data['name']} - {class_info['name']}")
        plt.ylim(0, 10)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save file
        filename = f"chart_student_{student_id}_class_{class_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self._get_file_path(filename)
        plt.savefig(filepath)
        plt.close()

        return filepath

    def generate_class_grade_distribution(self, class_id: int) -> str:
        """
        Gera um histograma de distribuição global de notas para uma turma.
        """
        class_info = self.data_service.get_class_by_id(class_id)
        if not class_info:
            raise ValueError("Turma não encontrada.")

        report_data = self.data_service.get_class_report_data(class_id)
        students = report_data['students']
        subjects = report_data['subjects']
        grades_map = report_data['grades_map']

        global_averages = []

        for student in students:
            student_id = student['student_id']
            student_subject_averages = []

            for subject in subjects:
                assessments = subject['assessments']
                student_grades = {}
                for assessment in assessments:
                    score = grades_map.get((student_id, assessment['id']))
                    if score is not None:
                        student_grades[assessment['id']] = score

                avg = GradeService.calculate_subject_final_average(student_id, student_grades, assessments)
                student_subject_averages.append(avg)

            if student_subject_averages:
                global_avg = sum(student_subject_averages) / len(student_subject_averages)
                global_averages.append(global_avg)
            else:
                global_averages.append(0.0)

        if not global_averages:
            raise ValueError("Sem dados para gerar a distribuição de notas.")

        plt.figure(figsize=(10, 6))
        plt.hist(global_averages, bins=[0, 2, 4, 6, 8, 10], edgecolor='black', alpha=0.7)
        plt.xlabel('Média Global (Todas as Disciplinas)')
        plt.ylabel('Número de Alunos')
        plt.title(f"Distribuição de Notas Global - {class_info['name']}")
        plt.xticks([1, 3, 5, 7, 9])
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        filename = f"chart_distribution_class_{class_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self._get_file_path(filename)
        plt.savefig(filepath)
        plt.close()

        return filepath

    def export_class_grades_csv(self, class_id: int) -> str:
        """
        Exporta as notas de uma turma para um arquivo CSV, listando disciplinas e médias.
        """
        class_info = self.data_service.get_class_by_id(class_id)
        if not class_info:
            raise ValueError("Turma não encontrada.")

        report_data = self.data_service.get_class_report_data(class_id)
        students = report_data['students']
        subjects = report_data['subjects']
        grades_map = report_data['grades_map']

        header = ["Nº", "Aluno"] + [s['course_name'] for s in subjects] + ["Média Global"]

        rows = []
        for student in students:
            student_id = student['student_id']
            row = [student['call_number'], student['name']]

            subject_averages = []
            for subject in subjects:
                assessments = subject['assessments']
                student_grades = {}
                for assessment in assessments:
                    score = grades_map.get((student_id, assessment['id']))
                    if score is not None:
                        student_grades[assessment['id']] = score

                avg = GradeService.calculate_subject_final_average(student_id, student_grades, assessments)
                row.append(f"{avg:.2f}")
                subject_averages.append(avg)

            if subject_averages:
                global_avg = sum(subject_averages) / len(subject_averages)
                row.append(f"{global_avg:.2f}")
            else:
                row.append("0.00")

            rows.append(row)

        filename = f"grades_class_{class_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = self._get_file_path(filename)

        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)

        return filepath

    def generate_student_report_card(self, student_id: int, class_id: int) -> str:
        """
        Gera um boletim em formato texto para um aluno, agrupando notas por disciplina.
        """
        class_info = self.data_service.get_class_by_id(class_id)
        if not class_info:
            raise ValueError("Turma não encontrada.")

        report_data = self.data_service.get_class_report_data(class_id)
        student_data = next((s for s in report_data['students'] if s['student_id'] == student_id), None)

        if not student_data:
            student_obj = self.data_service.get_student_by_id(student_id)
            if not student_obj:
                raise ValueError("Aluno não encontrado.")
            student_name = f"{student_obj['first_name']} {student_obj['last_name']}"
        else:
            student_name = student_data['name']

        subjects_data = report_data['subjects']
        grades_map = report_data['grades_map']
        student_incidents = self.data_service.get_student_incidents(student_id, class_id)

        lines = [
            "=" * 50,
            "BOLETIM ESCOLAR",
            "=" * 50,
            f"Aluno: {student_name}",
            f"Turma: {class_info['name']}",
            f"Data de Emissão: {datetime.now().strftime('%d/%m/%Y')}",
            "-" * 50,
            "DESEMPENHO POR DISCIPLINA:",
            ""
        ]

        if not subjects_data:
            lines.append("Nenhuma disciplina cadastrada nesta turma.")

        for subject in subjects_data:
            lines.append(f"DISCIPLINA: {subject['course_name'].upper()}")

            assessments = subject['assessments']
            student_grades = {}
            for assessment in assessments:
                score = grades_map.get((student_id, assessment['id']))
                if score is not None:
                    student_grades[assessment['id']] = score

            if not assessments:
                lines.append("  - Nenhuma avaliação registrada.")
            else:
                for assessment in assessments:
                    score = grades_map.get((student_id, assessment['id']))
                    score_str = f"{score:.2f}" if score is not None else "N/A"
                    lines.append(f"  - {assessment['name']} (Peso {assessment['weight']}): {score_str}")

            avg = GradeService.calculate_subject_final_average(student_id, student_grades, assessments)
            lines.append(f"  >> MÉDIA FINAL: {avg:.2f}")

            # Adiciona Frequência
            freq_stats = self.data_service.get_student_attendance_stats(student_id, subject['id'])
            if freq_stats['total_lessons'] > 0:
                lines.append(f"  >> FREQUÊNCIA: {freq_stats['percentage']:.1f}% ({freq_stats['present_count']} P / {freq_stats['total_lessons']} Aulas)")
            else:
                lines.append("  >> FREQUÊNCIA: N/A")

            lines.append("-" * 30)

        lines.extend([
            "",
            "=" * 50,
            f"OCORRÊNCIAS DISCIPLINARES: {len(student_incidents)}"
        ])
        for inc in student_incidents:
             lines.append(f"- {inc['date']}: {inc['description']}")

        lines.append("="*50)

        # Save file
        filename = f"boletim_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self._get_file_path(filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        return filepath