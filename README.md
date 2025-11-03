# Academic Management System with AI Assistant

## Sobre o Projeto

Este projeto é um sistema de gerenciamento acadêmico robusto, desenvolvido em Python, que visa simplificar a administração de estudantes, cursos, turmas e notas. A aplicação possui uma interface gráfica intuitiva construída com CustomTkinter e um banco de dados relacional gerenciado pelo SQLAlchemy.

O grande diferencial deste sistema é a integração de um **Assistente de IA**, que permite aos usuários interagir com o sistema através de linguagem natural para realizar consultas e executar operações de gerenciamento, otimizando o fluxo de trabalho e tornando a gestão acadêmica mais eficiente.

## Funcionalidades Principais

*   **Gerenciamento Completo (CRUD):** Interface para criar, visualizar, atualizar e deletar registros de estudantes, cursos, turmas, matrículas e notas.
*   **Assistente de IA Integrado:** Utilize comandos em linguagem natural para interagir com o banco de dados, como "liste todos os alunos da turma de Cálculo" ou "adicione o curso de História". O assistente utiliza um framework de ferramentas seguro para executar operações de leitura e escrita.
*   **Interface Gráfica Intuitiva:** Uma aplicação desktop desenvolvida com a biblioteca CustomTkinter, garantindo uma experiência de usuário moderna e agradável.
*   **Visualização de Dados:** Geração de gráficos e visualizações para análise de dados acadêmicos, como a distribuição de notas por curso.
*   **Importação de Dados:** Funcionalidade para importar listas de alunos para uma turma a partir de arquivos `.csv`.
*   **Banco de Dados Persistente:** Utiliza SQLite com o ORM SQLAlchemy para um acesso seguro e eficiente aos dados, com migrações de schema gerenciadas pelo Alembic.

## Tecnologias Utilizadas

A aplicação é construída com um conjunto de tecnologias modernas e eficientes do ecossistema Python:

*   **Linguagem:** Python 3.10+
*   **Interface Gráfica (GUI):** CustomTkinter
*   **Banco de Dados:** SQLite
*   **ORM (Object-Relational Mapping):** SQLAlchemy
*   **Migrações de Banco de Dados:** Alembic
*   **Gerenciador de Dependências:** Poetry
*   **Framework de Testes:** Pytest
*   **Inteligência Artificial:** Integração com a API da OpenAI

## Como Instalar e Rodar

Siga os passos abaixo para configurar o ambiente de desenvolvimento e executar a aplicação.

### Pré-requisitos

*   Python (versão >=3.10, <3.15)
*   Poetry instalado

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd academic-management-app
    ```

2.  **Instale as dependências:**
    Utilize o Poetry para instalar todas as dependências do projeto.
    ```bash
    poetry install
    ```

### Execução

Após a instalação das dependências, execute o comando abaixo para iniciar a aplicação:

```bash
poetry run python main.py
```

Ao ser iniciada, a aplicação executará automaticamente as migrações do banco de dados (Alembic) para garantir que o schema esteja atualizado.

## Como Executar os Testes

O projeto utiliza Pytest para os testes unitários e de integração. Para executar a suíte de testes, utilize o seguinte comando:

```bash
poetry run pytest
```

Os testes são configurados para rodar em um banco de dados SQLite em memória para garantir isolamento e velocidade.
