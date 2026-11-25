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
import logging
from typing import List, Dict, Any, Callable


class ToolRegistry:
    """
    Gerenciador de ferramentas registradas para o Assistente de IA.

    :ivar tools: Dicionário que associa o nome da ferramenta à função correspondente.
    :ivar schemas: Lista dos esquemas JSON de todas as ferramentas registradas.
    """
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self._schemas_by_name: Dict[str, Dict[str, Any]] = {}
        self.schemas: List[Dict[str, Any]] = []

    def register(self, tool_func: Callable):
        """Registra uma função ferramenta decorada com @tool, sem duplicar schemas."""
        func: Any = tool_func
        if not hasattr(func, 'schema'):
            raise ValueError(
                f"A função '{func.__name__}' não é uma ferramenta válida. Esqueceu o decorador @tool?"
            )

        tool_name = func.schema["function"]["name"]
        self.tools[tool_name] = func
        self._schemas_by_name[tool_name] = func.schema
        self.schemas = list(self._schemas_by_name.values())
        logging.debug(f"Ferramenta registrada: {tool_name}")

    def get_tool(self, name: str) -> Callable | None:
        """Recupera uma função ferramenta pelo nome."""
        return self.tools.get(name)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Retorna os esquemas JSON de todas as ferramentas registradas."""
        return list(self.schemas)
