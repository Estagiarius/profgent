# Guia para Agentes de IA

Este documento serve como um guia essencial para agentes de IA que trabalham neste repositório. Ele contém informações críticas sobre a arquitetura do projeto, convenções, comandos e armadilhas comuns. **A leitura e compreensão deste guia são obrigatórias antes de iniciar qualquer tarefa.**

## 1. Visão Geral do Projeto

Este é um **Aplicativo de Gestão Acadêmica** construído em Python, com uma interface gráfica desenvolvida usando a biblioteca **CustomTkinter**. O principal objetivo do projeto é fornecer ferramentas para gerenciar alunos, cursos, turmas e notas.

Um recurso central é a integração com um **Assistente de IA**, projetado para auxiliar os usuários a interagir com os dados do sistema por meio de linguagem natural. O agente de IA possui um conjunto de ferramentas para ler e escrever no banco de dados de forma segura.

## 2. Arquitetura do Software

O projeto segue uma arquitetura robusta e modular para garantir a separação de responsabilidades e a manutenibilidade.

- **Padrão MVC (Model-View-Controller) com Camada de Serviço:**
  - **Models (`app/models/`):** Representam as tabelas do banco de dados usando o ORM SQLAlchemy. Contêm a estrutura dos dados.
  - **Views (`app/ui/views/`):** Compõem a interface do usuário (UI) com CustomTkinter. São responsáveis pela apresentação dos dados.
  - **Services (`app/services/`):** Contêm a lógica de negócios. O `DataService` lida com todas as interações do banco de dados, e o `AssistantService` gerencia a lógica do agente de IA. As Views nunca acessam o banco de dados diretamente; elas sempre passam pelo `DataService`.

- **Injeção de Dependência:** As instâncias dos serviços (`DataService`, `AssistantService`) são criadas uma única vez em `main.py` e injetadas no construtor da `MainApp` e, subsequentemente, nas Views que precisam delas. Isso garante que componentes críticos sejam compartilhados e gerenciados de forma centralizada.

- **Banco de Dados:**
  - **ORM:** Utilizamos **SQLAlchemy** para mapear objetos Python para tabelas de um banco de dados **SQLite**.
  - **Sessão por Operação:** Para garantir a integridade dos dados e evitar problemas de concorrência, cada operação no banco de dados é executada em sua própria sessão transacional, gerenciada pelo `get_db_session` em `app/data/database.py`.

## 3. Ambiente de Desenvolvimento

O projeto utiliza **Poetry** para gerenciamento de dependências.

- **Instalação:** Para instalar todas as dependências necessárias, execute o seguinte comando na raiz do projeto:
  ```bash
  poetry install
  ```
- **Erro Comum:** Se o comando acima falhar com um erro `No file/folder found for package`, significa que o Poetry está tentando instalar o projeto atual como um pacote. Use o seguinte comando para instalar apenas as dependências:
  ```bash
  poetry install --no-root
  ```

## 4. Execução de Testes

Utilizamos **pytest** para os testes automatizados. Os testes são configurados para usar um banco de dados SQLite em memória, garantindo que sejam rápidos e não afetem o banco de dados de desenvolvimento.

- **Comando para Executar Testes:**
  ```bash
  poetry run pytest
  ```
- **⚠️ AVISO IMPORTANTE: Falha de Teste Conhecida**
  Existe uma falha de teste pré-existente e conhecida em `test_update_student`. Isso ocorre devido a uma sobrecarga de método não intencional em `DataService`. **Não tente consertar este teste**, a menos que a tarefa solicite explicitamente. Concentre-se em garantir que seus próprios testes e alterações passem.

## 5. Migrações de Banco de Dados

Utilizamos **Alembic** para gerenciar as alterações no esquema do banco de dados.

- **Criar uma Nova Migração:** Após modificar um modelo do SQLAlchemy, gere um script de migração com o comando:
  ```bash
  poetry run alembic revision --autogenerate -m "Descrição da alteração"
  ```
- **Aplicar Migrações:** Para aplicar as migrações mais recentes ao banco de dados, execute:
  ```bash
  poetry run alembic upgrade head
  ```
- **Importante:** Para que o Alembic detecte as alterações nos modelos, todos os modelos devem ser importados em `alembic/env.py`.

## 6. ❗ AVISO CRÍTICO: Ambiente Headless

O ambiente de execução é **headless**, o que significa que não há servidor de exibição ou monitor. Qualquer tentativa de executar a aplicação CustomTkinter (`poetry run python main.py`) resultará em um erro (`_tkinter.TclError`).

**Você não pode verificar visualmente as alterações na interface do usuário.** A verificação deve ser feita por meio de testes automatizados ou solicitando a confirmação do usuário.

## 7. Ferramentas do Agente de IA

O assistente de IA usa um framework de ferramentas para interagir com o sistema.

- **Para criar uma nova ferramenta:**
  1.  Defina uma função Python com uma docstring clara no diretório `app/tools/`.
  2.  Decore a função com o decorador `@tool`.
  3.  Registre a nova ferramenta no método `_register_tools` da classe `AssistantService` (`app/services/assistant_service.py`), importando-a e chamando `self.tool_registry.register()`.

## 8. Convenções e Pontos de Atenção

- **Nomes de Atributos dos Models:** Use os nomes de atributos corretos ao interagir com os modelos de dados para evitar `TypeError`.
  - `Student`: `first_name`, `last_name`
  - `Course`: `course_name`
  - `Class`: `name`
  - `Grade`: `score`
- **Arquivo `class_.py`:** O modelo para `Class` está em `app/models/class_.py` (com um sublinhado) para evitar conflito com a palavra-chave `class` do Python.
- **Commits Atômicos:** Cada commit deve ser focado em uma única preocupação. Não misture correções de bugs, refatorações e novas funcionalidades em um único commit.
- **Eager Loading (Carregamento Ansioso):** Para evitar `DetachedInstanceError` do SQLAlchemy, sempre carregue relacionamentos necessários de forma ansiosa (eager loading) nas consultas do `DataService` usando `options(joinedload(Model.relacionamento))`.
