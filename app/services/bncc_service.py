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
import json
import logging
from app.utils.path_utils import get_resource_path


class BNCCService:
    _data = None
    _code_index = None

    @classmethod
    def load_data(cls):
        if cls._data is None:
            loaded = []

            # Carrega BNCC Educação Infantil
            try:
                path = get_resource_path("app/data/bncc_infantil.json")
                with open(path, 'r', encoding='utf-8') as f:
                    loaded.extend(json.load(f))
            except Exception as e:
                logging.error(f"Erro ao carregar BNCC Infantil: {e}")

            # Carrega BNCC Ensino Fundamental
            try:
                path = get_resource_path("app/data/bncc_fundamental.json")
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    loaded.extend(cls._process_fundamental(data))
            except Exception as e:
                logging.error(f"Erro ao carregar BNCC Fundamental: {e}")

            # Carrega BNCC Ensino Médio
            try:
                path = get_resource_path("app/data/bncc_medio.json")
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    loaded.extend(cls._process_medio(data))
            except Exception as e:
                logging.error(f"Erro ao carregar BNCC Médio: {e}")

            # Só fixa o cache se ao menos um arquivo foi carregado (permite retry em falha transitória)
            if loaded:
                cls._data = loaded
                cls._build_index()
            else:
                return []

        return cls._data

    @classmethod
    def _build_index(cls):
        """Constrói índice O(1) por código de habilidade BNCC."""
        index = {}
        for group in cls._data or []:
            group_title = group.get('title', '')
            for item in group.get('itens', []):
                code = item.get('code', '').strip().upper()
                if code:
                    index[code] = {
                        "code": item['code'],
                        "description": item['description'],
                        "title": group_title,
                    }
        cls._code_index = index

    @classmethod
    def _process_fundamental(cls, data) -> list[dict]:
        """Normaliza os dados do Ensino Fundamental na estrutura padrão."""
        result = []
        for discipline_key, content in data.items():
            discipline_name = discipline_key.replace('_', ' ').title()
            for ano_group in content.get('ano', []):
                anos = ", ".join(ano_group.get('nome_ano', []))

                for unidade in ano_group.get('unidades_tematicas', []):
                    title = f"{discipline_name} - {unidade.get('nome_unidade', '')} ({anos})"

                    items = []
                    for objeto in unidade.get('objeto_conhecimento', []):
                        obj_name = objeto.get('nome_objeto', '')
                        for hab in objeto.get('habilidades', []):
                            raw_text = hab.get('nome_habilidade', '')
                            code = ""
                            desc = raw_text

                            if raw_text.startswith('('):
                                end_idx = raw_text.find(')')
                                if end_idx != -1:
                                    code = raw_text[1:end_idx]
                                    desc = raw_text[end_idx + 1:].strip()

                            items.append({
                                "code": code,
                                "description": f"{obj_name}: {desc}",
                                "range": anos
                            })

                    if items:
                        result.append({
                            "title": title,
                            "itens": items
                        })
        return result

    @classmethod
    def _process_medio(cls, data) -> list[dict]:
        """Normaliza os dados do Ensino Médio na estrutura padrão."""
        result = []
        for discipline_key, content in data.items():
            discipline_name = content.get('nome_disciplina', discipline_key.replace('_', ' ').title())

            for ano_group in content.get('ano', []):
                anos = ", ".join(ano_group.get('nome_ano', []))

                items = []
                for hab in ano_group.get('codigo_habilidade', []):
                    code = hab.get('nome_codigo', '')
                    desc = hab.get('nome_habilidade', '')

                    items.append({
                        "code": code,
                        "description": desc,
                        "range": anos
                    })

                if items:
                    result.append({
                        "title": f"{discipline_name} ({anos})",
                        "itens": items
                    })
        return result

    @classmethod
    def search_skills(cls, query: str = "") -> list[dict]:
        """
        Pesquisa habilidades da BNCC.
        Retorna uma lista de dicionários: {'code': str, 'description': str, 'title': str}
        """
        data = cls.load_data()
        results = []
        query = query.lower().strip()

        for group in data:
            group_title = group.get('title', '')
            for item in group.get('itens', []):
                code = item.get('code', '')
                description = item.get('description', '')

                if not query or (query in code.lower() or query in description.lower() or query in group_title.lower()):
                    results.append({
                        "code": code,
                        "description": description,
                        "title": group_title
                    })
        return results

    @classmethod
    def get_skill_by_code(cls, code: str) -> dict | None:
        cls.load_data()
        if not cls._code_index:
            return None
        return cls._code_index.get(code.strip().upper())
