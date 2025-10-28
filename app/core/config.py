import json
from pathlib import Path

# Define the path for the configuration file
CONFIG_DIR = Path.home() / ".academic_management_app"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Ensure the configuration directory exists
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def save_config(settings: dict):
    """Saves the application settings to the config file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except IOError as e:
        print(f"Error saving configuration: {e}")

def load_config() -> dict:
    """Loads the application settings from the config file."""
    if not CONFIG_FILE.exists():
        return {}  # Return empty dict if no config file

    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading configuration: {e}")
        return {}

def save_setting(key: str, value: any):
    """Saves a single setting."""
    settings = load_config()
    settings[key] = value
    save_config(settings)

def load_setting(key: str, default: any = None) -> any:
    """Loads a single setting."""
    settings = load_config()
    return settings.get(key, default)
