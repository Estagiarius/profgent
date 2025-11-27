# Guia para Agentes de IA

Este documento fornece diretrizes e informações essenciais para agentes de IA que trabalham neste repositório. Para uma visão técnica aprofundada, consulte sempre o arquivo [ARCHITECTURE.md](ARCHITECTURE.md).

## Visão Geral do Projeto

Este é um Sistema de Gestão Acadêmica construído em Python com uma GUI CustomTkinter e um banco de dados SQLite gerenciado via SQLAlchemy. O projeto inclui um Assistente de IA que utiliza um framework de ferramentas ("Function Calling") para interagir com o sistema de forma segura.

## Configuração do Ambiente

O projeto utiliza o **Poetry** para gerenciamento de dependências.

1.  **Instalar dependências:**
    ```bash
    poetry install --no-root --with dev
    ```
    *A flag `--with dev` é obrigatória para incluir dependências de teste como `pytest` e `pytest-mock`.*

## Padrões de Desenvolvimento

Para manter a consistência e estabilidade do código, siga estas regras estritamente:

*   **Idioma:** Todo o código visível ao usuário (interface, logs, saídas de ferramentas) e comentários devem ser em **Português do Brasil**. Identificadores de código (variáveis, funções, classes) devem permanecer em **Inglês**.
*   **Interface Gráfica e Assincronismo:** A aplicação usa `CustomTkinter` (CTK) em um loop de eventos principal.
    *   **NUNCA** execute código bloqueante (ex: `time.sleep`, requisições HTTP síncronas, queries pesadas) diretamente na thread da UI. Isso congelará a aplicação.
    *   Utilize o utilitário `run_async_task` (`app/utils/async_utils.py`) para despachar corrotinas para background.
    *   A classe `MainApp` integra o loop `asyncio` através de um mecanismo de polling (`update_asyncio`).
*   **Injeção de Dependência:** As Views da UI não devem instanciar serviços diretamente. Elas devem receber instâncias de `DataService` e `AssistantService` via construtor (`__init__`).

## Execução e Testes

*   **Executar a aplicação:**
    ```bash
    poetry run python main.py
    ```

*   **Executar a suíte de testes:**
    ```bash
    poetry run pytest
    ```
    *   **Ambiente de Teste:** Os testes utilizam o `tests/conftest.py` para criar um banco de dados SQLite **em memória** (`db_session` fixture) para cada função de teste. Isso garante isolamento total e evita efeitos colaterais.
    *   **Fixtures Úteis:**
        *   `db_session`: Sessão SQLAlchemy isolada em memória.
        *   `data_service`: Instância de `DataService` configurada para usar a `db_session`.
        *   `assistant_service`: Instância com o provedor de IA "mockado" para evitar chamadas de rede.

## Arquitetura do Banco de Dados

**AVISO IMPORTANTE:** O sistema de migração de banco de dados **Alembic foi removido** deste projeto.

*   **Banco de Dados:** O arquivo é nomeado `academic_management.db`.
*   **Inicialização:** Todas as tabelas são criadas automaticamente na primeira vez que a aplicação é executada. A lógica reside em `main.py` -> `initialize_database`, utilizando `Base.metadata.create_all(engine)`.
*   **Não tente usar comandos do Alembic.** Eles não funcionarão.

## Estrutura do Código

*   `app/`: Código-fonte da aplicação.
    *   `core/`: Núcleo estrutural (Configuração `config.py`, Segurança, Framework de IA).
    *   `data/`: Configuração da conexão com o banco de dados (`database.py`).
    *   `models/`: Definições de modelos SQLAlchemy (Schema).
    *   `services/`: Lógica de negócios (`DataService`, `AssistantService`, `ReportService`).
    *   `tools/`: Implementações concretas das ferramentas do Assistente.
    *   `ui/`: Camada de apresentação (`views/` e `main_app.py`).
    *   `utils/`: Utilitários compartilhados (Async, Gráficos, Parsers).
*   `tests/`: Testes automatizados.
*   `main.py`: Ponto de entrada (Bootstrap).

## Framework de Ferramentas do Agente

O Assistente de IA interage com o sistema exclusivamente através de ferramentas registradas.

*   **Infraestrutura:** A lógica de registro e execução reside em `app/core/tools/` (`ToolRegistry`, `ToolExecutor`).
*   **Definição:** As ferramentas concretas estão em `app/tools/` e devem ser decoradas com `@tool`.
*   **Registro:** Novas ferramentas devem ser registradas manualmente no método `_register_tools` da classe `AssistantService` (`app/services/assistant_service.py`).
*   **Segurança:** O agente deve usar apenas as ferramentas fornecidas. A execução de código arbitrário é proibida.
