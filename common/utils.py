from imports import *
from configuration import EPHEMERAL_GLOBAL
from gestion_langues import lang_manager

def get_ephemeral(interaction, default=True):
    return EPHEMERAL_GLOBAL if interaction else default
