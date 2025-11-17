# Este arquivo __init__.py serve para duas coisas principais:
# 1. Ele transforma o diretório 'models' em um pacote Python.
# 2. Ele centraliza a importação dos modelos, permitindo que outros arquivos
#    importem qualquer modelo diretamente do pacote 'app.models' em vez de
#    especificar o arquivo de cada modelo.

# Importa a classe Student do arquivo student.py para que ela fique acessível no pacote.
from .student import Student
# Importa a classe Course do arquivo course.py.
from .course import Course
# Importa a classe Class do arquivo class_.py (o '_' é usado para evitar conflito com a palavra-chave 'class').
from .class_ import Class
# Importa a classe Assessment do arquivo assessment.py.
from .assessment import Assessment
# Importa a classe Grade do arquivo grade.py.
from .grade import Grade
# Importa a classe ClassEnrollment do arquivo class_enrollment.py.
from .class_enrollment import ClassEnrollment
# Importa a classe Lesson do arquivo lesson.py.
from .lesson import Lesson
# Importa a classe Incident do arquivo incident.py.
from .incident import Incident
