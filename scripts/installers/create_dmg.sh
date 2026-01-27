#!/bin/bash
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

# Script para criar um instalador .dmg para MacOS
# Requer 'hdiutil' (padrão no MacOS)

APP_NAME="Profgent"
VERSION="1.0"
DIST_DIR="../../dist/onedir/${APP_NAME}.app" # O PyInstaller gera .app no mac em onedir
DMG_NAME="${APP_NAME}_${VERSION}_Installer.dmg"
OUTPUT_DIR="../../dist/installers"

echo "=== Criação de Instalador DMG para $APP_NAME ==="

# 1. Verifica ambiente
if [ "$(uname)" != "Darwin" ]; then
    echo "ERRO: Este script deve ser executado no MacOS."
    exit 1
fi

# 2. Verifica se o bundle .app existe
if [ ! -d "$DIST_DIR" ]; then
    echo "ERRO: Bundle .app não encontrado em $DIST_DIR"
    echo "Certifique-se de ter rodado 'scripts/build_executable.py' primeiro."
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo ">>> Criando imagem de disco temporária..."
hdiutil create -size 500m -fs HFS+ -volname "$APP_NAME" -ov -srcfolder "$DIST_DIR" "temp.dmg"

if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao criar imagem temporária."
    exit 1
fi

echo ">>> Convertendo para formato comprimido (UDZO)..."
hdiutil convert "temp.dmg" -format UDZO -o "$OUTPUT_DIR/$DMG_NAME"

rm "temp.dmg"

echo " "
echo " [OK] Instalador criado em: $OUTPUT_DIR/$DMG_NAME"
