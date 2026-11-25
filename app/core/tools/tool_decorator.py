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
import inspect
import re
import types
from functools import wraps
from typing import Union, get_args, get_origin


def _resolve_json_type(annotation) -> str:
    """Resolve anotações de tipo Python (inclusive Optional/Union/List/Dict) para tipos JSON Schema."""
    if annotation is inspect.Parameter.empty or annotation is None:
        return "string"

    origin = get_origin(annotation)
    if origin in (Union, types.UnionType):
        non_none_args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if non_none_args:
            return _resolve_json_type(non_none_args[0])
        return "string"
    if origin in (list, tuple, set):
        return "array"
    if origin is dict:
        return "object"

    type_mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }
    if annotation in type_mapping:
        return type_mapping[annotation]

    type_name = getattr(annotation, "__name__", str(annotation))
    name_mapping = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "list": "array",
        "dict": "object",
    }
    return name_mapping.get(type_name, "string")


def _extract_param_descriptions(docstring: str | None) -> dict[str, str]:
    """Extrai descrições de parâmetros no formato ':param nome: descrição' da docstring."""
    if not docstring:
        return {}
    descriptions = {}
    for match in re.finditer(r":param\s+(\w+)\s*:\s*(.+)", docstring):
        descriptions[match.group(1)] = match.group(2).strip()
    return descriptions


def tool(func):
    """
    Decora uma função para gerar um esquema JSON Schema com base na assinatura e na
    docstring da função. Suporta tipos simples e compostos (Optional, Union, List, Dict).

    :param func: A função que será decorada.
    :return: Função decorada com o esquema JSON Schema anexado no atributo `schema`.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    func_sig = inspect.signature(func)
    docstring = inspect.getdoc(func)
    param_descriptions = _extract_param_descriptions(docstring)

    schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }

    if docstring:
        schema["function"]["description"] = docstring.strip().split('\n')[0]

    for name, param in func_sig.parameters.items():
        param_type = _resolve_json_type(param.annotation)
        description = param_descriptions.get(name, f"Parâmetro '{name}' da função.")

        schema["function"]["parameters"]["properties"][name] = {
            "type": param_type,
            "description": description,
        }

        if param.default is inspect.Parameter.empty:
            schema["function"]["parameters"]["required"].append(name)

    wrapper.schema = schema
    return wrapper
