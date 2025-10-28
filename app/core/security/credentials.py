import keyring

# The service name under which the credentials will be stored.
# In a real application, this should be unique to your app.
APP_NAME = "academic-management-app"

def save_api_key(service_name: str, api_key: str):
    """
    Saves an API key for a given service in the system's secure keychain.

    Args:
        service_name: The name of the service (e.g., 'OpenAI').
        api_key: The API key to store.
    """
    try:
        keyring.set_password(APP_NAME, service_name, api_key)
        print(f"API key for {service_name} saved successfully.")
    except Exception as e:
        # Handle potential errors with the keyring backend
        print(f"Error saving API key for {service_name}: {e}")

def get_api_key(service_name: str) -> str | None:
    """
    Retrieves an API key for a given service from the system's secure keychain.

    Args:
        service_name: The name of the service (e.g., 'OpenAI').

    Returns:
        The API key as a string, or None if it's not found or an error occurs.
    """
    try:
        return keyring.get_password(APP_NAME, service_name)
    except Exception as e:
        # Handle potential errors with the keyring backend
        print(f"Error retrieving API key for {service_name}: {e}")
        return None
