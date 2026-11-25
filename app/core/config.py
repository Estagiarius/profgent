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
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

# Define o caminho para o diretório e arquivo de configuração
CONFIG_DIR = Path.home() / ".academic_management_app"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Garante que o diretório de configuração exista
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def save_config(settings: dict):
    """Salva as configurações da aplicação no arquivo JSON de forma atômica."""
    tmp_path = None
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=CONFIG_DIR,
            prefix=".config_",
            suffix=".tmp",
            delete=False,
        ) as tmp_file:
            json.dump(settings, tmp_file, indent=4, ensure_ascii=False)
            tmp_path = tmp_file.name
        os.replace(tmp_path, CONFIG_FILE)
    except OSError as e:
        logging.error(f"Erro ao salvar configuração: {e}")
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def load_config() -> dict:
    """Carrega as configurações da aplicação a partir do arquivo JSON."""
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logging.error(f"Erro ao carregar configuração: {e}")
        return {}


def save_setting(key: str, value: Any):
    """Salva uma configuração individual."""
    settings = load_config()
    settings[key] = value
    save_config(settings)


def load_setting(key: str, default: Any = None) -> Any:
    """Carrega uma configuração individual."""
    settings = load_config()
    return settings.get(key, default)
