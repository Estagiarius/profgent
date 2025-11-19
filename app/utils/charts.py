# Importa a biblioteca 'matplotlib.pyplot' para criar gráficos.
import matplotlib.pyplot as plt
# Importa o módulo 'os' para interagir com o sistema de arquivos (manipular caminhos).
import os
# Importa o módulo 'tempfile' para criar arquivos temporários de forma segura.
import tempfile
# Importa o modelo Grade, mas seu uso direto foi substituído por dicionários.
# A importação pode ser mantida para clareza ou removida se não for usada.
from app.models.grade import Grade

# Define a função que cria o gráfico de distribuição de notas.
def create_grade_distribution_chart(grades: list[dict], course_name: str) -> str:
    """
    Gera um histograma da distribuição de notas e o salva como um arquivo PNG temporário.
    Retorna o caminho para o arquivo de gráfico salvo.

    Args:
        grades: Uma lista de dicionários, onde cada dicionário representa uma nota e deve conter a chave 'score'.
        course_name: O nome do curso, para ser usado no título do gráfico.

    Returns:
        O caminho do arquivo onde a imagem do gráfico foi salva.
    """
    # Obtém o diretório temporário do sistema operacional.
    temp_dir = tempfile.gettempdir()
    # Cria um caminho completo para o nosso arquivo de gráfico temporário.
    output_path = os.path.join(temp_dir, "academic_app_chart.png")

    # Cria uma nova figura e um conjunto de eixos (o "quadro" do nosso gráfico).
    fig, ax = plt.subplots()

    # Se a lista de notas estiver vazia.
    if not grades:
        # Exibe uma mensagem de texto no centro do gráfico.
        ax.text(0.5, 0.5, 'Nenhuma nota disponível para este curso.', horizontalalignment='center', verticalalignment='center')
    # Se houver notas.
    else:
        # Extrai apenas as notas (scores) da lista de dicionários.
        # `min(g['score'], 10)` garante que qualquer nota acima de 10 (ex: por crédito extra)
        # seja visualmente limitada a 10 no gráfico.
        scores = [min(g['score'], 10) for g in grades]
        # Cria o histograma.
        # `bins=10` divide o intervalo em 10 barras (0-1, 1-2, ..., 9-10).
        # `range=(0, 10)` define o intervalo do eixo X.
        # `edgecolor='black'` adiciona uma borda preta às barras para melhor visualização.
        ax.hist(scores, bins=10, range=(0, 10), edgecolor='black')
        # Define os rótulos dos eixos X e Y.
        ax.set_xlabel('Nota')
        ax.set_ylabel('Número de Alunos')
        # Define as marcações no eixo X para que mostrem todos os números de 0 a 10.
        ax.set_xticks(range(0, 11, 1))

    # Define o título do gráfico.
    ax.set_title(f'Distribuição de Notas para {course_name}')

    # Salva a figura gerada no caminho do arquivo temporário.
    plt.savefig(output_path)
    # Fecha a figura para liberar memória.
    plt.close(fig)

    # Retorna o caminho onde o gráfico foi salvo.
    return output_path
