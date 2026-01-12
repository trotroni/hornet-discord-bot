# common/utils.py
from .imports import *
from common.config import load_bot_config
from typing import Union
import logging
logger = logging.getLogger(__name__)

def get_ephemeral(interaction, default=True):
    EPHEMERAL_GLOBAL = load_bot_config("ephemeral")
    print(EPHEMERAL_GLOBAL)
    return EPHEMERAL_GLOBAL if interaction else default

def command_log(command_name: str, user_id: int, user_name: str) -> None:
    logger.info(
        f"[{user_name}->id: {user_id}] a exécuté la commande [/{command_name}]"
    )


def date_now():
    return datetime.now(timezone.utc)
