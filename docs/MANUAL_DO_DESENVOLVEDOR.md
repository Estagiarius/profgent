# Manual do Desenvolvedor

## 1. Visão Geral

Bem-vindo ao Projeto de Gerenciamento Acadêmico!

Esta aplicação desktop foi desenvolvida em Python com a biblioteca CustomTkinter para a interface gráfica. Ela visa facilitar a administração de alunos, cursos, turmas e notas, além de contar com um Assistente de IA integrado para auxiliar os usuários a realizar tarefas através de linguagem natural.

Este documento serve como um guia para novos desenvolvedores, fornecendo uma visão completa da arquitetura do software, das ferramentas utilizadas e dos procedimentos necessários para configurar o ambiente de desenvolvimento, rodar a aplicação e contribuir com o projeto.

## 2. Estrutura do Projeto

O projeto está organizado da seguinte forma:

```
.
├── alembic/              # Contém os scripts de migração do banco de dados (Alembic).
├── app/                  # Onde fica todo o código-fonte da aplicação.
│   ├── data/             # Módulos relacionados ao acesso a dados (Modelos e Database).
│   ├── services/         # Lógica de negócio e serviços (DataService, AssistantService).
│   ├── ui/               # Componentes da interface do usuário (Views, MainApp).
│   └── agent/            # Lógica do assistente de IA, incluindo ferramentas.
├── docs/                 # Documentação do projeto.
├── tests/                # Testes automatizados (pytest).
├── .gitignore            # Arquivos e pastas ignorados pelo Git.
├── alembic.ini           # Arquivo de configuração do Alembic.
├── main.py               # Ponto de entrada da aplicação.
├── poetry.lock           # Dependências exatas do projeto.
├── pyproject.toml        # Arquivo de configuração do projeto (Poetry).
└── README.md             # Informações gerais sobre o projeto.
```

## 3. Arquitetura

A aplicação segue uma arquitetura inspirada no padrão **Model-View-Controller (MVC)**, com uma camada de **Serviço** adicional para encapsular a lógica de negócio.

-   **Models (`app/data/models`)**: Representam as entidades do banco de dados (ex: `Student`, `Course`, `Class`). São definidos usando SQLAlchemy ORM.
-   **Views (`app/ui/views`)**: São os componentes da interface gráfica, responsáveis pela apresentação dos dados ao usuário. Utilizam a biblioteca CustomTkinter.
-   **Controllers (implícito na View/MainApp)**: A lógica que conecta as Views aos Models e Services está contida dentro das próprias classes de View e na classe principal `MainApp`, que gerencia a navegação e o estado da aplicação.
-   **Services (`app/services`)**: Camada que centraliza a lógica de negócio. Por exemplo, `DataService` é responsável por todas as interações com o banco de dados, e `AssistantService` orquestra o funcionamento do assistente de IA.

## 4. Banco de Dados

-   **Tecnologia:** Utilizamos **SQLite** como banco de dados, o que simplifica a configuração, pois o banco é um único arquivo.
-   **ORM:** O acesso aos dados é feito exclusivamente através do **SQLAlchemy ORM**. Isso garante segurança e abstrai as queries SQL.
-   **Migrations:** As alterações no esquema do banco de dados (criação de tabelas, adição de colunas, etc.) são gerenciadas pelo **Alembic**. Para criar uma nova migração, use o comando:
    ```bash
    poetry run alembic revision --autogenerate -m "Descrição da alteração"
    ```
    Para aplicar as migrações e atualizar o banco de dados para a versão mais recente, use:
    ```bash
    poetry run alembic upgrade head
    ```
    A aplicação também tenta executar as migrações automaticamente ao ser iniciada.

## 5. Gerenciamento de Dependências

O projeto utiliza **Poetry** para gerenciar as dependências e o ambiente virtual.

Para instalar todas as dependências necessárias, execute o seguinte comando na raiz do projeto:

```bash
poetry install
```

Este comando irá ler o arquivo `pyproject.toml`, criar um ambiente virtual (se não existir) e instalar as bibliotecas listadas no `poetry.lock`.

## 6. Como Executar a Aplicação

Após instalar as dependências, você pode executar a aplicação principal com o comando:

```bash
poetry run python main.py
```

**Atenção:** A aplicação possui uma interface gráfica. Em um ambiente sem display (headless), a execução falhará.

## 7. Como Executar os Testes

Os testes automatizados são escritos com o framework **pytest**. Para rodar a suíte de testes completa, use o comando:

```bash
poetry run pytest
```

Os testes são configurados para rodar com um banco de dados SQLite em memória, garantindo que sejam rápidos e não afetem o banco de dados de desenvolvimento.

## 8. Assistente de IA

O assistente de IA é um componente central da aplicação. Ele permite que o usuário interaja com o sistema usando linguagem natural para consultar informações e executar ações.

-   **Funcionamento:** O assistente utiliza um provedor de LLM (Large Language Model) que suporta "function calling" (ex: OpenAI).
-   **Ferramentas (`app/agent/tools`)**: As ações que o assistente pode executar são definidas como "ferramentas". São funções Python decoradas com `@tool`. O decorador gera automaticamente um esquema JSON que descreve a função para a LLM.
-   **Fluxo de Execução:**
    1.  O usuário envia uma mensagem.
    2.  A `AssistantService` envia a mensagem (junto com o histórico da conversa e a lista de ferramentas disponíveis) para a LLM.
    3.  A LLM decide se deve responder diretamente ou usar uma ferramenta. Se optar por uma ferramenta, ela retorna o nome da ferramenta e os argumentos.
    4.  A `AssistantService` executa a ferramenta de forma segura.
    5.  O resultado da ferramenta é enviado de volta para a LLM.
    6.  A LLM gera uma resposta final em linguagem natural para o usuário, resumindo o que foi feito.

Este fluxo garante que o assistente seja seguro (executa apenas código predefinido) e preciso (baseia suas respostas nos dados retornados pelas ferramentas).
