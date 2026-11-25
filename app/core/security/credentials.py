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
import keyring
from app.core.config import CONFIG_DIR

# Nome do serviço sob o qual as credenciais são armazenadas no chaveiro do sistema.
APP_NAME = "academic-management-app"
SECRETS_FILE = CONFIG_DIR / "secrets.json"


def _write_secrets_dict(data: dict):
    """Escreve o dicionário de segredos de forma atômica com permissão restrita (0o600)."""
    tmp_path = None
    try:
        SECRETS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=SECRETS_FILE.parent,
            prefix=".secrets_",
            suffix=".tmp",
            delete=False,
        ) as tmp_file:
            json.dump(data, tmp_file, indent=4, ensure_ascii=False)
            tmp_path = tmp_file.name
        if os.name == "posix":
            os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, SECRETS_FILE)
        if os.name == "posix":
            os.chmod(SECRETS_FILE, 0o600)
    except OSError as e:
        logging.error(f"Erro ao gravar arquivo de segredos: {e}")
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def _load_secrets_dict() -> dict:
    """Carrega o dicionário de segredos do arquivo local de fallback."""
    if not SECRETS_FILE.exists():
        return {}
    try:
        with open(SECRETS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError) as e:
        logging.error(f"Erro ao ler arquivo de segredos: {e}")
        return {}


def _save_to_file(service_name: str, api_key: str):
    """Fallback: salva a chave de API em arquivo JSON local com permissão restrita."""
    data = _load_secrets_dict()
    data[service_name] = api_key
    _write_secrets_dict(data)
    logging.info(f"Chave de API para '{service_name}' salva em arquivo local (fallback).")


def _remove_from_file(service_name: str):
    """Remove uma chave específica do arquivo de fallback, caso exista."""
    if not SECRETS_FILE.exists():
        return
    data = _load_secrets_dict()
    if service_name in data:
        del data[service_name]
        if data:
            _write_secrets_dict(data)
        else:
            try:
                SECRETS_FILE.unlink()
            except OSError:
                pass


def _get_from_file(service_name: str) -> str | None:
    """Fallback: recupera a chave de API do arquivo JSON local."""
    data = _load_secrets_dict()
    return data.get(service_name)


def save_api_key(service_name: str, api_key: str):
    """
    Salva uma chave de API no chaveiro seguro do sistema operacional.
    Usa arquivo local restrito (0o600) como fallback caso o keyring não esteja disponível.
    """
    try:
        keyring.set_password(APP_NAME, service_name, api_key)
        # Limpa eventual cópia antiga no arquivo de fallback ao gravar com sucesso no keyring.
        _remove_from_file(service_name)
        logging.info(f"Chave de API para '{service_name}' salva com sucesso via keyring.")
    except Exception as e:
        logging.warning(f"Erro no keyring ({e}). Utilizando fallback em arquivo local.")
        _save_to_file(service_name, api_key)


def get_api_key(service_name: str) -> str | None:
    """
    Recupera uma chave de API do chaveiro seguro do sistema operacional.
    Consulta o arquivo local de fallback caso não encontrada ou em erro do keyring.
    """
    try:
        val = keyring.get_password(APP_NAME, service_name)
        if val is not None:
            return val
        return _get_from_file(service_name)
    except Exception as e:
        logging.warning(f"Erro no keyring ({e}). Consultando fallback em arquivo local.")
        return _get_from_file(service_name)


def delete_api_key(service_name: str):
    """Remove a chave de API do chaveiro do sistema e do arquivo local de fallback."""
    try:
        keyring.delete_password(APP_NAME, service_name)
    except Exception as e:
        logging.debug(f"Chave '{service_name}' não removida do keyring: {e}")
    _remove_from_file(service_name)
