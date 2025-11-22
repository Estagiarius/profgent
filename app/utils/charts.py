import matplotlib.pyplot as plt
import os
import tempfile
from typing import List, Dict, Any

def create_grade_distribution_chart(grades: List[Dict[str, Any]], course_name: str) -> str:
    """
    Gera e salva um gráfico da distribuição de notas de um curso específico. O gráfico é
    salvo em um arquivo temporário e retorna o caminho para o arquivo salvo. Caso não haja
    notas disponíveis, uma mensagem de aviso será exibida no gráfico.

    :param grades: Lista de dicionários, onde cada dicionário representa informações
        de notas de alunos. O campo 'score' deve conter a nota atribuída.
    :param course_name: Nome do curso cujas notas serão analisadas.
    :return: Caminho do arquivo temporário onde o gráfico gerado foi salvo, com extensão
        '.png'.
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
