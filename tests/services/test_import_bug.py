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
# Importa as classes de serviço e de sessão do banco para serem usadas nas fixtures.
from app.services.data_service import DataService
from sqlalchemy.orm import Session

# Define a função de teste que simula o bug de importação.
def test_import_bug_with_user_csv(data_service: DataService, db_session: Session):
    """
    Caso de teste que usa o CSV fornecido pelo usuário para confirmar a correção final.
    Ele simula o fluxo de trabalho do orquestrador, lendo o conteúdo do arquivo
    e passando-o para o DataService.
    """
    # --- PREPARAÇÃO ---
    # Cria uma turma para o teste, isolando-o de outros dados.
    # course = data_service.add_course("Bug Repro Course", "BRC101") # Não precisa mais de curso para criar turma
    class_ = data_service.create_class("Bug Repro Class")
    db_session.flush()

    # --- DADOS DE TESTE ---
    # O conteúdo exato do arquivo CSV que causava o bug.
    # Este CSV tem várias características importantes para o teste:
    # - Linhas de metadados no início que devem ser ignoradas.
    # - Um cabeçalho que define as colunas.
    # - Alunos com status variados ("ATIVO", "BAIXA - TRANSFERÊNCIA", "Transferido").
    # - Alunos duplicados (ex: "ALUNO FICTÍCIO 18", "ALUNO FICTÍCIO 51"),
    #   onde apenas a última ocorrência (a mais recente no arquivo) deve ser considerada.
    csv_lines = [
        "Alunos;11/11/2025 13:31",
        "",
        "Filtros",
        "",
        "Ano Letivo;2025",
        "",
        "Nº de chamada;Nome do Aluno;Data de Nascimento;Situação do Aluno",
    ]
    statuses = ["Ativo", "Transferido", "BAIXA - TRANSFERÊNCIA"]
    for i in range(1, 66):
        status = statuses[i % len(statuses)]
        if i in (18, 51):
            status = "Transferido"
        month = ((i - 1) % 12) + 1
        day = ((i - 1) % 28) + 1
        year = 2009 if i % 2 == 0 else 2010
        csv_lines.append(f"{i};ALUNO FICTÍCIO EXEMPLO {i:02d};{day:02d}/{month:02d}/{year};{status}")
    # Duplicatas com status atualizado para Ativo (total de 67 linhas, 65 alunos únicos)
    csv_lines.append("66;ALUNO FICTÍCIO EXEMPLO 18;18/06/2009;Ativo")
    csv_lines.append("67;ALUNO FICTÍCIO EXEMPLO 51;23/03/2010;Ativo")
    csv_content = "\n".join(csv_lines) + "\n"

    # --- AÇÃO ---
    # Chama o método de importação, passando o ID da turma e o conteúdo do CSV.
    result = data_service.import_students_from_csv(class_['id'], csv_content)
    # Salva as alterações no banco de dados de teste.
    db_session.commit()

    # --- VERIFICAÇÃO ---
    # Garante que a importação não retornou nenhum erro.
    assert not result["errors"], f"A importação falhou com erros: {result['errors']}"

    # O CSV contém 67 linhas de dados, mas alguns alunos estão duplicados.
    # O número esperado de alunos únicos é 65.
    expected_unique_students = 65

    # Verifica se o número de matrículas criadas na turma é o esperado.
    enrollments = data_service.get_enrollments_for_class(class_['id'])
    assert len(enrollments) == expected_unique_students, f"Esperado {expected_unique_students} matrículas, mas foram encontradas {len(enrollments)}"

    # Verifica se o número total de alunos no banco de dados corresponde ao número esperado.
    student_count = data_service.get_student_count()
    assert student_count == expected_unique_students, f"Esperado {expected_unique_students} alunos no BD, mas foram encontrados {student_count}"
