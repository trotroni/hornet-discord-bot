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

# Charger .env
load_dotenv(dotenv_path=BASE_DIR / "var.env")

# ---------- CONFIG GÉNÉRALE ----------
CONFIG_GENERAL = {
    "GUILD_ID": int(os.getenv("GUILD_ID", "0")) if os.getenv("GUILD_ID") else None,
    "DEFAULT_LANGUAGE": os.getenv("DEFAULT_LANGUAGE", "fr"),
    "EPHEMERAL_GLOBAL": os.getenv("EPHEMERAL_ENV", "false").lower() in ("1", "true", "yes"),
    "VERSION": os.getenv("VERSION", "dev"),
    "DEBUG": os.getenv("DEBUG", "false").lower() in ("1", "true", "yes"),
    "NOTIF_CHANNEL_ID": os.getenv("NOTIF_CHANNEL_ID"),
    "LOG_CHANNEL_ID": os.getenv("LOG_CHANNEL_ID"),
    "NERD_CHANNEL_ID": os.getenv("NERD_CHANNEL_ID"),
    "TRAVAUX": os.getenv("TRAVAUX_EMBED", "false").lower() in ("1", "true", "yes"),
    "MESSAGE": os.getenv("MESSAGE_EMBED", "false").lower() in ("1", "true", "yes"),
    "MAINTENANCE": os.getenv("MAINTENANCE_EMBED", "false").lower() in ("1", "true", "yes"),
}

# ---------- CONFIG CORE ----------
CONFIG_CORE = {
    "BOT_NAME": "nude-core-bot",
    "TOKEN": os.getenv("NUDE_CORE_TOKEN")
}

# ---------- CONFIG COMPTA ----------
CONFIG_COMPTA = {
    "BOT_NAME": "nude-compta-bot",
    "TOKEN": os.getenv("NUDE_COMPTA_TOKEN")
}

# ---------- FONCTION DE CHARGEMENT ----------
def load_bot_config(bot_type: str) -> dict:
    if bot_type == "core":
        specific = CONFIG_CORE
    elif bot_type == "compta":
        specific = CONFIG_COMPTA
    else:
        raise ValueError(f"Bot type inconnu : {bot_type}")

    config = {**CONFIG_GENERAL, **specific}

    if config["DEBUG"]:
        logger.info(f"🐞 Mode DEBUG activé pour {config['BOT_NAME']}")

    if not config.get("TOKEN"):
        raise ValueError(f"❌ Token manquant pour {bot_type}")
    if not config.get("GUILD_ID"):
        raise ValueError("❌ GUILD_ID manquant")

    return config
