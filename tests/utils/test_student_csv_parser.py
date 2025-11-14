# -*- coding: utf-8 -*-

"""
Testes para o parser de CSV de alunos e a funcionalidade de importação.
"""

import pytest
from app.services.data_service import DataService
from app.models.student import Student
from app.models.class_enrollment import ClassEnrollment

# Conteúdo de um arquivo CSV de exemplo para ser usado nos testes
MOCK_CSV_CONTENT = """
Alunos;11/11/2025 13:31

Filtros

Ano Letivo;2025

Nº de chamada;Nome do Aluno;Data de Nascimento;Situação do Aluno
1;ANA JULIA GONÇALVES;09/06/2008;Transferido
2;ANDRÉ HENRIQUE COSTA E SILVA;01/10/2009;Ativo
3;PEDRO HENRIQUE SILVA DA ROCHA;09/09/2009;Ativo
4;MARIA EDUARDA MORAES DA SILVA;03/07/2009;BAIXA - TRANSFERÊNCIA
5;JOSÉ CARLOS SANTANA;15/05/2010;Ativo

"""

@pytest.fixture
def data_service(db_session):
    """
    Fornece uma instância do DataService com a sessão de banco de dados do teste injetada.
    """
    return DataService(db_session=db_session)

def test_import_students_from_csv_success(data_service, db_session):
    """
    Testa o fluxo completo de importação de CSV, verificando se os alunos
    são criados e matriculados corretamente.
    """
    # Cria uma turma de teste para a qual os alunos serão matriculados
    course = data_service.add_course("Ciência da Computação - Teste CSV", "CSV-TEST-101")
    class_ = data_service.create_class("Turma Teste CSV", course.id)
    db_session.flush()

    # Executa a função de importação
    result = data_service.import_students_from_csv(class_.id, MOCK_CSV_CONTENT)

    # Verifica o resultado da importação
    assert result["imported_count"] == 5
    assert not result["errors"]

    # Verifica no banco de dados se os alunos foram criados
    all_students = db_session.query(Student).order_by(Student.first_name).all()
    assert len(all_students) == 5

    # Verifica os detalhes de alguns alunos para garantir o parsing correto

    # Teste de nome composto
    ana = db_session.query(Student).filter(Student.last_name == "GONÇALVES").first()
    assert ana is not None
    assert ana.first_name == "ANA JULIA"

    # Teste de nome composto com 'de'
    andre = db_session.query(Student).filter(Student.first_name == "ANDRÉ").first()
    assert andre is not None
    assert andre.last_name == "HENRIQUE COSTA E SILVA"

    # Teste de outro nome composto
    pedro = db_session.query(Student).filter(Student.first_name == "PEDRO HENRIQUE").first()
    assert pedro is not None
    assert pedro.last_name == "SILVA DA ROCHA"

    # Teste de status
    enrollments = db_session.query(ClassEnrollment).all()
    assert len(enrollments) == 5

    # Conta quantos estão ativos e inativos
    active_count = sum(1 for e in enrollments if e.status == "Active")
    inactive_count = sum(1 for e in enrollments if e.status == "Inactive")
    assert active_count == 3
    assert inactive_count == 2

    # Verifica se os call numbers foram atribuídos sequencialmente
    call_numbers = sorted([e.call_number for e in enrollments])
    assert call_numbers == [1, 2, 3, 4, 5]

def test_import_students_from_csv_invalid_header(data_service):
    """
    Testa se a importação falha corretamente quando o cabeçalho do CSV é inválido.
    """
    invalid_csv = "Coluna1;Coluna2\\nValor1;Valor2"
    result = data_service.import_students_from_csv(1, invalid_csv)

    assert result["imported_count"] == 0
    assert len(result["errors"]) == 1
    assert "Cabeçalho do CSV não encontrado" in result["errors"][0]

def test_import_handles_duplicate_students(data_service, db_session):
    """
    Testa se o parser lida com alunos duplicados, importando apenas a última
    ocorrência com o status mais recente.
    """
    duplicate_csv = """
Nº de chamada;Nome do Aluno;Data de Nascimento;Situação do Aluno
18;JÚLIA NOGUEIRA RAMOS;28/09/2009;Transferido
19;KAIQUE ALMEIDA CLEMENTE;29/01/2010;Ativo
63;JÚLIA NOGUEIRA RAMOS;28/09/2009;Ativo
"""
    course = data_service.add_course("Português", "PT101")
    class_ = data_service.create_class("Turma Duplicatas", course.id)
    db_session.flush()

    result = data_service.import_students_from_csv(class_.id, duplicate_csv)

    assert result["imported_count"] == 2
    assert not result["errors"]

    # Deve haver apenas 2 alunos e 2 matrículas no total
    students = db_session.query(Student).all()
    enrollments = db_session.query(ClassEnrollment).all()
    assert len(students) == 2
    assert len(enrollments) == 2

    # A aluna duplicada 'JÚLIA NOGUEIRA RAMOS' deve ter sido importada com o
    # status da sua ÚLTIMA aparição ('Ativo')
    julia_enrollment = db_session.query(ClassEnrollment).join(Student).filter(
        Student.first_name == "JÚLIA"
    ).first()

    assert julia_enrollment is not None
    assert julia_enrollment.status == "Active"
