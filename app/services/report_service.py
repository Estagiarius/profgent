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
        Generates a bar chart of a student's grades in a specific class, separated by Subject.

        :param student_id: ID of the student.
        :param class_id: ID of the class.
        :return: Path to the generated image file.
        """
        student = next((g for g in self.data_service.get_all_students() if g['id'] == student_id), None)
        class_info = self.data_service.get_class_by_id(class_id)

        if not student or not class_info:
            raise ValueError("Student or Class not found.")

        # Fetch subjects for the class
        subjects = self.data_service.get_subjects_for_class(class_id)
        if not subjects:
            raise ValueError(f"No subjects found for {class_info['name']}.")

        # Prepare data
        subject_names = []
        averages = []

        for subject in subjects:
            # For each subject, calculate the weighted average
            assessments = self.data_service.get_assessments_for_subject(subject['id'])
            grades = self.data_service.get_grades_for_subject(subject['id'])
            student_grades = [g for g in grades if g['student_id'] == student_id]

            avg = self.data_service.calculate_weighted_average(student_id, student_grades, assessments)
            subject_names.append(subject['course_name'])
            averages.append(avg)

        # Plotting
        plt.figure(figsize=(12, 6))
        plt.bar(subject_names, averages, color='skyblue')
        plt.xlabel('Disciplinas')
        plt.ylabel('Média')
        plt.title(f"Desempenho de {student['first_name']} {student['last_name']} - {class_info['name']}")
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
        Generates a histogram of global grade distribution for a class (averaging all subjects).

        :param class_id: ID of the class.
        :return: Path to the generated image file.
        """
        class_info = self.data_service.get_class_by_id(class_id)
        if not class_info:
            raise ValueError("Class not found.")

        enrollments = self.data_service.get_enrollments_for_class(class_id)
        subjects = self.data_service.get_subjects_for_class(class_id)

        global_averages = []

        for enrollment in enrollments:
            student_id = enrollment['student_id']
            student_subject_averages = []

            for subject in subjects:
                assessments = self.data_service.get_assessments_for_subject(subject['id'])
                grades = self.data_service.get_grades_for_subject(subject['id'])
                student_grades = [g for g in grades if g['student_id'] == student_id]

                avg = self.data_service.calculate_weighted_average(student_id, student_grades, assessments)
                student_subject_averages.append(avg)

            if student_subject_averages:
                global_avg = sum(student_subject_averages) / len(student_subject_averages)
                global_averages.append(global_avg)
            else:
                global_averages.append(0.0)

        if not global_averages:
             raise ValueError("No data to generate distribution.")

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.hist(global_averages, bins=[0, 2, 4, 6, 8, 10], edgecolor='black', alpha=0.7)
        plt.xlabel('Média Global (Todas as Disciplinas)')
        plt.ylabel('Número de Alunos')
        plt.title(f"Distribuição de Notas Global - {class_info['name']}")
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
        Exports grades for a class to a CSV file, listing all subjects and averages.

        :param class_id: ID of the class.
        :return: Path to the generated CSV file.
        """
        class_info = self.data_service.get_class_by_id(class_id)
        if not class_info:
            raise ValueError("Class not found.")

        enrollments = self.data_service.get_enrollments_for_class(class_id)
        subjects = self.data_service.get_subjects_for_class(class_id)

        # Prepare CSV Data
        # Header: Nº, Aluno, Subject 1 Avg, Subject 2 Avg, ..., Global Average
        header = ["Nº", "Aluno"] + [s['course_name'] for s in subjects] + ["Média Global"]

        rows = []
        for enrollment in enrollments:
            student_id = enrollment['student_id']
            student_name = f"{enrollment['student_first_name']} {enrollment['student_last_name']}"

            row = [enrollment['call_number'], student_name]

            subject_averages = []
            for subject in subjects:
                assessments = self.data_service.get_assessments_for_subject(subject['id'])
                grades = self.data_service.get_grades_for_subject(subject['id'])
                student_grades = [g for g in grades if g['student_id'] == student_id]

                avg = self.data_service.calculate_weighted_average(student_id, student_grades, assessments)
                row.append(f"{avg:.2f}")
                subject_averages.append(avg)

            if subject_averages:
                global_avg = sum(subject_averages) / len(subject_averages)
                row.append(f"{global_avg:.2f}")
            else:
                row.append("0.00")

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
        Generates a text-based report card for a student, grouping grades by subject.

        :param student_id: ID of the student.
        :param class_id: ID of the class.
        :return: Path to the generated text file.
        """
        class_info = self.data_service.get_class_by_id(class_id)
        student_obj = next((s for s in self.data_service.get_all_students() if s['id'] == student_id), None)

        if not class_info or not student_obj:
            raise ValueError("Class or Student not found.")

        subjects = self.data_service.get_subjects_for_class(class_id)
        incidents = self.data_service.get_incidents_for_class(class_id)
        student_incidents = [i for i in incidents if i['student_id'] == student_id]

        # Build Report Content
        lines = []
        lines.append("="*50)
        lines.append(f"BOLETIM ESCOLAR")
        lines.append("="*50)
        lines.append(f"Aluno: {student_obj['first_name']} {student_obj['last_name']}")
        lines.append(f"Turma: {class_info['name']}")
        lines.append(f"Data de Emissão: {datetime.now().strftime('%d/%m/%Y')}")
        lines.append("-" * 50)
        lines.append("DESEMPENHO POR DISCIPLINA:")
        lines.append("")

        if not subjects:
            lines.append("Nenhuma disciplina cadastrada nesta turma.")

        for subject in subjects:
            lines.append(f"DISCIPLINA: {subject['course_name'].upper()}")

            assessments = self.data_service.get_assessments_for_subject(subject['id'])
            grades = self.data_service.get_grades_for_subject(subject['id'])
            student_grades = [g for g in grades if g['student_id'] == student_id]

            if not assessments:
                lines.append("  - Nenhuma avaliação registrada.")
            else:
                for assessment in assessments:
                    grade_item = next((g for g in student_grades if g['assessment_id'] == assessment['id']), None)
                    score_str = f"{grade_item['score']:.2f}" if grade_item else "N/A"
                    lines.append(f"  - {assessment['name']} (Peso {assessment['weight']}): {score_str}")

            avg = self.data_service.calculate_weighted_average(student_id, student_grades, assessments)
            lines.append(f"  >> MÉDIA FINAL: {avg:.2f}")
            lines.append("-" * 30)

        lines.append("")
        lines.append("=" * 50)
        lines.append(f"OCORRÊNCIAS DISCIPLINARES: {len(student_incidents)}")
        for inc in student_incidents:
             lines.append(f"- {inc['date']}: {inc['description']}")

        lines.append("="*50)

        # Save file
        filename = f"boletim_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self._get_file_path(filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        return filepath
