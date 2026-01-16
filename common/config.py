# common/config.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
logger.info(f"📁 Dossier de base : {BASE_DIR}")

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LANG_DIR = BASE_DIR / "languages"
LANG_DIR.mkdir(exist_ok=True)

COMMANDS_CSV = BASE_DIR / "commands.csv"
COMMANDS_CSV.touch(exist_ok=True)

WARN_FILE = BASE_DIR / "warns.csv"
WARN_FILE.touch(exist_ok=True)


def load_bot_config(bot_type: str) -> dict:
    load_dotenv(dotenv_path=BASE_DIR / "var.env")

    config = {}

    if bot_type == "core":
        config["TOKEN"] = os.getenv("NUDE_CORE_TOKEN")
    elif bot_type == "compta":
        config["TOKEN"] = os.getenv("NUDE_COMPTA_TOKEN")
    else:
        raise ValueError("bot_type doit être 'core' ou 'compta'")

    config["BOT_NAME"] = f"nude-{bot_type}-bot"
    config["GUILD_ID"] = int(os.getenv("GUILD_ID", "0")) or None
    config["CHANNEL_ID_NOTIF"] = os.getenv("CHANNEL_ID_NOTIF")
    config["GENERAL_CHANNEL_ID"] = os.getenv("GENERAL_CHANNEL_ID")
    config["DEFAULT_LANGUAGE"] = os.getenv("DEFAULT_LANGUAGE", "fr")
    config["VERSION"] = os.getenv("VERSION")
    config["EPHEMERAL_GLOBAL"] = os.getenv("EPHEMERAL_ENV", "true").lower() == "true"
    config["TRAVAUX"] = os.getenv("TRAVAUX_EMBED", "false").lower() == "true"
    config["MESSAGE"] = os.getenv("MESSAGE_EMBED", "false").lower() == "true"
    config["MAINTENANCE"] = os.getenv("MAINTENANCE_EMBED", "false").lower() == "true"
    debug_env = os.getenv("DEBUG", "false").lower()
    config["DEBUG"] = debug_env in ("1", "true", "yes", "on")

    if config["DEBUG"]:
        logger.info("🐞 Mode DEBUG activé")

    if not config["TOKEN"]:
        raise ValueError("❌ Token manquant")
    if not config["GUILD_ID"]:
        raise ValueError("❌ GUILD_ID manquant")

    return config


# --- Variables globales pour chaque bot ---
try:
    CONFIG_CORE = load_bot_config("core")
    CONFIG_COMPTA = load_bot_config("compta")
except Exception as e:
    logger.critical(f"❌ Impossible de charger les configs : {e}")
    CONFIG_CORE = {}
    CONFIG_COMPTA = {}
