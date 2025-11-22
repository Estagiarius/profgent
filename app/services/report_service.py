import csv
import os
import json
from datetime import datetime
import matplotlib
# Force Agg backend for headless/background generation to avoid GUI lockups
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from app.services.data_service import DataService

class ReportService:
    """
    Service responsible for generating reports and visualizations.
    This service centralizes logic used by both the AI Assistant and the UI.
    """

    REPORTS_DIR = "reports"

    def __init__(self):
        self.data_service = DataService()
        self._ensure_reports_dir()

    def _ensure_reports_dir(self):
        """Ensures the reports directory exists."""
        if not os.path.exists(self.REPORTS_DIR):
            os.makedirs(self.REPORTS_DIR)

    def _get_file_path(self, filename: str) -> str:
        """Returns the full path for a report file."""
        return os.path.join(self.REPORTS_DIR, filename)

    def generate_student_grade_chart(self, student_id: int, class_id: int) -> str:
        """
        Generates a bar chart of a student's grades in a specific class.

        :param student_id: ID of the student.
        :param class_id: ID of the class.
        :return: Path to the generated image file.
        """
        # Fetch data
        grades = self.data_service.get_grades_for_class(class_id)
        student_grades = [g for g in grades if g['student_id'] == student_id]

        student = next((g for g in self.data_service.get_all_students() if g['id'] == student_id), None)
        class_info = self.data_service.get_class_by_id(class_id)

        if not student or not class_info:
            raise ValueError("Student or Class not found.")

        if not student_grades:
            raise ValueError(f"No grades found for {student['first_name']} in {class_info['name']}.")

        # Prepare data for plotting
        assessment_names = [g['assessment_name'] for g in student_grades]
        scores = [g['score'] for g in student_grades]

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.bar(assessment_names, scores, color='skyblue')
        plt.xlabel('Avaliações')
        plt.ylabel('Nota')
        plt.title(f"Desempenho de {student['first_name']} {student['last_name']} - {class_info['name']}")
        plt.ylim(0, 10)  # Assuming grades are 0-10
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Save file
        filename = f"chart_student_{student_id}_class_{class_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self._get_file_path(filename)
        plt.savefig(filepath)
        plt.close()

        return filepath

    def generate_class_grade_distribution(self, class_id: int) -> str:
        """
        Generates a histogram of grade distribution for a class (using averages).

        :param class_id: ID of the class.
        :return: Path to the generated image file.
        """
        class_info = self.data_service.get_class_by_id(class_id)
        if not class_info:
            raise ValueError("Class not found.")

        enrollments = self.data_service.get_enrollments_for_class(class_id)
        assessments = class_info.get('assessments', [])
        grades = self.data_service.get_grades_for_class(class_id)

        averages = []
        for enrollment in enrollments:
            student_id = enrollment['student_id']
            student_grades = [g for g in grades if g['student_id'] == student_id]
            avg = self.data_service.calculate_weighted_average(student_id, student_grades, assessments)
            averages.append(avg)

        if not averages:
             raise ValueError("No data to generate distribution.")

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.hist(averages, bins=[0, 2, 4, 6, 8, 10], edgecolor='black', alpha=0.7)
        plt.xlabel('Média')
        plt.ylabel('Número de Alunos')
        plt.title(f"Distribuição de Notas - {class_info['name']}")
        plt.xticks([1, 3, 5, 7, 9])
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Save file
        filename = f"chart_distribution_class_{class_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self._get_file_path(filename)
        plt.savefig(filepath)
        plt.close()

        return filepath

    def export_class_grades_csv(self, class_id: int) -> str:
        """
        Exports all grades for a class to a CSV file.

        :param class_id: ID of the class.
        :return: Path to the generated CSV file.
        """
        class_info = self.data_service.get_class_by_id(class_id)
        if not class_info:
            raise ValueError("Class not found.")

        enrollments = self.data_service.get_enrollments_for_class(class_id)
        assessments = class_info.get('assessments', [])
        grades = self.data_service.get_grades_for_class(class_id)

        # Prepare CSV Data
        # Header: Call Number, Student Name, Assessment 1, Assessment 2..., Final Average
        header = ["Nº", "Aluno"] + [a['name'] for a in assessments] + ["Média Final"]

        rows = []
        for enrollment in enrollments:
            student_id = enrollment['student_id']
            student_name = f"{enrollment['student_first_name']} {enrollment['student_last_name']}"

            row = [enrollment['call_number'], student_name]

            student_grades_map = {g['assessment_id']: g['score'] for g in grades if g['student_id'] == student_id}

            for assessment in assessments:
                score = student_grades_map.get(assessment['id'], "")
                row.append(score)

            # Calculate average
            student_grades_list = [g for g in grades if g['student_id'] == student_id]
            avg = self.data_service.calculate_weighted_average(student_id, student_grades_list, assessments)
            row.append(f"{avg:.2f}")

            rows.append(row)

        # Save file
        filename = f"grades_class_{class_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = self._get_file_path(filename)

        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)

        return filepath

    def generate_student_report_card(self, student_id: int, class_id: int) -> str:
        """
        Generates a simple text-based report card for a student.

        :param student_id: ID of the student.
        :param class_id: ID of the class.
        :return: Path to the generated text file.
        """
        class_info = self.data_service.get_class_by_id(class_id)
        student_obj = next((s for s in self.data_service.get_all_students() if s['id'] == student_id), None)

        if not class_info or not student_obj:
            raise ValueError("Class or Student not found.")

        grades = self.data_service.get_grades_for_class(class_id)
        student_grades = [g for g in grades if g['student_id'] == student_id]
        assessments = class_info.get('assessments', [])

        # Calculate average
        avg = self.data_service.calculate_weighted_average(student_id, student_grades, assessments)

        incidents = self.data_service.get_incidents_for_class(class_id)
        student_incidents = [i for i in incidents if i['student_id'] == student_id]

        # Build Report Content
        lines = []
        lines.append("="*40)
        lines.append(f"BOLETIM ESCOLAR")
        lines.append("="*40)
        lines.append(f"Aluno: {student_obj['first_name']} {student_obj['last_name']}")
        lines.append(f"Turma: {class_info['name']}")
        lines.append(f"Data de Emissão: {datetime.now().strftime('%d/%m/%Y')}")
        lines.append("-" * 40)
        lines.append("NOTAS PARCIAIS:")

        for assessment in assessments:
             # Find grade
             grade_item = next((g for g in student_grades if g['assessment_id'] == assessment['id']), None)
             score_str = str(grade_item['score']) if grade_item else "N/A"
             lines.append(f"- {assessment['name']} (Peso {assessment['weight']}): {score_str}")

        lines.append("-" * 40)
        lines.append(f"MÉDIA FINAL: {avg:.2f}")
        lines.append("-" * 40)
        lines.append(f"OCORRÊNCIAS DISCIPLINARES: {len(student_incidents)}")
        for inc in student_incidents:
             lines.append(f"- {inc['date']}: {inc['description']}")

        lines.append("="*40)

        # Save file
        filename = f"boletim_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self._get_file_path(filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        return filepath
