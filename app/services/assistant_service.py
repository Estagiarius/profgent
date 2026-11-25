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
# Importa a classe base para provedores de LLM e a estrutura de resposta do assistente.
from app.core.llm.base import LLMProvider, AssistantResponse
# Importa o provedor específico para a API da OpenAI.
from app.core.llm.openai_provider import OpenAIProvider
# Importa o provedor específico para a API da Maritaca.
from app.core.llm.maritaca_provider import MaritacaProvider
# Importa o provedor específico para a API do OpenRouter.
from app.core.llm.open_router_provider import OpenRouterProvider
# Importa o provedor específico para rodar modelos localmente com Ollama.
from app.core.llm.ollama_provider import OllamaProvider
# Importa a função para obter chaves de API de forma segura.
from app.core.security.credentials import get_api_key
# Importa a função para carregar configurações salvas.
from app.core.config import load_setting
# Importa o registro de ferramentas, que gerencia as ferramentas disponíveis para a IA.
from app.core.tools.tool_registry import ToolRegistry
# Importa o executor de ferramentas, que executa as chamadas de função da IA.
from app.core.tools.tool_executor import ToolExecutor

# --- Importação das Ferramentas (Tools) ---
# Importa as ferramentas de leitura e escrita do banco de dados.
from app.tools.database_tools import (
    get_student_grades_by_course, list_courses_for_student,
    list_all_classes, get_class_roster,
    add_new_student, add_new_course, add_new_grade,
    create_new_class, add_subject_to_class, create_new_assessment,
    add_new_lesson, register_incident,
    update_student_name, enroll_existing_student,
    list_all_courses,
    global_search_tool, get_class_full_details_tool,
    get_incidents_for_class, get_assessments_for_subject,
    get_lessons_for_subject, get_unenrolled_students,
    get_students_with_birthday_today, search_students,
    get_attendance_stats_tool,
)
# Importa as ferramentas de busca na internet.
from app.tools.internet_tools import search_internet
# Importa as ferramentas de análise de dados.
from app.tools.analysis_tools import (
    get_student_performance_summary_tool,
    get_students_at_risk_tool,
    get_global_dashboard_stats_tool,
    get_global_performance_stats_tool,
    get_class_incident_ranking_tool,
)
# Importa as ferramentas com foco pedagógico.
from app.tools.pedagogical_tools import suggest_lesson_activities_tool
# Importa as ferramentas de relatórios e gráficos.
from app.tools.report_tools import (
    generate_grade_chart_tool, generate_class_distribution_tool,
    export_class_grades_tool, generate_report_card_tool
)
# Importa as ferramentas estendidas de horário, mapa de sala, BNCC e médias bimestrais.
from app.tools.academic_extended_tools import (
    get_weekly_schedule_tool,
    list_seating_charts_tool,
    search_bncc_skills_tool,
    get_bncc_coverage_tool,
    get_student_period_averages_tool,
)

SYSTEM_PROMPT = (
    "Você é um assistente de gestão acadêmica especializado, integrado a um aplicativo de desktop. "
    "Sua função principal é ajudar os usuários a gerenciar dados de alunos, cursos e notas usando um "
    "conjunto predefinido de ferramentas. Você deve seguir as seguintes regras estritamente:\n"
    "1.  **Use Ferramentas Exclusivamente**: Você DEVE usar as ferramentas fornecidas para responder a perguntas e realizar ações. "
    "Não ofereça realizar ações que não são suportadas pelas ferramentas.\n"
    "2.  **Sem Geração de Código**: Você NÃO DEVE gerar, escrever ou sugerir qualquer código (ex: Python, SQL). "
    "Seu papel é usar as ferramentas, não ser um programador.\n"
    "3.  **Admita Limitações**: Se você não puder atender a uma solicitação com as ferramentas disponíveis, declare claramente que "
    "não pode fazê-lo e explique a limitação. Não invente ferramentas ou funcionalidades.\n"
    "4.  **Clareza e Confirmação**: Após executar uma ferramenta que modifica dados (ex: adicionar um aluno), "
    "sempre confirme o sucesso da ação em uma mensagem clara e amigável, com base na saída da ferramenta.\n"
    "5.  **Planejamento de Aulas**: Se o usuário solicitar a criação de um plano de aula, gere primeiro o conteúdo "
    "estruturado (Objetivos, Conteúdo, Atividades, Avaliação) no chat. Após a aprovação do usuário, "
    "use a ferramenta `add_new_lesson` para salvar esse conteúdo na disciplina e turma apropriadas."
)


class AssistantService:
    """
    Orquestra o assistente de gestão acadêmica integrado à aplicação desktop.
    Mantém o histórico da conversa, gerencia o ciclo de vida do provedor LLM e
    executa chamadas de ferramentas em múltiplas rodadas de forma não bloqueante.
    """

    MAX_TOOL_ITERATIONS = 5

    def __init__(self):
        self.provider: LLMProvider | None = None
        self._provider_config_signature: tuple | None = None
        self.messages: list = [{"role": "system", "content": SYSTEM_PROMPT}]

        self.tool_registry = ToolRegistry()
        self._register_tools()
        self.tool_executor = ToolExecutor(self.tool_registry)

        self._initialize_provider()

    def _register_tools(self):
        # Ferramentas de leitura e consulta
        self.tool_registry.register(get_student_grades_by_course)
        self.tool_registry.register(list_courses_for_student)
        self.tool_registry.register(list_all_classes)
        self.tool_registry.register(get_class_roster)
        self.tool_registry.register(list_all_courses)
        self.tool_registry.register(global_search_tool)
        self.tool_registry.register(get_class_full_details_tool)
        self.tool_registry.register(get_incidents_for_class)
        self.tool_registry.register(get_assessments_for_subject)
        self.tool_registry.register(get_lessons_for_subject)
        self.tool_registry.register(get_unenrolled_students)
        self.tool_registry.register(get_students_with_birthday_today)
        self.tool_registry.register(search_students)
        self.tool_registry.register(get_attendance_stats_tool)
        # Ferramentas de análise
        self.tool_registry.register(get_student_performance_summary_tool)
        self.tool_registry.register(get_students_at_risk_tool)
        self.tool_registry.register(get_global_dashboard_stats_tool)
        self.tool_registry.register(get_global_performance_stats_tool)
        self.tool_registry.register(get_class_incident_ranking_tool)
        # Ferramentas de horário, mapa de sala, BNCC e médias bimestrais
        self.tool_registry.register(get_weekly_schedule_tool)
        self.tool_registry.register(list_seating_charts_tool)
        self.tool_registry.register(search_bncc_skills_tool)
        self.tool_registry.register(get_bncc_coverage_tool)
        self.tool_registry.register(get_student_period_averages_tool)
        # Ferramentas pedagógicas
        self.tool_registry.register(suggest_lesson_activities_tool)
        # Ferramentas de relatórios
        self.tool_registry.register(generate_grade_chart_tool)
        self.tool_registry.register(generate_class_distribution_tool)
        self.tool_registry.register(export_class_grades_tool)
        self.tool_registry.register(generate_report_card_tool)
        # Ferramentas de internet
        self.tool_registry.register(search_internet)
        # Ferramentas de escrita não destrutivas
        self.tool_registry.register(add_new_student)
        self.tool_registry.register(add_new_course)
        self.tool_registry.register(add_new_grade)
        self.tool_registry.register(create_new_class)
        self.tool_registry.register(add_subject_to_class)
        self.tool_registry.register(create_new_assessment)
        self.tool_registry.register(add_new_lesson)
        self.tool_registry.register(register_incident)
        self.tool_registry.register(update_student_name)
        self.tool_registry.register(enroll_existing_student)

    def clear_history(self):
        """Reinicia o histórico da conversa mantendo apenas o prompt de sistema."""
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def _get_current_provider_config(self) -> tuple:
        """Retorna uma assinatura imutável da configuração atual do provedor de LLM."""
        active_provider_name = load_setting("active_provider", "OpenAI")
        model_config_key = f"{active_provider_name.lower()}_model"

        if active_provider_name == "Ollama":
            ollama_url = load_setting("ollama_url", "http://localhost:11434/v1")
            selected_model = load_setting(model_config_key, "llama3.1")
            return ("Ollama", ollama_url, selected_model, None)

        api_key = get_api_key(active_provider_name)
        default_models = {
            "OpenAI": "gpt-4",
            "Maritaca": "sabia-3",
            "OpenRouter": "mistralai/mistral-7b-instruct:free",
        }
        selected_model = load_setting(model_config_key, default_models.get(active_provider_name, ""))
        return (active_provider_name, None, selected_model, api_key)

    def _build_provider_from_config(self, config: tuple) -> LLMProvider | None:
        """Instancia o provedor correspondente à assinatura de configuração fornecida."""
        provider_name, base_url, selected_model, api_key = config

        if provider_name == "Ollama":
            return OllamaProvider(base_url=base_url, model=selected_model)

        if not api_key:
            return None

        if provider_name == "OpenAI":
            return OpenAIProvider(api_key=api_key, model=selected_model)
        if provider_name == "Maritaca":
            return MaritacaProvider(api_key=api_key, model=selected_model)
        if provider_name == "OpenRouter":
            return OpenRouterProvider(api_key=api_key, model=selected_model)
        return None

    def _initialize_provider(self):
        """Inicializa o provedor de LLM ativo sem apagar o histórico da conversa."""
        config = self._get_current_provider_config()
        if self.provider is not None and config == self._provider_config_signature:
            return
        self.provider = self._build_provider_from_config(config)
        self._provider_config_signature = config if self.provider is not None else None
        if not self.messages:
            self.clear_history()

    async def _ensure_provider_async(self):
        """Garante que o provedor esteja atualizado, fechando o provedor anterior caso tenha mudado."""
        config = self._get_current_provider_config()
        if self.provider is not None and config == self._provider_config_signature:
            return
        if self.provider is not None:
            try:
                await self.provider.close()
            except Exception:
                pass
        self.provider = self._build_provider_from_config(config)
        self._provider_config_signature = config if self.provider is not None else None
        if not self.messages:
            self.clear_history()

    async def get_response(self, user_input: str) -> AssistantResponse:
        # Atualiza provedor apenas se a configuração mudou (preservando o histórico da conversa).
        if self.provider is None or self._provider_config_signature is not None:
            await self._ensure_provider_async()

        if not self.provider:
            return AssistantResponse(content="Provedor de IA não configurado. Verifique as configurações e a chave de API.")

        if not self.messages:
            self.clear_history()

        self.messages.append({"role": "user", "content": user_input})

        tool_schemas = (
            self.tool_registry.get_all_schemas()
            if self.provider.name in ["OpenAI", "OpenRouter", "Ollama"]
            else None
        )

        response = await self.provider.get_chat_response(self.messages, tools=tool_schemas)

        # Loop multi-turn de chamadas de ferramentas com limite de segurança.
        iterations = 0
        while response.tool_calls and iterations < self.MAX_TOOL_ITERATIONS:
            iterations += 1
            tool_calls_list = response.tool_calls if isinstance(response.tool_calls, list) else [response.tool_calls]
            self.messages.append({"role": "assistant", "tool_calls": tool_calls_list})

            tool_results = []
            for tool_call in tool_calls_list:
                result = await self.tool_executor.execute_tool_call_async(tool_call)
                tool_results.append(result)

            self.messages.extend(tool_results)
            response = await self.provider.get_chat_response(self.messages, tools=tool_schemas)

        if response.content:
            self.messages.append({"role": "assistant", "content": response.content})
        elif response.tool_calls:
            fallback_msg = "Limite de chamadas encadeadas de ferramentas atingido. Tente reformular sua solicitação."
            self.messages.append({"role": "assistant", "content": fallback_msg})
            return AssistantResponse(content=fallback_msg)

        return response

    async def close(self):
        """Fecha os recursos do provedor de LLM subjacente."""
        if self.provider:
            await self.provider.close()

    async def generate_lesson_content(self, topic: str, course_name: str, class_name: str) -> str:
        """Gera uma sugestão de plano de aula baseada no tópico, disciplina e turma."""
        if not self.provider:
            await self._ensure_provider_async()
            if not self.provider:
                return "Erro: Provedor de IA não configurado."

        system_prompt = (
            "Você é um especialista pedagógico. Sua tarefa é criar um plano de aula detalhado e estruturado. "
            "A saída deve ser texto formatado (não Markdown complexo, mas com quebras de linha e seções claras) "
            "adequado para ser colado em um campo de texto simples.\n"
            "Estrutura Obrigatória:\n"
            "1. Objetivos de Aprendizagem\n"
            "2. Conteúdo/Tópicos a Abordar\n"
            "3. Sugestão de Atividades Práticas\n"
            "4. Avaliação/Verificação de Aprendizado\n\n"
            "Seja direto e prático. Adapte a linguagem à disciplina e nível escolar (inferido pelo nome da turma)."
        )

        user_prompt = f"Crie um plano de aula para a disciplina '{course_name}' da turma '{class_name}' sobre o tema: '{topic}'."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await self.provider.get_chat_response(messages)
        return response.content if response.content else "Não foi possível gerar o conteúdo."
