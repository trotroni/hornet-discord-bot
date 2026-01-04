from .imports import *
from common.loggingBot import getLogger
from common.config import LANG_DIR

logger = getLogger("lang_manager")

class LanguageManager:
    def __init__(self):
        self.translations = {}
        self.available_languages = []
        self.user_preferences = {}
        self.default_language = "fr"
        self.lang_dir = None

    def configure(self, config: dict):
        self.default_language = config.get("DEFAULT_LANGUAGE", "fr")
        self.lang_dir = Path(config.get("LANG_DIR", "languages"))

    def load_languages(self):
        if not self.lang_dir:
            raise RuntimeError("LanguageManager non configuré")
        self.translations.clear()
        self.available_languages.clear()
        files = list(LANG_DIR.glob("*.json"))
        if not files:
            logger.error(f"❌ Aucun fichier de langue dans {LANG_DIR}")
            raise FileNotFoundError("Aucun fichier de traduction")

        for file in files:
            lang_code = file.stem
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
                    self.available_languages.append(lang_code)
                logger.info(f"✅ Langue chargée : {lang_code}")
            except Exception as e:
                logger.error(f"❌ Erreur chargement {file}: {e}")
        if not self.available_languages:
            raise ValueError("Aucune langue valide chargée")

    def get(self, key: str, user_id: int = None, **kwargs) -> str:
        lang = self.user_preferences.get(user_id, self.default_language)
        if lang not in self.translations:
            lang = CONFIG["DEFAULT_LANGUAGE"]

        data = self.translations.get(lang, {})
        for part in key.split("."):
            if not isinstance(data, dict):
                return f"[{key}]"
            data = data.get(part)
        if data is None:
            return f"[{key}]"
        try:
            return data.format(**kwargs)
        except KeyError as e:
            logger.warning(f"⚠️ Variable manquante pour '{key}': {e}")
            return data

    def set_user_language(self, user_id: int, language: str) -> bool:
        if language in self.available_languages:
            self.user_preferences[user_id] = language
            return True
        return False

    def get_language_name(self, lang_code: str) -> str:
        return self.translations.get(lang_code, {}).get("language_name", lang_code)

lang_manager = LanguageManager()
