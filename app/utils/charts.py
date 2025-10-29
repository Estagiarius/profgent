import matplotlib.pyplot as plt
import os
from app.models.grade import Grade

def create_grade_distribution_chart(grades: list[Grade], course_name: str, output_path: str):
    """
    Generates a histogram of grade distribution for a given course and saves it as a PNG file.
    """
    if not grades:
        # Create a blank chart if there are no grades
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'No grades available for this course.', horizontalalignment='center', verticalalignment='center')
        ax.set_title(f'Grade Distribution for {course_name}')
        plt.savefig(output_path)
        plt.close(fig)
        return

    scores = [grade.score for grade in grades]

    fig, ax = plt.subplots()
    ax.hist(scores, bins=10, range=(0, 100), edgecolor='black')

    ax.set_title(f'Grade Distribution for {course_name}')
    ax.set_xlabel('Score')
    ax.set_ylabel('Number of Students')
    ax.set_xticks(range(0, 101, 10))

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.savefig(output_path)
    plt.close(fig) # Close the figure to free up memory
