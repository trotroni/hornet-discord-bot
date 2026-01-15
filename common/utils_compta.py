from datetime import datetime
import json
import os
import discord
from discord.ui import View, Button

DATA_DIR = "../nude-compta-bot/data"

def now_iso():
    return datetime.utcnow().isoformat()

def _get_all_ids():
    ids = []

    for name in ("tickets.json", "archives.json"):
        path = os.path.join(DATA_DIR, name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                ids.extend(json.load(f).keys())

    return ids

def generate_ticket_id(type_ticket):
    prefix = "a" if type_ticket == "p2p" else "b"
    ids = _get_all_ids()

    nums = [
        int(i[1:]) for i in ids
        if i.startswith(prefix) and i[1:].isdigit()
    ]

    next_num = max(nums, default=0) + 1
    return f"{prefix}{next_num:04d}"

def euros_to_cents(amount: float) -> int:
    return int(round(amount * 100))

def cents_to_euros(amount: int) -> str:
    return f"{amount / 100:.2f}€"

def embed_color(type_ticket: str) -> discord.Color:
    type_ticket = type_ticket.lower()
    
    if type_ticket == "p2p":
        return discord.Color.blue()
    elif type_ticket == "groupe":
        return discord.Color.green()
    elif type_ticket == "remboursement":
        return discord.Color.orange()
    elif type_ticket == "alerte":
        return discord.Color.red()
    else:
        # Couleur par défaut si type inconnu
        return discord.Color.magenta()
