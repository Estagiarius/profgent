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
import asyncio
import inspect
import json
from typing import Dict, Any
from app.core.tools.tool_registry import ToolRegistry


class ToolExecutor:
    """
    Gerencia a execução segura de ferramentas solicitadas pelo LLM.
    """
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def _parse_arguments(self, raw_arguments: Any) -> Dict[str, Any]:
        """Converte argumentos (dict ou JSON string) em dicionário válido."""
        if raw_arguments is None or raw_arguments == "":
            return {}
        if isinstance(raw_arguments, dict):
            return raw_arguments
        if isinstance(raw_arguments, str):
            parsed = json.loads(raw_arguments)
            if parsed is None:
                return {}
            if not isinstance(parsed, dict):
                raise ValueError("Os argumentos devem ser um objeto JSON.")
            return parsed
        raise ValueError("Formato de argumentos não suportado.")

    def execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Executa de forma síncrona uma chamada de ferramenta solicitada pelo LLM."""
        tool_call_id = tool_call['id']
        tool_name = tool_call['function']['name']
        tool_function = self.registry.get_tool(tool_name)

        if not tool_function:
            return self._create_error_result(tool_call_id, tool_name, f"Ferramenta '{tool_name}' não encontrada.")

        try:
            arguments = self._parse_arguments(tool_call['function'].get('arguments'))
            result = tool_function(**arguments)
            return self._create_success_result(tool_call_id, tool_name, result)
        except json.JSONDecodeError:
            return self._create_error_result(tool_call_id, tool_name, "Formato de argumentos inválido. Esperado um JSON válido.")
        except (TypeError, ValueError) as e:
            return self._create_error_result(tool_call_id, tool_name, f"Argumentos inválidos para a ferramenta '{tool_name}': {e}")
        except Exception as e:
            return self._create_error_result(tool_call_id, tool_name, f"Erro inesperado ao executar '{tool_name}': {e}")

    async def execute_tool_call_async(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma chamada de ferramenta sem bloquear o event loop asyncio.
        Suporta tanto ferramentas assíncronas quanto síncronas (via asyncio.to_thread).
        """
        tool_call_id = tool_call['id']
        tool_name = tool_call['function']['name']
        tool_function = self.registry.get_tool(tool_name)

        if not tool_function:
            return self._create_error_result(tool_call_id, tool_name, f"Ferramenta '{tool_name}' não encontrada.")

        try:
            arguments = self._parse_arguments(tool_call['function'].get('arguments'))
            if inspect.iscoroutinefunction(tool_function) or inspect.iscoroutinefunction(getattr(tool_function, "__wrapped__", None)):
                result = await tool_function(**arguments)
            else:
                result = await asyncio.to_thread(tool_function, **arguments)
            return self._create_success_result(tool_call_id, tool_name, result)
        except json.JSONDecodeError:
            return self._create_error_result(tool_call_id, tool_name, "Formato de argumentos inválido. Esperado um JSON válido.")
        except (TypeError, ValueError) as e:
            return self._create_error_result(tool_call_id, tool_name, f"Argumentos inválidos para a ferramenta '{tool_name}': {e}")
        except Exception as e:
            return self._create_error_result(tool_call_id, tool_name, f"Erro inesperado ao executar '{tool_name}': {e}")

    @staticmethod
    def _create_success_result(tool_call_id: str, tool_name: str, result: Any) -> Dict[str, Any]:
        return {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "name": tool_name,
            "content": str(result),
        }

    @staticmethod
    def _create_error_result(tool_call_id: str, tool_name: str, error_message: str) -> Dict[str, Any]:
        return {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "name": tool_name,
            "content": f"Erro: {error_message}",
        }
