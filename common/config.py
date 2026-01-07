# common/config.py
from common.imports import *
from dotenv import load_dotenv
from common.loggingBot import getLogger
from common.init import CONFIG

logger = getLogger("config.py", CONFIG["BOT_NAME"])

# -------------------------------
# Variables globales pour tous les bots
# -------------------------------
BASE_DIR = Path(__file__).parent.parent
logger.info(f"📁 Dossier de base : {BASE_DIR}")

LOGS_DIR = BASE_DIR / "logs"
logger.info(f"📁 Dossier des logs : {LOGS_DIR}")
LOGS_DIR.mkdir(exist_ok=True)

LANG_DIR = BASE_DIR / "languages"
logger.info(f"📁 Dossier des langues : {LANG_DIR}")
LANG_DIR.mkdir(exist_ok=True)

COMMANDS_CSV = BASE_DIR / "commands.csv"
logger.info(f"📁 Fichier des commandes : {COMMANDS_CSV}")
COMMANDS_CSV.touch(exist_ok=True)

WARN_FILE = BASE_DIR / "warns.csv"
logger.info(f"📁 Fichier des warns : {WARN_FILE}")
WARN_FILE.touch(exist_ok=True)

def load_bot_config(bot_type: str = ""):

    load_dotenv(dotenv_path=BASE_DIR / "var.env")

    config = {}

    if bot_type == "core":
        config["TOKEN"] = os.getenv("NUDE_CORE_TOKEN")
    elif bot_type == "compta":
        config["TOKEN"] = os.getenv("NUDE_COMPTA_TOKEN")
    else:
        raise ValueError("bot_type doit être 'core' ou 'compta'")

    config["GUILD_ID_STR"] = os.getenv("GUILD_ID")
    config["GUILD_ID"] = int(config["GUILD_ID_STR"]) if config["GUILD_ID_STR"] else None
    config["CHANNEL_ID_NOTIF"] = os.getenv("CHANNEL_ID_NOTIF")
    config["DEFAULT_LANGUAGE"] = os.getenv("DEFAULT_LANGUAGE", "fr")
    config["EPHEMERAL_GLOBAL"] = os.getenv("EPHEMERAL_ENV", "true").lower() == "true"
    config["VERSION"] = os.getenv("VERSION")
    config["ADMIN_ROLE_ID"] = os.getenv("ADMIN_ROLE_ID")

    # DEBUG
    debug_env = os.getenv("DEBUG", "false").lower()
    config["DEBUG"] = debug_env in ("1", "true", "yes", "on")

    config["BOT_NAME"] = f"nude-{bot_type}-bot"

    if config["DEBUG"]:
        logger.info(f"🐞 Mode DEBUG activé")

    # Vérifications
    if not config["TOKEN"]:
        logger.error(f"❌ Token manquant pour {bot_type}")
        raise ValueError(f"❌ Token manquant pour {bot_type}")
    if not config["GUILD_ID"]:
        logger.error("❌ GUILD_ID manquant ou invalide")
        raise ValueError("❌ GUILD_ID manquant ou invalide")
    if not config["CHANNEL_ID_NOTIF"]:
        logger.error("❌ CHANNEL_ID_NOTIF manquant")
        raise ValueError("❌ CHANNEL_ID_NOTIF manquant")

    return config
