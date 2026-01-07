# common/utils.py
from .imports import *
from common.config import load_bot_config

def get_ephemeral(interaction, default=True):
    EPHEMERAL_GLOBAL = load_bot_config("ephemeral")
    print(EPHEMERAL_GLOBAL)
    return EPHEMERAL_GLOBAL if interaction else default

def command_log(command_name: str, user_name: int) -> None:
    logger.info(f"L'utilisateur {user_name} a exécuté la commande {command_name}")
