# -*- coding: utf-8 -*-

"""
Este módulo contém a lógica de importação de alunos via CSV que foi desativada.

A abordagem original utilizava um provedor de Large Language Model (LLM) para
analisar o conteúdo de arquivos CSV e extrair de forma inteligente os dados
dos alunos, incluindo a complexa tarefa de dividir nomes completos em nome e
sobrenome.

-------------------------------------------------------------------------------
Visão Geral da Lógica Antiga
-------------------------------------------------------------------------------
1.  **`parse_student_csv_with_ai`**:
    -   Esta função recebia o conteúdo de texto de um arquivo CSV.
    -   Ela enviava o texto completo para a IA com um prompt detalhado,
        solicitando a extração dos dados dos alunos.
    -   A expectativa era que a IA retornasse uma string JSON contendo uma
        lista de dicionários, cada um representando um aluno com os campos
        'full_name', 'first_name', 'last_name', 'birth_date', e 'status'.

2.  **`split_full_name` (Função Auxiliar)**:
    -   Originalmente, o plano era processar o CSV linha por linha, e esta
        função seria chamada para cada nome de aluno.
    -   Ela enviava um único nome completo para a IA e pedia a divisão em
        nome e sobrenome, retornando um JSON.
    -   Esta abordagem se mostrou muito lenta devido à alta latência de
        múltiplas chamadas de rede.

-------------------------------------------------------------------------------
Motivo da Desativação
-------------------------------------------------------------------------------
A importação baseada em IA foi desativada por duas razões principais:

1.  **Falta de Confiabilidade**: O provedor de IA nem sempre retornava um
    JSON válido. Muitas vezes, a resposta incluía texto conversacional
    adicional (e.g., "Aqui está o JSON que você pediu: ```json...```"), o
    que causava falhas na análise do JSON. Além disso, a IA por vezes
    "alucinava" dados incorretos, como datas de nascimento inválidas.

2.  **Performance e Custo**: A abordagem de fazer uma chamada de API para cada
    aluno (`split_full_name`) era inviável em termos de velocidade. A abordagem
    de enviar o arquivo inteiro (`parse_student_csv_with_ai`) era mais rápida,
    mas ainda significativamente mais lenta e mais cara (em termos de uso de API)
    do que uma solução determinística.

A funcionalidade foi substituída por um parser determinístico localizado em
`app/utils/student_csv_parser.py` que utiliza uma lógica baseada em uma lista
de nomes compostos comuns para alcançar um resultado mais rápido e confiável.
"""

import json

# Dependências que seriam necessárias se este código estivesse ativo.
# from app.core.llm.base import LLMProvider


class LegacyAiCsvParser:
    """
    Encapsula a lógica de parsing de CSV que dependia de um provedor de IA.
    """
    def __init__(self, provider):
        """
        Inicializa o parser com um provedor de IA.

        Args:
            provider (LLMProvider): Uma instância de um provedor de LLM.
        """
        self.provider = provider

    async def split_full_name(self, full_name: str) -> tuple[str, str]:
        """
        (Desativado) Divide um nome completo em nome e sobrenome usando IA.
        """
        def simple_split(name):
            parts = name.split()
            return parts[0], " ".join(parts[1:])

        if not self.provider or not full_name:
            return simple_split(full_name)

        try:
            prompt = (
                "You are a linguistic expert specializing in Brazilian names. "
                "Your task is to separate a full name into a first name and a last name. "
                "The first name may be composite (e.g., 'Ana Julia', 'Maria Clara'). "
                "Respond with only a JSON object with two keys: 'first_name' and 'last_name'.\\n\\n"
                f'Full name: \\"{full_name}\\"'
            )
            messages = [{"role": "user", "content": prompt}]
            response = await self.provider.get_chat_response(messages)

            if response.content:
                try:
                    name_parts = json.loads(response.content)
                    first_name = name_parts.get('first_name')
                    last_name = name_parts.get('last_name')
                    if first_name and last_name:
                        return first_name, last_name
                except (json.JSONDecodeError, KeyError):
                    print(f"AI response for name splitting was not valid JSON: {response.content}")

        except Exception as e:
            print(f"An error occurred during AI name splitting: {e}")

        return simple_split(full_name)

    async def parse_student_csv_with_ai(self, csv_content: str) -> list[dict]:
        """
        (Desativado) Usa uma única chamada de IA para analisar o conteúdo de um CSV.
        """
        if not self.provider:
            raise RuntimeError("AI provider is not configured.")

        prompt = (
            "You are an expert data extraction assistant. Analyze the following text... " # Prompt omitido por brevidade
            f'"""{csv_content}"""'
        )
        messages = [{"role": "user", "content": prompt}]

        try:
            response = await self.provider.get_chat_response(messages)

            if not response or not response.content:
                raise RuntimeError("AI provider returned an empty response.")

            if response.content.strip().startswith("Error:"):
                raise RuntimeError(f"The AI provider reported an error: {response.content.strip()}")

            cleaned_json_str = response.content.strip().replace("```json", "").replace("```", "").strip()

            if not cleaned_json_str:
                raise RuntimeError("AI provider returned an empty JSON string.")

            return json.loads(cleaned_json_str)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse CSV with AI: Invalid JSON format. Error: {e}") from e
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred while parsing CSV with AI: {e}") from e
