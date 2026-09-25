import os
import json
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "volume": 70,
    "always_on_top": True,
    "enable_ai": False,
    "start_on_boot": False,
    "cat_scale": 1.0
}

def get_config_path() -> str:
    # Use config.json in the user's home directory or current app directory
    # User's home dir is safer for cross-platform packaged apps.
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, ".nekodesk")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.json")

def load_config() -> Dict[str, Any]:
    path = get_config_path()
    if not os.path.exists(path):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure all default keys are present
            config = DEFAULT_CONFIG.copy()
            for k, v in DEFAULT_CONFIG.items():
                if k in data:
                    config[k] = data[k]
            return config
    except Exception as e:
        print(f"Error loading config, using defaults: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    path = get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

class Settings:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance.data = load_config()
        return cls._instance
    
    def get(self, key: str) -> Any:
        return self.data.get(key, DEFAULT_CONFIG.get(key))
    
    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        save_config(self.data)
