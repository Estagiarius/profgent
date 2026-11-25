# Author: Victor Hugo Garcia de Oliveira
# Date: 2026-11-25
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
from datetime import date
from typing import Optional
import os
import pytest
from sqlalchemy import create_engine, inspect

from app.core.tools.tool_decorator import tool
from app.core.tools.tool_registry import ToolRegistry
from app.core.tools.tool_executor import ToolExecutor
from app.data.migrations import migrate_database
from app.models.base import Base
import app.models  # noqa: F401
from app.utils.name_parser import split_full_name
from app.utils.student_csv_parser import parse_student_csv
from app.core.security import credentials
from app.tools import database_tools


def test_tool_decorator_compound_types_and_param_docs():
    """Valida suporte a Optional, Union (|), list e extração de :param na docstring."""
    @tool
    def sample_tool(name: str, age: Optional[int] = None, tags: list[str] | None = None) -> str:
        """
        Ferramenta de teste.

        :param name: Nome do usuário.
        :param age: Idade opcional.
        :param tags: Lista de rótulos.
        """
        return f"{name}-{age}-{tags}"

    props = sample_tool.schema["function"]["parameters"]["properties"]
    assert props["name"]["type"] == "string"
    assert props["name"]["description"] == "Nome do usuário."
    assert props["age"]["type"] == "integer"
    assert props["age"]["description"] == "Idade opcional."
    assert props["tags"]["type"] == "array"
    assert sample_tool.schema["function"]["parameters"]["required"] == ["name"]


def test_tool_registry_deduplicates_schemas_on_reregister():
    @tool
    def ping() -> str:
        """Retorna pong."""
        return "pong"

    registry = ToolRegistry()
    registry.register(ping)
    registry.register(ping)
    assert len(registry.get_all_schemas()) == 1


def test_tool_executor_accepts_dict_args_and_preserves_error_tool_name():
    @tool
    def echo(msg: str) -> str:
        """Retorna a mensagem."""
        return msg

    registry = ToolRegistry()
    registry.register(echo)
    executor = ToolExecutor(registry)

    ok = executor.execute_tool_call({"id": "1", "function": {"name": "echo", "arguments": {"msg": "oi"}}})
    assert ok["content"] == "oi"
    assert ok["name"] == "echo"

    err = executor.execute_tool_call({"id": "2", "function": {"name": "missing_tool", "arguments": "{}"}})
    assert err["name"] == "missing_tool"
    assert "Erro:" in err["content"]


def test_name_parser_accented_compound_names():
    assert split_full_name("João Pedro Silva") == ("João Pedro", "Silva")
    assert split_full_name("José Carlos Santana") == ("José Carlos", "Santana")
    assert split_full_name("  Maria Júlia   Costa ") == ("Maria Júlia", "Costa")


def test_student_csv_parser_missing_status_and_status_detail():
    csv_text = (
        "Nome do Aluno;Data de Nascimento;Situação do Aluno\n"
        "Ana Clara Souza;10/05/2010;BAIXA - TRANSFERÊNCIA\n"
        "Bruno Lima;12/06/2010\n"
    )
    parsed = parse_student_csv(csv_text)
    assert len(parsed) == 2
    ana = next(p for p in parsed if p["first_name"] == "Ana Clara")
    assert ana["status"] == "Inactive"
    assert ana["status_detail"] == "BAIXA - TRANSFERÊNCIA"
    bruno = next(p for p in parsed if p["first_name"] == "Bruno")
    assert bruno["status"] == "Inactive"
    assert bruno["status_detail"] == ""


def test_migrations_creates_performance_indexes_idempotently():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    migrate_database(engine)
    migrate_database(engine)

    insp = inspect(engine)
    grade_indexes = {idx["name"] for idx in insp.get_indexes("grades")}
    assert "ix_grades_student_id" in grade_indexes
    assert "ix_grades_assessment_id" in grade_indexes


def test_credentials_file_fallback_permissions_and_delete(tmp_path, monkeypatch):
    secrets_file = tmp_path / "secrets.json"
    monkeypatch.setattr(credentials, "SECRETS_FILE", secrets_file)
    monkeypatch.setattr(credentials.keyring, "set_password", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("no keyring")))
    monkeypatch.setattr(credentials.keyring, "get_password", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("no keyring")))
    monkeypatch.setattr(credentials.keyring, "delete_password", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("no keyring")))

    credentials.save_api_key("OpenAI", "sk-test-123")
    assert credentials.get_api_key("OpenAI") == "sk-test-123"
    if os.name == "posix":
        assert (secrets_file.stat().st_mode & 0o777) == 0o600

    credentials.delete_api_key("OpenAI")
    assert credentials.get_api_key("OpenAI") is None


def test_update_student_name_tool_preserves_birth_date(data_service, monkeypatch):
    monkeypatch.setattr(database_tools, "data_service", data_service)
    s = data_service.add_student("Joana", "Silva", birth_date=date(2010, 4, 15))

    result = database_tools.update_student_name("Joana Silva", "Joana", "Oliveira")
    assert "Nome atualizado" in result

    updated = data_service.get_student_by_id(s["id"])
    assert updated["last_name"] == "Oliveira"
    assert updated["birth_date"] == "2010-04-15"
