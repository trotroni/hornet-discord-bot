# common/langManager.py

import json
import logging
from pathlib import Path
from common.config import LANG_DIR
logger = logging.getLogger(__name__)


class LanguageManager:
    def __init__(self):
        self.translations = {}
        self.available_languages = []
        self.user_preferences = {}
        self.default_language = "fr"
        self.lang_dir = None

    def configure(self, config: dict):
        self.default_language = config.get("DEFAULT_LANGUAGE", "fr")
        self.lang_dir = Path(config.get("LANG_DIR", LANG_DIR))

    def load_languages(self):
        files = list(LANG_DIR.glob("*.json"))
        if not files:
            raise FileNotFoundError("Aucun fichier de langue")

        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                self.translations[file.stem] = json.load(f)
                self.available_languages.append(file.stem)
            logger.info(f"✅ Langue chargée : {file.stem}")

    def translation_key(self, key: str, lang: str | None = None, **kwargs) -> str:
        lang = lang or self.default_language
        data = self.translations.get(lang, {})
        for part in key.split("."):
            data = data.get(part, {})
            if not isinstance(data, dict):
                break
        value = data if isinstance(data, str) else key
        return value.format(**kwargs)


lang_manager = LanguageManager()
