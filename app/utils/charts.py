import matplotlib.pyplot as plt
import os
import tempfile
from app.models.grade import Grade

def create_grade_distribution_chart(grades: list[Grade], course_name: str) -> str:
    """
    Generates a histogram of grade distribution and saves it as a temporary PNG file.
    Returns the path to the saved chart file.
    """
    # Create a temporary file path
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, "academic_app_chart.png")

    fig, ax = plt.subplots()

    if not grades:
        ax.text(0.5, 0.5, 'No grades available for this course.', horizontalalignment='center', verticalalignment='center')
    else:
        scores = [grade.score for grade in grades]
        ax.hist(scores, bins=10, range=(0, 100), edgecolor='black')
        ax.set_xlabel('Score')
        ax.set_ylabel('Number of Students')
        ax.set_xticks(range(0, 101, 10))

    ax.set_title(f'Grade Distribution for {course_name}')

    plt.savefig(output_path)
    plt.close(fig)

    return output_path
