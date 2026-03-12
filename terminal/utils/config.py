import json
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".dwarp_config.json"

DEFAULTS = {
    "gemini_api_key": None,
    "model": "gemini-2.5-flash",
    "max_tokens": 10000,
    "temperature": 0.7,
    "safety_settings": {
        "harassment": "BLOCK_MEDIUM_AND_ABOVE",
        "hate_speech": "BLOCK_MEDIUM_AND_ABOVE",
        "dangerous_content": "BLOCK_MEDIUM_AND_ABOVE",
        "sexual_content": "BLOCK_MEDIUM_AND_ABOVE",
    },
}


@dataclass
class Config:
    config_file: Path = DEFAULT_CONFIG_PATH
    model_override: str | None = None

    def __post_init__(self):
        self.config_file = Path(self.config_file)

    def load(self) -> dict:
        if not self.config_file.exists():
            return DEFAULTS.copy()
        try:
            with open(self.config_file) as f:
                return {**DEFAULTS, **json.load(f)}
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            return DEFAULTS.copy()

    def save(self, data: dict) -> bool:
        try:
            with open(self.config_file, "w") as f:
                json.dump(data, f, indent=2)
            os.chmod(self.config_file, mode=0o600)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_api_key(self) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            return api_key

        data = self.load()
        if data.get("gemini_api_key"):
            return data["gemini_api_key"]

        print("\nGemini API Key Required")
        print("To use AI features, you need a Gemini API key from Google AI Studio.")
        print("Get one at: https://aistudio.google.com/app/apikey\n")

        while True:
            api_key = input("Enter your Gemini API key: ").strip()
            if api_key and len(api_key) > 10:
                data["gemini_api_key"] = api_key
                if self.save(data):
                    print("API key saved securely!")
                return api_key
            print("Invalid API key. Please try again.")

    def get_model_config(self) -> dict:
        data = self.load()
        return {
            "model": self.model_override or data.get("model", "gemini-2.5-flash"),
            "max_tokens": data.get("max_tokens", 4000),
            "temperature": data.get("temperature", 0.7),
            "safety_settings": data.get("safety_settings", DEFAULTS["safety_settings"]),
        }


config = Config()
