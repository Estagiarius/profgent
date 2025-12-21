# Manual do Usuário - Sistema de Gestão Acadêmica

Bem-vindo ao manual do usuário do Sistema de Gestão Acadêmica (Profgent). Este documento guiará você através de todas as funcionalidades da aplicação, desde o cadastro básico até o uso de ferramentas avançadas de Inteligência Artificial.

## Sumário
1. [Introdução](#introdução)
2. [Primeiros Passos](#primeiros-passos)
3. [Dashboard](#dashboard)
4. [Gestão de Turmas](#gestão-de-turmas)
5. [Área da Turma](#área-da-turma)
    - [Alunos e Matrículas](#alunos-e-matrículas)
    - [Avaliações](#avaliações)
    - [Aulas e Frequência](#aulas-e-frequência)
    - [Quadro de Notas](#quadro-de-notas)
    - [Incidentes](#incidentes)
    - [Relatórios e BNCC](#relatórios-e-bncc)
6. [Horário Escolar](#horário-escolar)
7. [Gestão de Dados](#gestão-de-dados)
8. [Configurações](#configurações)
9. [Assistente IA](#assistente-ia)

---

## Introdução

O **Profgent** é um sistema completo para gestão de escolas e turmas, desenvolvido para facilitar a vida de professores e gestores. Ele permite controlar matrículas, lançar notas e frequência, gerar relatórios automáticos, acompanhar a cobertura da BNCC e muito mais.

Uma das principais características do sistema é seu Assistente de IA, capaz de realizar tarefas complexas como importar dados de planilhas, gerar conteúdo de aulas e responder dúvidas sobre o desempenho dos alunos.

---

## Primeiros Passos

Ao iniciar a aplicação, você verá uma barra de navegação à esquerda com os principais módulos do sistema:
- **Dashboard:** Visão geral estatística da escola.
- **Minhas Turmas:** Onde você gerencia suas classes.
- **Horário:** Visualização e configuração da grade horária.
- **Assistente IA:** Chat para interagir com a inteligência artificial.
- **Gestão de Dados:** Cadastro de alunos e disciplinas (fora do contexto de turma).
- **Configurações:** Ajustes de tema e conexão com provedores de IA.

A navegação é simples: clique nos botões laterais para alternar entre as telas. O sistema salva suas alterações automaticamente no banco de dados local.

---

## Dashboard

O **Dashboard** é a tela inicial e oferece um resumo vital da escola. Ele é dividido em três abas principais:

### 1. Visão Geral
Aqui você encontra os principais indicadores:
- **Cards de Estatísticas:** Total de alunos ativos, turmas, disciplinas e incidentes registrados.
- **Índice Global de Aprovação:** Um gráfico de pizza mostrando a proporção de aprovados vs. reprovados (média >= 5.0).
- **Botão "Ver Alunos em Risco":** Abre uma lista detalhada dos alunos com média abaixo de 5.0 para ação rápida.

### 2. Destaques & Alertas
Focado em rankings:
- **Quadro de Honra:** Lista de alunos com média geral igual ou superior a 9.0.
- **Top Incidentes:** Ranking das turmas com maior número de ocorrências disciplinares.

### 3. Por Disciplina
Permite selecionar uma disciplina específica para visualizar um gráfico de distribuição de médias daquela matéria.

**Painel Lateral:** Exibe os **Aniversariantes do Dia** para que você possa parabenizar seus alunos.

---

## Gestão de Turmas

Acesse este módulo clicando em **"Minhas Turmas"**. Aqui você vê todas as turmas cadastradas em formato de cartões.

### Funcionalidades:
- **Adicionar Nova Turma:** Clique no botão no canto superior direito, digite o nome da turma e confirme.
- **Ver Detalhes:** Clique neste botão no cartão da turma para entrar na [Área da Turma](#área-da-turma) e gerenciar o dia a dia.
- **Editar:** Permite renomear a turma.
- **Copiar Turma (Botão Verde):** Cria uma cópia da turma, permitindo replicar a estrutura (disciplinas, avaliações) e até os alunos para um novo ano ou semestre.
- **Excluir (Botão Vermelho):** Remove a turma permanentemente. Exige confirmação digitando "DELETE".

---

## Área da Turma

Ao clicar em "Ver Detalhes" de uma turma, você entra no ambiente de trabalho principal. No topo, há um seletor de **Disciplina**. Quase todas as ações abaixo dependem da disciplina selecionada (exceto gestão de alunos e incidentes).

**Importante:** Se a turma for nova, clique em **"Adicionar Disciplina"** no topo para vincular as matérias (ex: Matemática, História) à turma.

### Alunos e Matrículas
Aba **"Alunos"**:
- **Lista de Alunos:** Exibe Nº de chamada, nome, % de frequência e data de nascimento.
- **Status (Ativo/Inativo):** Clique no botão de status para ativar ou desativar um aluno na turma.
- **Matricular Aluno:** Adiciona um aluno já existente no banco de dados à esta turma.
- **Importar Alunos (.csv):** Importa uma lista de alunos de uma planilha CSV. O sistema detecta nomes e datas de nascimento automaticamente.

### Avaliações
Aba **"Avaliações"**:
- Organizada por **Bimestres (1º a 4º)**.
- **Adicionar Nova Avaliação:** Crie provas, trabalhos ou atividades. Você define o nome, peso, bimestre e códigos BNCC associados.
- **Editar/Excluir:** Gerencie as avaliações existentes.

### Aulas e Frequência
Aba **"Aulas"**:
- **Lista de Aulas:** Histórico do que foi lecionado.
- **Adicionar Nova Aula:** Abre o editor de aulas.
    - **Editor:** Insira título, data, conteúdo e códigos BNCC.
    - **Gerar com IA:** Botão mágico que cria uma sugestão de plano de aula baseada no título e disciplina informados.
- **Chamada (Botão Verde):** Abre a lista de presença para a aula selecionada. Marque Presente, Falta ou Justificada.
- **Copiar para Outra Turma:** Permite replicar o conteúdo de aulas para outras turmas da mesma disciplina.

### Quadro de Notas
Aba **"Quadro de Notas"**:
- Uma planilha dinâmica para lançamento rápido de notas.
- Navegue entre as abas dos **Bimestres** para digitar as notas das avaliações criadas.
- O sistema calcula a **Média do Bimestre** automaticamente com base nos pesos.
- **Resultados Finais:** Exibe a média anual. Permite lançar uma "Nota Final" manual (ex: recuperação) que sobrescreve o cálculo automático.
- **Salvar:** Lembre-se sempre de clicar em "Salvar Alterações" após digitar as notas.

### Incidentes
Aba **"Incidentes"**:
- Registro de ocorrências disciplinares ou observações sobre alunos específicos da turma.

### Relatórios e BNCC
Abas **"BNCC"** e **"Relatórios"**:
- **BNCC:** Mostra o percentual de cobertura do currículo. Indica quais habilidades foram trabalhadas e quais estão pendentes.
    - *Aviso:* Se aparecer um alerta laranja, significa que você precisa cadastrar as habilidades esperadas no menu da disciplina (via Gestão de Dados ou botão "Editar Currículo Global").
- **Relatórios:**
    - **Exportar CSV:** Baixa todas as notas da turma.
    - **Boletim (TXT):** Gera um boletim individual para o aluno selecionado.
    - **Gráficos:** Visualiza desempenho individual ou da turma.

---

## Horário Escolar

Acesse via **"Horário"**.

1. **Aba Configuração:**
   - Defina a estrutura da sua escola. Adicione os horários das aulas (ex: 1ª Aula: 07:30 - 08:20) para cada dia da semana.
2. **Aba Visualização:**
   - Veja a grade semanal.
   - **Alocar:** Clique em um espaço vazio para definir qual turma e disciplina ocorre naquele horário.
   - **Registrar Aula:** Clique em um horário preenchido para abrir rapidamente o registro de conteúdo e chamada para aquela aula.

---

## Gestão de Dados

Acesse via **"Gestão de Dados"**. Esta tela é para manutenção cadastral fora das turmas.
- **Alunos:** Consulte, edite ou exclua alunos do sistema globalmente. Útil para corrigir nomes ou datas de nascimento erradas.
- **Disciplinas:** Gerencie o catálogo de disciplinas oferecidas pela escola (ex: criar "Robótica" para depois vincular às turmas).

---

## Configurações

Acesse via **"Configurações"**.
- **Tema:** Escolha entre diversos temas visuais (Black & Orange, Dracula, Ocean Breeze, etc.). Requer reinício da aplicação.
- **Provedor de IA:** Configure sua conexão com inteligências artificiais.
    - Suporte para **OpenAI**, **Maritaca** (brasileira), **OpenRouter** e **Ollama** (local).
    - Insira suas chaves de API aqui para habilitar o Assistente.

---

## Assistente IA

O **Assistente IA** é seu copiloto inteligente. Ele pode realizar ações por você através de comandos de chat natural.

**Exemplos de uso:**
- *"Crie uma nova turma chamada 9º Ano B"*
- *"Matricule o aluno João da Silva na turma 9º Ano B"*
- *"Gere um gráfico de desempenho da turma 101"*
- *"Quais alunos estão com risco de reprovação?"*
- *"Sugira uma aula sobre Revolução Francesa para História"*

O assistente tem acesso às ferramentas do sistema e pode buscar dados, criar registros e analisar informações para você.

---
*Manual atualizado para a versão mais recente do Profgent.*
