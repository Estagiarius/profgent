# -*- coding: utf-8 -*-

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


def split_full_name(full_name, compound_names_list=COMMON_COMPOUND_NAMES):
    """
    Divide um nome completo em primeiro nome e sobrenome.

    A lógica prioriza nomes compostos. Se o início do nome completo corresponder
    a um nome composto da lista, ele será considerado o primeiro nome. Caso contrário,
    apenas a primeira palavra será o primeiro nome.

    Args:
        full_name (str): O nome completo a ser dividido.
        compound_names_list (list): Uma lista de nomes compostos a serem considerados.

    Returns:
        tuple: Uma tupla contendo (primeiro_nome, sobrenome).
    """
    if not full_name:
        return "", ""

    full_name_upper = full_name.upper()

    # Verifica se o nome começa com algum nome composto da lista
    for compound_name in compound_names_list:
        if full_name_upper.startswith(compound_name + " "):
            # Encontrou um nome composto
            first_name_end_index = len(compound_name)
            first_name = full_name[:first_name_end_index]
            last_name = full_name[first_name_end_index:].strip()
            return first_name, last_name

    # Se nenhum nome composto for encontrado, usa a lógica padrão (primeira palavra)
    parts = full_name.split(" ")
    first_name = parts[0]
    last_name = " ".join(parts[1:]).strip()

    return first_name, last_name
