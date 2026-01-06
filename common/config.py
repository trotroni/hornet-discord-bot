# common/config.py
from common.imports import *
from dotenv import load_dotenv
# -------------------------------
# Variables globales pour tous les bots
# -------------------------------
BASE_DIR = Path(__file__).parent.parent
print(f"📁 Dossier de base : {BASE_DIR}")
LOGS_DIR = BASE_DIR / "logs"
print(f"📁 Dossier des logs : {LOGS_DIR}")
LOGS_DIR.mkdir(exist_ok=True)

LANG_DIR = BASE_DIR / "languages"
print(f"📁 Dossier des langues : {LANG_DIR}")
LANG_DIR.mkdir(exist_ok=True)

COMMANDS_CSV = BASE_DIR / "commands.csv"
print(f"📁 Fichier des commandes : {COMMANDS_CSV}")
COMMANDS_CSV.touch(exist_ok=True)

WARN_FILE = BASE_DIR / "warns.csv"
print(f"📁 Fichier des warns : {WARN_FILE}")
WARN_FILE.touch(exist_ok=True)

# -------------------------------
# Fonction pour charger la config
# -------------------------------
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
    config["BOT_NAME"] = f"nude-{bot_type}-bot"

    # Vérifications
    if not config["TOKEN"]:
        raise ValueError(f"❌ Token manquant pour {bot_type}")
    if not config["GUILD_ID"]:
        raise ValueError("❌ GUILD_ID manquant ou invalide")
    if not config["CHANNEL_ID_NOTIF"]:
        raise ValueError("❌ CHANNEL_ID_NOTIF manquant")

    return config
