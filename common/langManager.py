# common/langManager.py

import json
import logging
from pathlib import Path
from common.config import LANG_DIR

logger = logging.getLogger(__name__)


class LanguageManager:
    def __init__(self):
        self.translations: dict[str, dict] = {}
        self.available_languages: dict[str, str] = {}
        self.user_preferences: dict[int, str] = {}
        self.default_language: str = "fr"
        self.lang_dir: Path | None = None

    def configure(self, config: dict):
        self.default_language = config.get("DEFAULT_LANGUAGE", "fr")
        self.lang_dir = Path(config.get("LANG_DIR", LANG_DIR))

    def load_languages(self):
        """Charge toutes les langues depuis les JSON dans LANG_DIR"""
        if not self.lang_dir or not self.lang_dir.exists():
            raise FileNotFoundError(f"Dossier des langues introuvable : {self.lang_dir}")

        files = list(self.lang_dir.glob("*.json"))
        if not files:
            raise FileNotFoundError("Aucun fichier de langue trouvé")

        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                lang_code = data.get("code", file.stem)        # code de la langue
                lang_name = data.get("name", lang_code)       # nom lisible
                self.translations[lang_code] = data
                self.available_languages[lang_code] = lang_name
            logger.info(f"✅ Langue chargée : {lang_code} ({lang_name})")

    def translation_key(self, key: str, lang: str | None = None, **kwargs) -> str:
        """Récupère la traduction d'une clé, injecte kwargs si nécessaire"""
        lang = lang or self.default_language
        data = self.translations.get(lang, {})

        for part in key.split("."):
            if isinstance(data, dict) and part in data:
                data = data[part]
            else:
                data = key
                break

        if not isinstance(data, str):
            data = key

        return data.format(**kwargs)


# instance globale
lang_manager = LanguageManager()
