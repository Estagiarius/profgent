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

APP_NAME="Profgent"
# Detecta o caminho absoluto atual para garantir que o .desktop funcione
BASE_DIR="$(pwd)"
EXEC_PATH="$BASE_DIR/dist/onefile/$APP_NAME"
ICON_PATH="$BASE_DIR/app/ui/assets/icon.png"

echo "=== Configuração de Atalho Linux para $APP_NAME ==="

# 1. Verifica se o executável existe
if [ ! -f "$EXEC_PATH" ]; then
    echo "ERRO: Executável não encontrado em: $EXEC_PATH"
    echo "Por favor, rode o script de build primeiro: 'poetry run python scripts/build_executable.py'"
    exit 1
fi

# 2. Verifica Ícone
if [ ! -f "$ICON_PATH" ]; then
    echo "AVISO: Ícone personalizado não encontrado ($ICON_PATH). Usando ícone genérico."
    ICON_PATH="utilities-terminal"
fi

# 3. Cria arquivo .desktop local
DESKTOP_FILE="Profgent.desktop"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=Profgent
Comment=Sistema de Gestão Acadêmica
Exec="$EXEC_PATH"
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Education;Office;
EOF

chmod +x "$DESKTOP_FILE"

echo " [OK] Arquivo '$DESKTOP_FILE' criado com sucesso!"
echo " "
echo "Para instalar no menu de aplicativos do seu usuário, execute:"
echo "  mv $DESKTOP_FILE ~/.local/share/applications/"
echo " "
echo "Ou apenas dê dois cliques no arquivo gerado para abrir."
