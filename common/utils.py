from .imports import *
from .config import EPHEMERAL_GLOBAL

from common.loggingBot import getLogger
logger = getLogger("langManager.py")

def get_ephemeral(interaction, default=True):
    return EPHEMERAL_GLOBAL if interaction else default
