# Importa a biblioteca 'keyring', que fornece uma maneira de acessar
# o armazenamento seguro de credenciais do sistema operacional (como o Keychain no macOS,
# Credential Vault no Windows, ou Secret Service no Linux).
import keyring

# O nome do serviço sob o qual as credenciais serão armazenadas.
# Em uma aplicação real, isso deve ser um identificador único para o seu aplicativo.
APP_NAME = "academic-management-app"

# Define uma função para salvar uma chave de API.
def save_api_key(service_name: str, api_key: str):
    """
    Salva uma chave de API para um determinado serviço no keychain seguro do sistema.

    Args:
        service_name: O nome do serviço (ex: 'OpenAI'). Funciona como o "username" no par serviço/username.
        api_key: A chave de API a ser armazenada. Funciona como a "password".
    """
    try:
        # Usa a função `set_password` do keyring.
        # APP_NAME é o nome do serviço geral (o "aplicativo").
        # service_name é o "nome de usuário" ou identificador específico da chave.
        # api_key é a "senha" a ser armazenada.
        keyring.set_password(APP_NAME, service_name, api_key)
        print(f"Chave de API para {service_name} salva com sucesso.")
    except Exception as e:
        # Captura possíveis erros com o backend do keyring (ex: se nenhum backend estiver configurado).
        print(f"Erro ao salvar a chave de API para {service_name}: {e}")

# Define uma função para obter uma chave de API.
def get_api_key(service_name: str) -> str | None:
    """
    Recupera uma chave de API para um determinado serviço do keychain seguro do sistema.

    Args:
        service_name: O nome do serviço (ex: 'OpenAI').

    Returns:
        A chave de API como uma string, ou None se não for encontrada ou se ocorrer um erro.
    """
    try:
        # Usa a função `get_password` para recuperar a chave armazenada.
        return keyring.get_password(APP_NAME, service_name)
    except Exception as e:
        # Captura possíveis erros com o backend do keyring.
        print(f"Erro ao recuperar a chave de API para {service_name}: {e}")
        return None
