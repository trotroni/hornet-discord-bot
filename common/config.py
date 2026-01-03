from imports import *

def reload_nude_core_config():
    load_dotenv(dotenv_path="../var.env")

    NUDE_COMPTA_TOKEN = os.getenv("NUDE_COMPTA_TOKEN")
    GUILD_ID_STR = os.getenv("GUILD_ID")
    GUILD_ID = int(GUILD_ID_STR)
    guild_obj = discord.Object(id=GUILD_ID)
    CHANNEL_ID_NOTIF = os.getenv("CHANNEL_ID_NOTIF")

    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "fr")
    EPHEMERAL_ENV = os.getenv("EPHEMERAL_ENV", "true").lower()
    EPHEMERAL_GLOBAL = EPHEMERAL_ENV == "true"
    VERSION = os.getenv("VERSION")

    if not NUDE_COMPTA_TOKEN:
        logger.error("❌ NUDE_COMPTA_TOKEN manquant dans les fichiers .env")
        raise ValueError("❌ NUDE_COMPTA_TOKEN manquant dans les fichiers .env")
    elif not GUILD_ID_STR:
        logger.error("❌ GUILD_ID_STR manquant dans les fichiers .env")
        raise ValueError("❌ GUILD_ID_STR manquant dans les fichiers .env")
        if not GUILD_ID:
            logger.error("❌ Échec de la convertion de GUILD_ID en 'int'")
            raise ValueError("❌ Échec de la convertion de GUILD_ID en 'int'")
            if guild_obj is None:
                logger.error("❌ GUILD_ID invalide, impossible de créer l'objet guild")
                raise ValueError("❌ GUILD_ID invalide, impossible de créer l'objet guild")
    elif not CHANNEL_ID_NOTIF:
        logger.error("❌ CHANNEL_ID_NOTIF manquant dans les fichiers .env")
        raise ValueError("❌ CHANNEL_ID_NOTIF manquant dans les fichiers .env")

    elif not DEFAULT_LANGUAGE:
        logger.error("❌ DEFAULT_LANGUAGE manquant dans les fichiers .env")
        raise ValueError("❌ DEFAULT_LANGUAGE manquant dans les fichiers .env")
    elif EPHEMERAL_ENV not in ["true", "false"]:
        logger.error("❌ EPHEMERAL_ENV doit être 'true' ou 'false'")
        raise ValueError("❌ EPHEMERAL_ENV doit être 'true' ou 'false'")

    logger.info(f"✅ Configuration chargée: GUILD_ID={GUILD_ID}, CHANNEL_ID_NOTIF={CHANNEL_ID_NOTIF}, ADMIN_ROLE_ID={ADMIN_ROLE_ID}, DEFAULT_LANGUAGE={DEFAULT_LANGUAGE}, EPHEMERAL_GLOBAL={EPHEMERAL_GLOBAL}")

def reload_nude_compta_config():
    load_dotenv(dotenv_path="../var.env")

    NUDE_CORE_TOKEN = os.getenv("NUDE_CORE_TOKEN")
    GUILD_ID_STR = os.getenv("GUILD_ID")
    GUILD_ID = int(GUILD_ID_STR)
    guild_obj = discord.Object(id=GUILD_ID)
    CHANNEL_ID_NOTIF = os.getenv("CHANNEL_ID_NOTIF")

    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "fr")
    EPHEMERAL_ENV = os.getenv("EPHEMERAL_ENV", "true").lower()
    EPHEMERAL_GLOBAL = EPHEMERAL_ENV == "true"
    VERSION = os.getenv("VERSION")

    if not NUDE_CORE_TOKEN:
        logger.error("❌ NUDE_CORE_TOKEN manquant dans les fichiers .env")
        raise ValueError("❌ NUDE_CORE_TOKEN manquant dans les fichiers .env")
    elif not GUILD_ID_STR:
        logger.error("❌ GUILD_ID_STR manquant dans les fichiers .env")
        raise ValueError("❌ GUILD_ID_STR manquant dans les fichiers .env")
        if not GUILD_ID:
            logger.error("❌ Échec de la convertion de GUILD_ID en 'int'")
            raise ValueError("❌ Échec de la convertion de GUILD_ID en 'int'")
            if guild_obj is None:
                logger.error("❌ GUILD_ID invalide, impossible de créer l'objet guild")
                raise ValueError("❌ GUILD_ID invalide, impossible de créer l'objet guild")
    elif not CHANNEL_ID_NOTIF:
        logger.error("❌ CHANNEL_ID_NOTIF manquant dans les fichiers .env")
        raise ValueError("❌ CHANNEL_ID_NOTIF manquant dans les fichiers .env")

    elif not DEFAULT_LANGUAGE:
        logger.error("❌ DEFAULT_LANGUAGE manquant dans les fichiers .env")
        raise ValueError("❌ DEFAULT_LANGUAGE manquant dans les fichiers .env")
    elif EPHEMERAL_ENV not in ["true", "false"]:
        logger.error("❌ EPHEMERAL_ENV doit être 'true' ou 'false'")
        raise ValueError("❌ EPHEMERAL_ENV doit être 'true' ou 'false'")

    logger.info(f"✅ Configuration chargée: GUILD_ID={GUILD_ID}, CHANNEL_ID_NOTIF={CHANNEL_ID_NOTIF}, ADMIN_ROLE_ID={ADMIN_ROLE_ID}, DEFAULT_LANGUAGE={DEFAULT_LANGUAGE}, EPHEMERAL_GLOBAL={EPHEMERAL_GLOBAL}")
