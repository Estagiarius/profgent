# Guia de Desenvolvimento e Arquitetura

Este documento fornece uma visão detalhada da arquitetura, design e fluxos de execução do Sistema de Gestão Acadêmica. Ele serve como referência para novos desenvolvedores entenderem como os componentes interagem e como o sistema é estruturado.

Para diretrizes específicas sobre desenvolvimento de agentes de IA, consulte [AGENTS.md](../AGENTS.md).
Para uma visão técnica de alto nível, consulte [ARCHITECTURE.md](../ARCHITECTURE.md).

---

## 1. Visão Geral (Diagrama de Casos de Uso)

O sistema atende a dois atores principais: o **Usuário** (Administrador/Professor) e o **Assistente de IA**. Abaixo estão as principais funcionalidades disponíveis, representadas através de um fluxograma de interação.

```mermaid
graph LR
    %% Definição dos Atores (Fora do Sistema)
    User["👤 Usuário (Professor/Admin)"]
    AI["🤖 Assistente de IA"]

    %% Limite do Sistema
    subgraph System ["Sistema de Gestão Acadêmica"]
        direction TB
        UC1(["Gerenciar Turmas"])
        UC2(["Gerenciar Alunos (Importar/Editar)"])
        UC3(["Gerenciar Notas e Avaliações"])
        UC4(["Gerenciar Aulas (Conteúdo)"])
        UC5(["Registrar Incidentes"])
        UC6(["Gerar Relatórios e Gráficos"])
        UC7(["Consultar Assistente Inteligente"])
        UC8(["Executar Ferramentas de Banco de Dados"])
        UC9(["Executar Ferramentas de Relatório"])
    end

    %% Conexões Usuário -> Casos de Uso
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7

    %% Conexões Casos de Uso -> IA
    UC7 -.-> AI
    AI --> UC8
    AI --> UC9
```

---

## 2. Modelo de Dados (Diagrama de Classes)

O banco de dados utiliza SQLite com SQLAlchemy ORM. O diagrama abaixo ilustra as entidades e seus relacionamentos.

**Nota:** Não existe uma entidade de "Presença" (Attendance). A gestão é feita através de `ClassEnrollment` (Status: Ativo/Inativo), `Lesson` (Registro de conteúdo de aula) e `Incident` (Ocorrências disciplinares).

```mermaid
classDiagram
    class Student {
        +int id
        +string first_name
        +string last_name
        +date birth_date
        +string enrollment_date
    }

    class Class {
        +int id
        +string name
        +enum calculation_method
    }

    class ClassEnrollment {
        +int id
        +int class_id
        +int student_id
        +int call_number
        +string status
        +string status_detail
    }

    class Course {
        +int id
        +string course_name
        +string course_code
    }

    class ClassSubject {
        +int id
        +int class_id
        +int course_id
    }

    class Assessment {
        +int id
        +int class_subject_id
        +string name
        +float weight
    }

    class Grade {
        +int id
        +int student_id
        +int assessment_id
        +float score
        +string date_recorded
    }

    class Lesson {
        +int id
        +int class_subject_id
        +date date
        +string title
        +string content
    }

    class Incident {
        +int id
        +int class_id
        +int student_id
        +date date
        +string description
    }

    Class "1" -- "*" ClassEnrollment : Tem
    Class "1" -- "*" Incident : Tem
    Class "1" -- "*" ClassSubject : Oferece
    Student "1" -- "*" ClassEnrollment : Matriculado em
    Student "1" -- "*" Grade : Recebe
    Student "1" -- "*" Incident : Envolvido em
    Course "1" -- "*" ClassSubject : Define
    ClassSubject "1" -- "*" Assessment : Tem
    ClassSubject "1" -- "*" Lesson : Tem
    Assessment "1" -- "*" Grade : Avaliado em
```

---

## 3. Arquitetura de Componentes

O sistema segue uma arquitetura em camadas, separando a Interface de Usuário (UI), Lógica de Negócios (Services) e Acesso a Dados (Data Layer).

```mermaid
graph TD
    subgraph UI_Layer [Camada de Apresentação UI]
        UI_Main[MainApp CustomTkinter]
        UI_Views[Views ClassDetail, Dashboard]
    end

    subgraph Service_Layer [Camada de Serviço Business Logic]
        Service_Data[DataService Singleton]
        Service_AI[AssistantService AI Orchestrator]
        Service_Report[ReportService Charts/Files]
    end

    subgraph Core_Layer [Núcleo e Ferramentas]
        Core_Tools[ToolRegistry]
        Core_Executor[ToolExecutor]
        Core_LLM[LLMProvider OpenAI/Ollama]
    end

    subgraph Data_Layer [Camada de Dados]
        DB[(SQLite Database)]
    end

    UI_Main --> UI_Views
    UI_Views --> Service_Data
    UI_Views --> Service_AI
    UI_Views --> Service_Report

    Service_Data --> DB
    Service_Report --> Service_Data

    Service_AI --> Core_LLM
    Service_AI --> Core_Executor
    Core_Executor --> Core_Tools
    Core_Executor --> Service_Data
    Core_Executor --> Service_Report
```

---

## 4. Fluxos de Execução (Diagramas de Sequência)

### 4.1. Inicialização do Sistema
Este diagrama detalha o processo de startup da aplicação, desde o `main.py` até o loop de eventos da UI.

```mermaid
sequenceDiagram
    participant Boot as Main (main.py)
    participant DB as Database (SQLAlchemy)
    participant AS as AssistantService
    participant UI as MainApp (UI)

    Boot->>DB: initialize_database()
    DB->>DB: inspect(engine)
    alt Tabelas não existem
        DB->>DB: Base.metadata.create_all()
    end

    Boot->>AS: AssistantService() (Singleton)
    AS->>AS: Carrega Configurações

    Boot->>UI: MainApp(data_service, assistant_service)
    UI->>UI: Configura Tema
    UI->>UI: Inicializa Views (Dashboard, Classes, etc.)

    Boot->>UI: app.mainloop()
    loop Event Loop
        UI->>UI: Processa Eventos Tkinter
        UI->>UI: update_asyncio() (Polling 20ms)
    end
```

### 4.2. Interação com o Assistente de IA
Este fluxo mostra como uma solicitação do usuário é processada pelo Assistente, convertida em chamadas de ferramentas e retornada como resposta natural.

```mermaid
sequenceDiagram
    actor User
    participant View as AssistantView
    participant Service as AssistantService
    participant LLM as LLMProvider
    participant Exec as ToolExecutor
    participant Data as DataService

    User->>View: "Cadastre o aluno João na turma 1A"
    View->>Service: get_response("Cadastre o aluno...")

    Service->>Service: _initialize_provider()
    Service->>LLM: get_chat_response(messages, tools)

    alt LLM decide usar ferramenta
        LLM-->>Service: Response(tool_calls=[add_new_student])
        Service->>Exec: execute_tool_call(add_new_student)

        Exec->>Data: add_student("João", ...)
        Data-->>Exec: {student_id: 123}
        Exec->>Data: add_student_to_class(123, "1A")
        Data-->>Exec: Success

        Exec-->>Service: "Aluno João cadastrado com ID 123 na turma 1A."

        Service->>LLM: get_chat_response(messages + tool_result)
        LLM-->>Service: Response(content="João foi cadastrado com sucesso!")
    else LLM responde direto
        LLM-->>Service: Response(content="Olá, como posso ajudar?")
    end

    Service-->>View: AssistantResponse
    View->>User: Exibe mensagem na tela
```
