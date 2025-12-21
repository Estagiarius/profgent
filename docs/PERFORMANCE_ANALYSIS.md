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

# Análise de Performance e Fluidez do Sistema

Este documento detalha os pontos fracos identificados na arquitetura do sistema que impactam a fluidez e a performance, conforme solicitado. A análise baseia-se na inspeção do código-fonte e nos dados de uso fornecidos (600+ alunos, 50 alunos/turma, Hardware Comum).

## 1. Bloqueio da Thread Principal (Synchronous I/O)

O ponto mais crítico é a execução de operações de Banco de Dados diretamente na thread principal da interface gráfica (UI Thread).

*   **Problema:** O método `ClassDetailView.on_show` e os métodos `populate_*` (ex: `populate_grade_grid`) realizam chamadas síncronas ao `DataService` (ex: `get_enrollments_for_class`, `get_assessments_for_subject`).
*   **Impacto:** Em um banco SQLite local, isso pode levar de 50ms a 500ms dependendo da carga e fragmentação do arquivo. Durante esse tempo, a interface congela completamente ("Travamento"), pois o loop de eventos do Tkinter é interrompido.
*   **Localização:** `app/ui/views/class_detail_view.py`.

## 2. Custo de Instanciação de Widgets (Rendering Overhead)

O framework CustomTkinter/Tkinter possui um custo computacional significativo para criar e desenhar novos widgets.

*   **Problema:** No "Quadro de Notas", o sistema cria um widget `CTkEntry` para **cada célula** da tabela.
    *   Cálculo: 50 alunos * 6 avaliações = 300 widgets complexos criados de uma só vez.
    *   Além disso, 50 `CTkButton` são criados na aba de Alunos para o status.
*   **Impacto:** O Python precisa instanciar centenas de objetos e o Tkinter precisa alocar recursos gráficos para cada um. Isso causa o "Lag Visual" e demora na renderização inicial da aba.
*   **Localização:** Loops dentro de `populate_grade_grid` e `populate_student_list`.

## 3. Cálculos de Negócio na Camada de Apresentação

*   **Problema:** O cálculo de médias (`calculate_weighted_average`) é realizado dentro do loop de renderização da UI.
*   **Impacto:** Para cada aluno, o sistema pausa a renderização para fazer aritmética. Embora rápido individualmente, multiplicado por 50 alunos, soma-se ao tempo de congelamento da interface.
*   **Solução:** Mover esse cálculo para o Backend (`DataService`), retornando os dados já processados.

## 4. Carregamento Sequencial (Waterfall Loading)

*   **Problema:** Ao abrir uma turma, o sistema carrega os dados um por um:
    1.  Busca Turma -> Espera
    2.  Busca Alunos -> Espera
    3.  Busca Disciplinas -> Espera
*   **Impacto:** O tempo total de espera é a soma de todas as operações.
*   **Solução:** Carregamento Assíncrono e Paralelo (quando possível) ou em Batch.

## Plano de Ação (Implementação Imediata)

Para resolver esses problemas, as seguintes otimizações serão implementadas:

1.  **Carregamento Assíncrono:** Refatorar `ClassDetailView` para carregar dados em background (`asyncio`), exibindo um indicador de "Carregando..." para manter a interface responsiva.
2.  **Otimização de Backend:** Criar métodos otimizados no `GradeService` para buscar e calcular todos os dados do grid de notas em uma única transação eficiente.
3.  **Redução de Overhead:** Minimizar a lógica de negócios na UI.
