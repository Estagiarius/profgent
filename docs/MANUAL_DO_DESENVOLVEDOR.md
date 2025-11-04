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

## 9. Tópicos Avançados

### 9.1. Fluxo de Dados na Interface do Usuário (UI)

A interação entre a interface do usuário e a camada de dados segue um padrão claro para garantir a consistência e a separação de responsabilidades. O `DataService` atua como a única fonte de verdade para todas as operações de banco de dados.

O ciclo de vida típico de dados em uma view é o seguinte:

1.  **Carregamento (Loading):**
    *   Quando uma view precisa ser exibida ou atualizada (por exemplo, a `ManagementView` ou a `GradeGridView`), ela chama um método apropriado do `DataService` para buscar os dados necessários. Ex: `data_service.get_all_students(active_only=True)`.
    *   Para evitar problemas de concorrência com o banco de dados e garantir a integridade dos dados, as consultas no `DataService` frequentemente usam *eager loading* (carregamento antecipado) de relacionamentos (ex: carregar um curso junto com suas turmas) através de `options(joinedload(...))` do SQLAlchemy.

2.  **Exibição (Displaying):**
    *   Os dados retornados pelo `DataService` (geralmente uma lista de objetos do modelo SQLAlchemy) são então usados para popular os widgets da UI (como tabelas, formulários ou menus).
    *   A view é responsável por iterar sobre esses objetos e apresentar seus atributos nos locais corretos. Por exemplo, a `GradeGridView` constrói uma grade onde as linhas representam alunos e as colunas representam avaliações.

3.  **Modificação e Persistência (Saving):**
    *   Quando o usuário realiza uma alteração (edita um campo, adiciona um novo registro), a view captura essa informação dos widgets.
    *   Ao acionar uma ação de salvamento (clicando em "Salvar", por exemplo), a view agrupa os dados modificados e chama o método correspondente no `DataService`. Ex: `data_service.update_student(...)` ou `data_service.update_grade(...)`.
    *   O `DataService` então executa a operação de escrita no banco de dados dentro de uma sessão transacional, garantindo que a alteração seja atômica.
    *   Após a conclusão da operação, a view geralmente se recarrega ou atualiza sua exibição para refletir o novo estado dos dados, reiniciando o ciclo.

Este padrão garante que toda a lógica de banco de dados permaneça isolada no `DataService`, enquanto as views se concentram exclusivamente na apresentação e na captura da entrada do usuário.

### 9.2. Criando Novas Ferramentas para o Assistente de IA

Adicionar novas capacidades ao Assistente de IA é um processo simples e seguro, centrado na criação de "ferramentas". Uma ferramenta é apenas uma função Python que é exposta de forma segura para a LLM.

Siga os passos abaixo para criar uma nova ferramenta:

1.  **Crie o Arquivo da Ferramenta:**
    *   Adicione um novo arquivo Python no diretório `app/agent/tools/`, por exemplo, `minha_nova_ferramenta.py`.

2.  **Defina a Função:**
    *   Dentro do novo arquivo, importe o decorador `@tool` e a instância do `data_service`.
    *   Escreva uma função Python normal. Use type hints para todos os argumentos e para o valor de retorno.
    *   **Crucial:** Escreva uma `docstring` clara e detalhada. A LLM usa a docstring para entender o que a ferramenta faz, quais são seus parâmetros e quando deve ser usada. Seja explícito.

3.  **Use o `DataService`:**
    *   Para qualquer interação com o banco de dados, utilize a instância importada do `data_service`. Isso garante que a lógica de acesso a dados permaneça centralizada e consistente.
    *   Sempre envolva as chamadas de serviço que modificam o banco de dados (criar, atualizar, deletar) em um bloco `try...except SQLAlchemyError` para capturar e relatar erros de forma graciosa.

4.  **Decore a Função:**
    *   Adicione o decorador `@tool` logo acima da definição da sua função. Ele irá registrar a função e gerar o esquema JSON necessário para a LLM.

5.  **Registre a Ferramenta:**
    *   Para que a aplicação reconheça a nova ferramenta, importe-a no arquivo `app/agent/tools/__init__.py`. Isso a adicionará automaticamente ao registro de ferramentas que é carregado pelo `AssistantService`.

**Exemplo de uma Ferramenta Simples:**

```python
# Em app/agent/tools/student_tools.py

from sqlalchemy.exc import SQLAlchemyError
from app.agent.tools.tool_decorator import tool
from app.services import data_service

@tool
def find_student_by_email(email: str) -> str:
    """
    Encontra um aluno pelo seu endereço de e-mail e retorna suas informações básicas.

    Args:
        email: O endereço de e-mail do aluno a ser procurado.

    Returns:
        Uma string com as informações do aluno ou uma mensagem de erro se o aluno não for encontrado.
    """
    try:
        student = data_service.get_student_by_email(email)
        if student:
            return f"Aluno encontrado: ID {student.id}, Nome: {student.name}, Status: {student.status}"
        else:
            return "Nenhum aluno encontrado com este e-mail."
    except SQLAlchemyError as e:
        return f"Ocorreu um erro no banco de dados: {e}"

```
Lembre-se de adicionar `from .student_tools import find_student_by_email` em `app/agent/tools/__init__.py`.

### 9.3. Aprofundando na Estratégia de Testes

Nossa suíte de testes é construída com `pytest` e projetada para ser robusta e isolada, garantindo que as alterações no código possam ser validadas de forma confiável sem afetar o ambiente de desenvolvimento.

**Configuração Central (`tests/conftest.py`):**

Este arquivo é o coração da nossa configuração de testes. Ele define *fixtures* do `pytest` que estão disponíveis para todos os arquivos de teste. As principais fixtures são:

-   `session`: Esta fixture configura um banco de dados **SQLite em memória** para cada sessão de teste. Isso significa que cada execução de `pytest` começa com um banco de dados limpo e todas as alterações são descartadas ao final. Isso garante total isolamento dos testes em relação ao banco de dados de desenvolvimento.
-   `mock_db_session`: Para testar a camada de serviço (`DataService`) de forma isolada, esta fixture usa `pytest-mock` para "enganar" o `DataService`, fazendo com que ele use a sessão do banco de dados em memória fornecida pela fixture `session` em vez de tentar se conectar ao banco de dados real.

**Escrevendo Testes para o `DataService`:**

Ao escrever testes para métodos do `DataService`, você deve sempre incluir a fixture `mock_db_session` como um argumento no seu teste. Isso garante que o serviço opere contra o banco de dados de teste.

**Exemplo de Teste:**

```python
# Em tests/test_data_service.py

from app.services.data_service import DataService
from app.data.models.student import Student

def test_create_student(mock_db_session):
    """
    Testa se o DataService consegue criar um novo aluno com sucesso.
    """
    # Arrange: prepara os dados de teste
    data_service = DataService()
    student_name = "João da Silva"
    student_email = "joao.silva@example.com"

    # Act: executa a ação a ser testada
    new_student = data_service.create_student(name=student_name, email=student_email)

    # Assert: verifica se o resultado está correto
    assert new_student is not None
    assert new_student.name == student_name

    # Verifica também se o aluno foi realmente salvo no banco de dados de teste
    retrieved_student = mock_db_session.query(Student).filter_by(email=student_email).one()
    assert retrieved_student.name == student_name
```

Este padrão de uso de fixtures e um banco de dados em memória torna nossos testes rápidos, confiáveis e fáceis de escrever.
