# -*- coding: utf-8 -*-
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

"""
Este módulo fornece funcionalidades para análise e divisão de nomes completos em
primeiro nome e sobrenome, com suporte especial para nomes compostos comuns no Brasil.
"""

# Lista dos 100 nomes compostos mais comuns no Brasil.
# Fontes:
# - https://www.pampers.com.br/gravidez/nomes-para-o-bebe/artigo/nomes-compostos-para-meninos-e-meninas
# - https://bebe.abril.com.br/nomes-de-bebe/100-nomes-compostos-para-meninas/
# - https://bebe.abril.com.br/nomes-de-bebe/50-nomes-compostos-para-meninos/
# A lista foi compilada e normalizada para maiúsculas para consistência.
COMMON_COMPOUND_NAMES = [
    "ANA BEATRIZ", "ANA CAROLINA", "ANA CLARA", "ANA JULIA", "ANA LAURA", "ANA LUIZA",
    "ANNE GABRIELLY", "ANTONIO CARLOS", "BRUNO HENRIQUE", "CAIO ALEXANDRE",
    "CARLOS ALBERTO", "CARLOS EDUARDO", "CARLOS HENRIQUE", "DAVI LUCAS", "DAVI LUIZ",
    "ENZO GABRIEL", "ENZO MIGUEL", "ERICK GABRIEL", "FERNANDA CATARINA", "FRANCISCO JOSE",
    "GABRIEL HENRIQUE", "GUSTAVO HENRIQUE", "HEITOR GABRIEL", "HELENA BEATRIZ",
    "HENRIQUE GABRIEL", "IGOR GABRIEL", "JOAO AUGUSTO", "JOAO BATISTA", "JOAO CARLOS",
    "JOAO FELIPE", "JOAO GABRIEL", "JOAO GUILHERME", "JOAO HENRIQUE", "JOAO LUCAS",
    "JOAO LUIZ", "JOAO MARCOS", "JOAO MIGUEL", "JOAO PAULO", "JOAO PEDRO", "JOAO VITOR",
    "JOSE CARLOS", "JOSE HENRIQUE", "JOSE LUIZ", "JOSE MIGUEL", "JUAN GUILHERME",
    "JULIA BEATRIZ", "JULIA GABRIELA", "JULIA VITORIA", "KAUA GABRIEL", "LAURA BEATRIZ",
    "LAURA SOFIA", "LORENZO GABRIEL", "LUCAS GABRIEL", "LUCAS HENRIQUE", "LUIZ ANTONIO",
    "LUIZ CARLOS", "LUIZ EDUARDO", "LUIZ FELIPE", "LUIZ FERNANDO", "LUIZ GUSTAVO",
    "LUIZ HENRIQUE", "LUIZ MIGUEL", "LUIZA HELENA", "MARCELA VITORIA", "MARCO ANTONIO",
    "MARCOS PAULO", "MARIA ALICE", "MARIA ANTONIA", "MARIA BEATRIZ", "MARIA CECILIA",
    "MARIA CLARA", "MARIA EDUARDA", "MARIA FERNANDA", "MARIA FLOR", "MARIA HELENA",
    "MARIA ISABEL", "MARIA JULIA", "MARIA LAURA", "MARIA LUIZA", "MARIA VALENTINA",
    "MARIA VITORIA", "MIGUEL HENRIQUE", "NICOLAS GABRIEL", "PAULO ANDRE", "PAULO CESAR",
    "PAULO HENRIQUE", "PAULO RICARDO", "PAULO ROBERTO", "PAULO SERGIO", "PAULO VICTOR",
    "PEDRO AFONSO", "PEDRO ARTHUR", "PEDRO AUGUSTO", "PEDRO DANIEL", "PEDRO ENRIQUE",
    "PEDRO GABRIEL", "PEDRO HENRIQUE", "PEDRO LUCAS", "PEDRO MIGUEL", "PIETRO GABRIEL",
    "RYAN GABRIEL", "VICTOR HUGO", "VITOR GABRIEL", "YASMIN VITORIA", "YURI GABRIEL"
]


import unicodedata


def _normalize_text(text: str) -> str:
    """Remove acentos e converte o texto para maiúsculas para comparação."""
    normalized = unicodedata.normalize("NFD", text)
    without_accents = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return without_accents.upper()


def split_full_name(full_name, compound_names_list=None):
    """
    Divide um nome completo em primeiro nome e sobrenome. Este método leva em consideração
    uma lista pré-definida de nomes compostos para identificar corretamente os nomes que
    devem ser tratados como um único primeiro nome. Caso nenhum nome composto seja identificado,
    o nome é dividido com base no primeiro espaço encontrado.

    :param full_name: O nome completo a ser dividido.
    :type full_name: str
    :param compound_names_list: Uma lista opcional de nomes compostos para auxiliar
        na divisão dos nomes. Se não fornecida, será usada uma lista padrão.
    :type compound_names_list: list[str], optional
    :return: Uma tupla contendo o primeiro nome e o sobrenome correspondentes.
    :rtype: tuple[str, str]
    """
    if compound_names_list is None:
        compound_names_list = COMMON_COMPOUND_NAMES
    if not full_name:
        return "", ""

    cleaned_name = " ".join(full_name.strip().split())
    if not cleaned_name:
        return "", ""

    words = cleaned_name.split(" ")
    normalized_words = [_normalize_text(w) for w in words]

    for compound_name in compound_names_list:
        compound_parts = _normalize_text(compound_name).split()
        part_count = len(compound_parts)
        if len(words) > part_count and normalized_words[:part_count] == compound_parts:
            first_name = " ".join(words[:part_count])
            last_name = " ".join(words[part_count:]).strip()
            return first_name, last_name

    # Caso não corresponda a um nome composto, divide na primeira palavra.
    first_name = words[0]
    last_name = " ".join(words[1:]).strip()
    return first_name, last_name
