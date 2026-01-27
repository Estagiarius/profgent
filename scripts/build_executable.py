#!/usr/bin/env python3
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

import PyInstaller.__main__
import sys
import os
import shutil
from pathlib import Path

# Determina o diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

def check_prerequisites():
    """Verifica se o ambiente está correto para o build."""
    print(">>> Verificando pré-requisitos...")

    # Verifica diretórios essenciais
    required_dirs = [
        BASE_DIR / "app" / "data",
        BASE_DIR / "app" / "ui" / "themes",
        BASE_DIR / "app" / "ui" / "assets"
    ]

    missing = []
    for d in required_dirs:
        if not d.exists():
            missing.append(str(d))

    if missing:
        print("ERRO: Os seguintes diretórios obrigatórios não foram encontrados:")
        for m in missing:
            print(f" - {m}")
        print("Certifique-se de estar rodando o script da raiz do projeto e que os assets existam.")
        sys.exit(1)

    print(">>> Pré-requisitos OK.")

def clean_dist():
    """Limpa as pastas de build anteriores para evitar conflitos."""
    print(">>> Limpando builds anteriores...")
    dirs_to_clean = [BASE_DIR / "build", BASE_DIR / "dist"]
    for d in dirs_to_clean:
        if d.exists():
            try:
                shutil.rmtree(d)
                print(f"    - Removido: {d}")
            except Exception as e:
                print(f"    - AVISO: Não foi possível limpar {d}: {e}")

def build_executable():
    """
    Script de automação para build do Profgent com PyInstaller.
    Gera executáveis para Linux, e configurações para Windows/Mac.
    """
    print(f"\n{'='*60}")
    print(f"INICIANDO PROCESSO DE BUILD DO PROFGENT")
    print(f"Diretório Base: {BASE_DIR}")
    print(f"{'='*60}\n")

    check_prerequisites()
    clean_dist()

    # 1. Definição de Caminhos e Assets
    data_path = BASE_DIR / "app" / "data"
    themes_path = BASE_DIR / "app" / "ui" / "themes"
    assets_path = BASE_DIR / "app" / "ui" / "assets"

    # Define o separador de caminho (Windows usa ';', Unix usa ':')
    sep = ';' if sys.platform.startswith('win') else ':'

    # Lista de arquivos/pastas para incluir (--add-data)
    # Formato: "origem:destino"
    add_data = [
        f"{data_path}{sep}app/data", # Copia a pasta inteira
        f"{themes_path}{sep}app/ui/themes", # Copia a pasta inteira
        f"{assets_path}{sep}app/ui/assets", # Copia a pasta inteira
    ]

    # Ícone
    icon_path = assets_path / "icon.ico"
    if not icon_path.exists():
        print("AVISO: 'icon.ico' não encontrado em app/ui/assets. O executável terá o ícone padrão.")
        icon_path = None

    # 2. Definição de Imports Ocultos (--hidden-import)
    hidden_imports = [
        "babel.numbers",
        "sqlalchemy.sql.default_comparator",
        "customtkinter",
        "PIL._tkinter_finder",
        # Serviços de Dados
        "app.services.data.student_service",
        "app.services.data.course_service",
        "app.services.data.enrollment_service",
        "app.services.data.grade_service",
        "app.services.data.lesson_service",
        "app.services.data.incident_service",
        "app.services.data.schedule_service",
        "app.services.data.dashboard_service",
        "app.services.data.seating_chart_service",
        "app.services.report_service",
    ]

    # 3. Argumentos Comuns
    args = [
        str(BASE_DIR / "main.py"), # Script principal
        "--name=Profgent",
        "--noconfirm",
        "--clean",
        "--windowed", # Não abre console (GUI mode)
    ]

    for data in add_data:
        args.append(f"--add-data={data}")

    for hidden in hidden_imports:
        args.append(f"--hidden-import={hidden}")

    if icon_path:
        args.append(f"--icon={str(icon_path)}")

    # 4. Modo OneDir (Diretório - Mais rápido para iniciar)
    print("\n>>> Gerando versão OneDir (Pasta - Ideal para Desenvolvimento/Debug)...")
    onedir_args = args.copy()
    onedir_args.append("--onedir")
    onedir_args.append("--distpath=dist/onedir")

    try:
        PyInstaller.__main__.run(onedir_args)
        print("    [OK] Versão OneDir gerada com sucesso.")
    except Exception as e:
        print(f"    [ERRO] Falha ao gerar OneDir: {e}")
        sys.exit(1)

    # 5. Modo OneFile (Arquivo Único - Melhor distribuição simples)
    print("\n>>> Gerando versão OneFile (Executável Único - Ideal para Distribuição)...")
    onefile_args = args.copy()
    onefile_args.append("--onefile")
    onefile_args.append("--distpath=dist/onefile")

    try:
        PyInstaller.__main__.run(onefile_args)
        print("    [OK] Versão OneFile gerada com sucesso.")
    except Exception as e:
        print(f"    [ERRO] Falha ao gerar OneFile: {e}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print("BUILD CONCLUÍDO!")
    print(f"Arquivos gerados em: {BASE_DIR / 'dist'}")
    print(" - OneDir:  dist/onedir/Profgent/ (Contém pasta com libs)")
    print(" - OneFile: dist/onefile/         (Executável único)")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    build_executable()
