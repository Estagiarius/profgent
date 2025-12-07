import matplotlib
# Configura o backend 'Agg' antes de importar pyplot para evitar problemas com threads e GUI
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import tempfile
from typing import List, Dict, Any, Union

def create_grade_distribution_chart(data: Union[List[Dict[str, Any]], List[float]], course_name: str) -> str:
    """
    Gera e salva um gráfico da distribuição de notas (ou médias) de um curso específico.
    O gráfico é salvo em um arquivo temporário e retorna o caminho para o arquivo salvo.
    Caso não haja dados disponíveis, uma mensagem de aviso será exibida no gráfico.

    :param data: Lista de notas. Pode ser uma lista de dicionários (legado) contendo 'score',
                 ou uma lista direta de valores float (médias finais).
    :param course_name: Nome do curso cujas notas serão analisadas.
    :return: Caminho do arquivo temporário onde o gráfico gerado foi salvo.
    """
    # Create a temporary file path
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, "academic_app_chart.png")

    fig, ax = plt.subplots()

    if not data:
        ax.text(0.5, 0.5, 'Nenhum dado disponível para este curso.', horizontalalignment='center', verticalalignment='center')
    else:
        # Extrai os scores. Se for lista de dicts, extrai 'score'. Se for lista de floats, usa direto.
        scores = []
        if isinstance(data[0], dict):
             scores = [min(d['score'], 10) for d in data]
        else:
             scores = [min(v, 10) for v in data]

        ax.hist(scores, bins=10, range=(0, 10), edgecolor='black')
        ax.set_xlabel('Média Final')
        ax.set_ylabel('Número de Alunos')
        # Set ticks from 0 to 10
        ax.set_xticks(range(0, 11, 1))

    ax.set_title(f'Distribuição de Médias para {course_name}')

    plt.savefig(output_path)
    plt.close(fig)

    return output_path
