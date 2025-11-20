import matplotlib.pyplot as plt
import os
import tempfile
from typing import List, Dict, Any

def create_grade_distribution_chart(grades: List[Dict[str, Any]], course_name: str) -> str:
    """
    Generates a histogram of grade distribution and saves it as a temporary PNG file.
    Returns the path to the saved chart file.
    """
    # Create a temporary file path
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, "academic_app_chart.png")

    fig, ax = plt.subplots()

    if not grades:
        ax.text(0.5, 0.5, 'Nenhuma nota disponível para este curso.', horizontalalignment='center', verticalalignment='center')
    else:
        # Clamp scores to a maximum of 10, accessing the score from the dictionary
        scores = [min(grade['score'], 10) for grade in grades]
        ax.hist(scores, bins=10, range=(0, 10), edgecolor='black')
        ax.set_xlabel('Nota')
        ax.set_ylabel('Número de Alunos')
        # Set ticks from 0 to 10
        ax.set_xticks(range(0, 11, 1))

    ax.set_title(f'Distribuição de Notas para {course_name}')

    plt.savefig(output_path)
    plt.close(fig)

    return output_path
