# Guia de Compilação e Deploy do Profgent

Este documento detalha o processo de geração de executáveis e instaladores do **Profgent** para Windows, MacOS e Linux. O objetivo é permitir que desenvolvedores e administradores de sistema criem versões distribuíveis da aplicação.

## 1. Pré-requisitos Gerais

Antes de iniciar, certifique-se de que sua máquina de desenvolvimento possui:

1.  **Python 3.10 ou superior**: [Download Python](https://www.python.org/downloads/)
2.  **Poetry (Gerenciador de Dependências)**:
    ```bash
    pip install poetry
    ```
3.  **Git**: Para clonar o repositório.

### Configuração Inicial

Clone o repositório e instale as dependências do projeto (incluindo as de desenvolvimento, como o PyInstaller):

```bash
git clone <URL_DO_REPOSITORIO>
cd academic-management-app
poetry install --with dev
```

---

## 2. Gerando o Executável

O projeto inclui um script de automação (`scripts/build_executable.py`) que configura o **PyInstaller** com todas as dependências ocultas e assets necessários.

**Importante:** O PyInstaller não faz compilação cruzada (Cross-Compilation). Para gerar um executável de Windows, você deve rodar o script no Windows. Para Linux, no Linux, e assim por diante.

### Executando o Build

Na raiz do projeto, execute:

```bash
poetry run python scripts/build_executable.py
```

O script realizará as seguintes ações:
1.  Verificará se os assets (ícones, banco de dados base) existem.
2.  Limpará builds antigos.
3.  Gerará duas versões na pasta `dist/`:
    *   `dist/onedir/`: Uma pasta contendo o executável e todas as bibliotecas. **Inicia mais rápido.** Ideal para instaladores.
    *   `dist/onefile/`: Um arquivo único executável. **Mais fácil de compartilhar**, mas demora um pouco mais para abrir (descompacta temporariamente).

---

## 3. Instruções Específicas por Sistema Operacional

Abaixo, instruções detalhadas para criar instaladores e resolver problemas comuns em cada plataforma.

### Windows

#### Criando um Instalador (Setup.exe)
Utilizamos o **Inno Setup** para criar um instalador profissional.

1.  Baixe e instale o [Inno Setup](https://jrsoftware.org/isdl.php).
2.  Gere o executável (Passo 2 acima). Certifique-se de que a pasta `dist/onedir` foi criada.
3.  Vá até a pasta `scripts/installers/`.
4.  Abra o arquivo `windows_setup.iss` com o Inno Setup Compiler.
5.  Clique no botão **Compile** (Run).
6.  O instalador `Profgent_Setup.exe` será gerado em `dist/installers/`.

#### Avisos de Segurança (SmartScreen)
Como o executável não possui uma assinatura digital (que é paga), o Windows pode exibir o aviso **"O Windows protegeu o computador"**.
*   **Para usuários:** Clique em "Mais informações" -> "Executar assim mesmo".
*   **Solução Definitiva:** Para eliminar isso, é necessário adquirir um certificado de assinatura de código (Code Signing Certificate) e assinar o .exe.

---

### MacOS

#### Criando uma Imagem de Disco (.dmg)
O script de build gera um `.app` (Application Bundle). Para distribuir, empacotamos em um `.dmg`.

1.  Gere o executável (Passo 2 acima).
2.  Execute o script de criação de DMG:
    ```bash
    chmod +x scripts/installers/create_dmg.sh
    ./scripts/installers/create_dmg.sh
    ```
3.  O arquivo `.dmg` será gerado em `dist/installers/`.

#### Avisos de Segurança (Gatekeeper)
Ao tentar abrir o App baixado da internet (ou copiado de outro lugar), o MacOS pode dizer que o aplicativo está **"danificado"** ou **"não pode ser aberto porque o desenvolvedor não foi verificado"**.

*   **Solução Rápida:**
    1.  Mova o App para a pasta `Applications`.
    2.  Clique com o **botão direito** (Control+Click) no ícone do App.
    3.  Selecione **Abrir**.
    4.  Na janela de confirmação, clique em **Abrir** novamente.
*   **Comando de Terminal (Se necessário):**
    ```bash
    xattr -cr /Applications/Profgent.app
    ```

---

### Linux

No Linux, a distribuição mais comum para este tipo de app é o executável "OneFile" ou um pacote específico (DEB/RPM). Focaremos no executável direto.

#### Dependências do Sistema
Embora o PyInstaller empacote o Python, bibliotecas gráficas do sistema (Tcl/Tk) às vezes precisam estar instaladas na máquina do usuário se a distribuição for muito diferente da máquina de build.
*   **Ubuntu/Debian:** `sudo apt-get install python3-tk`
*   **Fedora:** `sudo dnf install python3-tkinter`

#### Criando Atalho no Menu
Para integrar o executável ao menu de aplicativos:

1.  Gere o executável (Passo 2 acima).
2.  Rode o script de configuração:
    ```bash
    chmod +x scripts/installers/linux_setup.sh
    ./scripts/installers/linux_setup.sh
    ```
3.  Um arquivo `Profgent.desktop` será criado. Para instalá-lo:
    ```bash
    mv Profgent.desktop ~/.local/share/applications/
    ```

---

## 4. Solução de Problemas Comuns

### Banco de Dados não Salva
O executável foi configurado para **não** salvar dados dentro da pasta de instalação (que muitas vezes é somente leitura, como em `Program Files`).
*   O banco de dados e logs são salvos na pasta do usuário:
    *   **Windows:** `C:\Users\SeuUsuario\.academic_management_app\`
    *   **Linux/Mac:** `/home/seuusuario/.academic_management_app/`

### Erro "Module not found" ao abrir
Se o programa fechar imediatamente:
1.  Tente executar via terminal (`./Profgent`) para ver o erro.
2.  Geralmente indica que uma biblioteca nova foi adicionada ao projeto mas não ao script de build.
3.  **Solução:** Adicione o nome da biblioteca à lista `hidden_imports` no arquivo `scripts/build_executable.py` e compile novamente.

### Ícones Faltando
Verifique se a pasta `app/ui/assets` contém os arquivos `.png` ou `.ico` necessários antes de compilar. O script avisa se eles não forem encontrados.
