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
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.core.llm.base import AssistantResponse
from app.services.assistant_service import AssistantService


@pytest.mark.anyio
async def test_assistant_preserves_history_across_turns(mocker):
    """Garante que o histórico da conversa não é apagado entre turnos."""
    mocker.patch("app.services.assistant_service.AssistantService._initialize_provider")
    service = AssistantService()

    mock_provider = MagicMock()
    mock_provider.name = "OpenAI"
    mock_provider.get_chat_response = AsyncMock(
        side_effect=[
            AssistantResponse(content="Olá! Como posso ajudar?"),
            AssistantResponse(content="Você disse Olá no turno anterior."),
        ]
    )
    mock_provider.close = AsyncMock()
    service.provider = mock_provider

    r1 = await service.get_response("Olá")
    r2 = await service.get_response("O que eu disse antes?")

    assert r1.content == "Olá! Como posso ajudar?"
    assert r2.content == "Você disse Olá no turno anterior."
    # system + user1 + assistant1 + user2 + assistant2 = 5 mensagens
    assert len(service.messages) == 5
    assert service.messages[1] == {"role": "user", "content": "Olá"}
    assert service.messages[3] == {"role": "user", "content": "O que eu disse antes?"}

    service.clear_history()
    assert len(service.messages) == 1
    assert service.messages[0]["role"] == "system"


@pytest.mark.anyio
async def test_assistant_multi_turn_tool_calls(mocker):
    """Garante que o AssistantService suporta múltiplas rodadas encadeadas de tool calls."""
    mocker.patch("app.services.assistant_service.AssistantService._initialize_provider")
    service = AssistantService()

    mock_provider = MagicMock()
    mock_provider.name = "OpenAI"
    mock_provider.get_chat_response = AsyncMock(
        side_effect=[
            AssistantResponse(
                content="",
                tool_calls=[{"id": "c1", "function": {"name": "list_all_classes", "arguments": "{}"}}],
            ),
            AssistantResponse(
                content="",
                tool_calls=[{"id": "c2", "function": {"name": "list_all_courses", "arguments": "{}"}}],
            ),
            AssistantResponse(content="Consulta encadeada concluída com sucesso."),
        ]
    )
    service.provider = mock_provider

    mocker.patch.object(
        service.tool_executor,
        "execute_tool_call_async",
        new=AsyncMock(
            side_effect=[
                {"tool_call_id": "c1", "role": "tool", "name": "list_all_classes", "content": "Turma 1A"},
                {"tool_call_id": "c2", "role": "tool", "name": "list_all_courses", "content": "Matemática"},
            ]
        ),
    )

    response = await service.get_response("Liste turmas e depois disciplinas.")
    assert response.content == "Consulta encadeada concluída com sucesso."
    assert mock_provider.get_chat_response.await_count == 3


def test_assistant_registers_safe_tools_and_excludes_destructive(mocker):
    """Verifica que ferramentas seguras estão registradas e destrutivas permanecem fora."""
    mocker.patch("app.services.assistant_service.AssistantService._initialize_provider")
    service = AssistantService()
    registered_names = set(service.tool_registry.tools.keys())

    assert "get_global_dashboard_stats_tool" in registered_names
    assert "get_global_performance_stats_tool" in registered_names
    assert "global_search_tool" in registered_names
    assert "delete_student" not in registered_names
    assert "delete_class" not in registered_names
    assert "delete_course" not in registered_names
