# Guia para Agentes de IA

Este documento fornece diretrizes e informações essenciais para agentes de IA que trabalham neste repositório.

## Visão Geral do Projeto

Este é um Sistema de Gestão Acadêmica construído em Python com uma GUI CustomTkinter e um banco de dados SQLite gerenciado via SQLAlchemy. O projeto inclui um Assistente de IA que utiliza um framework de ferramentas para interagir com o banco de dados.

## Configuração do Ambiente

O projeto utiliza o Poetry para gerenciamento de dependências.

1.  **Instalar dependências:**
    ```bash
    poetry install --no-root --with dev
    ```
    *Use a flag `--with dev` para incluir dependências de teste como o pytest.*

## Execução e Testes

*   **Executar a aplicação:**
    ```bash
    poetry run python main.py
    ```

*   **Executar a suíte de testes:**
    ```bash
    poetry run pytest
    ```
    *Os testes são executados em um banco de dados SQLite em memória para garantir o isolamento.*

## Arquitetura do Banco de Dados

**AVISO IMPORTANTE:** O sistema de migração de banco de dados **Alembic foi removido** deste projeto.

*   **Inicialização do Banco de Dados:** O banco de dados (`app.db`) e todas as tabelas são criados automaticamente na primeira vez que a aplicação é executada. A lógica para isso está em `main.py` na função `initialize_database`, que usa `Base.metadata.create_all(engine)`.
*   **Não tente usar comandos do Alembic.** Eles não funcionarão e podem causar erros.

## Estrutura do Código

*   `app/`: Contém o código-fonte principal da aplicação.
    *   `data/`: Módulo de acesso a dados, incluindo a configuração do banco de dados.
    *   `models/`: Definições de modelos SQLAlchemy para todas as entidades do banco de dados.
    *   `services/`: Lógica de negócios (`DataService`, `AssistantService`).
    *   `tools/`: Ferramentas utilizadas pelo Assistente de IA para interagir com a aplicação.
    *   `ui/`: Componentes da interface do usuário (Views) construídos com CustomTkinter.
*   `tests/`: Contém todos os testes automatizados.
*   `main.py`: O ponto de entrada da aplicação.

## Framework de Ferramentas do Agente

O Assistente de IA opera utilizando um conjunto de "ferramentas" que lhe permitem interagir de forma segura com o banco de dados e outros serviços.

*   **Definição de Ferramentas:** As ferramentas são funções Python localizadas no diretório `app/tools/`. Elas são decoradas com `@tool` para expor sua assinatura à API do LLM.
*   **Registro de Ferramentas:** Todas as ferramentas devem ser registradas no `AssistantService` (`app/services/assistant_service.py`) para que o assistente possa utilizá-las.
*   **Segurança:** O agente deve usar exclusivamente as ferramentas fornecidas. Tentar escrever ou executar código arbitrário é estritamente proibido.
