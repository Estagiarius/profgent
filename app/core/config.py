# Importa o módulo 'json' para trabalhar com arquivos JSON.
import json
# Importa a classe 'Path' do módulo 'pathlib' para lidar com caminhos de arquivo de forma orientada a objetos.
from pathlib import Path

# Define o caminho para o diretório de configuração.
# Ele será criado na pasta 'home' do usuário, dentro de um diretório oculto '.academic_management_app'.
CONFIG_DIR = Path.home() / ".academic_management_app"
# Define o caminho completo para o arquivo de configuração.
CONFIG_FILE = CONFIG_DIR / "config.json"

# Garante que o diretório de configuração exista.
# `parents=True` cria diretórios pais, se necessário. `exist_ok=True` não gera erro se o diretório já existir.
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Define a função para salvar o dicionário de configurações completo.
def save_config(settings: dict):
    """Salva as configurações da aplicação no arquivo de configuração."""
    try:
        # Abre o arquivo de configuração no modo de escrita ("w").
        with open(CONFIG_FILE, "w") as f:
            # Usa o `json.dump` para escrever o dicionário no arquivo, formatado com 4 espaços de indentação.
            json.dump(settings, f, indent=4)
    # Captura erros de entrada/saída (ex: permissão negada).
    except IOError as e:
        print(f"Erro ao salvar a configuração: {e}")

# Define a função para carregar o dicionário de configurações completo.
def load_config() -> dict:
    """Carrega as configurações da aplicação do arquivo de configuração."""
    # Se o arquivo de configuração não existir, retorna um dicionário vazio.
    if not CONFIG_FILE.exists():
        return {}

    try:
        # Abre o arquivo de configuração no modo de leitura ("r").
        with open(CONFIG_FILE, "r") as f:
            # Usa `json.load` para ler o arquivo e convertê-lo de JSON para um dicionário Python.
            return json.load(f)
    # Captura erros de I/O ou de decodificação de JSON (arquivo corrompido).
    except (IOError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar a configuração: {e}")
        # Retorna um dicionário vazio em caso de erro para evitar que a aplicação quebre.
        return {}

# Define uma função utilitária para salvar uma única configuração.
def save_setting(key: str, value: any):
    """Salva uma única configuração."""
    # Carrega todas as configurações atuais.
    settings = load_config()
    # Adiciona ou atualiza a chave específica com o novo valor.
    settings[key] = value
    # Salva o dicionário de configurações modificado de volta no arquivo.
    save_config(settings)

# Define uma função utilitária para carregar uma única configuração.
def load_setting(key: str, default: any = None) -> any:
    """Carrega uma única configuração."""
    # Carrega todas as configurações.
    settings = load_config()
    # Usa o método `.get()` do dicionário, que retorna o valor da chave se ela existir,
    # ou o valor `default` caso contrário.
    return settings.get(key, default)
