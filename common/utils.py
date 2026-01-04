from .imports import *
from .config import EPHEMERAL_GLOBAL

def get_ephemeral(interaction, default=True):
    return EPHEMERAL_GLOBAL if interaction else default
