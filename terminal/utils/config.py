import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any

class Config:

    def __init__(self):
        self.config_file = Path.home() / ".dwarp_config.json"
        self._migrate_config()
        self.default_config = {
            "gemini_api_key": None,
            "model": "gemini-2.5-flash",
            "max_tokens": 4000,
            "temperature": 0.7,
            "safety_settings": {
                "harassment": "BLOCK_MEDIUM_AND_ABOVE",
                "hate_speech": "BLOCK_MEDIUM_AND_ABOVE", 
                "dangerous_content": "BLOCK_MEDIUM_AND_ABOVE",
                "sexual_content": "BLOCK_MEDIUM_AND_ABOVE"
            }
        }
    
    def _migrate_config(self):
        old_config = Path.home() / ".ai_terminal_config.json"
        if old_config.exists() and not self.config_file.exists():
            shutil.move(str(old_config), str(self.config_file))

    def load_config(self) -> Dict[str, Any]:
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    merged_config = self.default_config.copy()
                    merged_config.update(config)
                    return merged_config
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                return self.default_config.copy()

        return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            os.chmod(self.config_file, 0o600)  # Secure permissions
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_api_key(self) -> str:
        config = self.load_config()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            return api_key
        
        if config.get("gemini_api_key"):
            return config["gemini_api_key"]

        print("\nGemini API Key Required")
        print("To use AI features, you need a Gemini API key from Google AI Studio.")
        print("Get one at: https://aistudio.google.com/app/apikey")
        print()
        
        while True:
            api_key = input("Enter your Gemini API key: ").strip()
            if api_key and len(api_key) > 10:
                config["gemini_api_key"] = api_key
                if self.save_config(config):
                    print("API key saved securely!")
                return api_key
            else:
                print("Invalid API key. Please try again.")
    
    def get_model_config(self) -> Dict[str, Any]:
        config = self.load_config()
        return {
            "model": config.get("model", "gemini-2.5-flash"),
            "max_tokens": config.get("max_tokens", 4000),
            "temperature": config.get("temperature", 0.7),
            "safety_settings": config.get("safety_settings", self.default_config["safety_settings"])
        }

config = Config()
