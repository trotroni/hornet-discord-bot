# common/utils.py
from common.config import CONFIG_CORE, CONFIG_GENERAL
from datetime import datetime, timezone
from common.langManager import lang_manager
import discord
import logging
import subprocess
import json
from pathlib import Path
import yt_dlp
from collections import deque

logger = logging.getLogger(__name__)
t = lang_manager.translation_key

custom_commands = {}

CUSTOM_COMMANDS_FILE = Path("custom_commands.json")

def load_custom_commands():
    global custom_commands
    if CUSTOM_COMMANDS_FILE.exists():
        with open(CUSTOM_COMMANDS_FILE, "r", encoding="utf-8") as f:
            custom_commands = json.load(f)
    else:
        custom_commands = {}

def save_custom_commands():
    try:
        with open(CUSTOM_COMMANDS_FILE, "w", encoding="utf-8") as f:
            json.dump(custom_commands, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def date_now():
    return datetime.now(timezone.utc)

def command_log(command_name: str, user_id: int, user_name: str) -> None:
    logger.info(f"[{user_name}->id: {user_id}] a exécuté la commande [/{command_name}]")

async def send_with_warning(
    interaction: discord.Interaction,
    embeds: list[discord.Embed],
    ephemeral: bool = True,
    config: dict = CONFIG_GENERAL
    ):

    if config.get("MESSAGE", False):
        embeds.append(message_embed())
    if config.get("TRAVAUX", False):
        embeds.append(travaux_embed())
    if config.get("MAINTENANCE", False):
        embeds.append(maintenance_embed())

    await interaction.followup.send(embeds=embeds, ephemeral=ephemeral)

def travaux_embed() -> discord.Embed:
    embed_travaux = discord.Embed(
        title=t("embed.travaux.title"),
        description=t("embed.travaux.description"),
        color=discord.Color.yellow()
    )
    embed_travaux.add_field(
        name=t("embed.bugs.name"),
        value=t("embed.bugs.value"),
        inline=False
    )
    embed_travaux.timestamp = date_now()
    return embed_travaux

def message_embed() -> discord.Embed:
    embed_message = discord.Embed(
        title=t("embed.message.title"),
        description=t("embed.message.description"),
        color=discord.Color.light_embed()
    )
    embed_message.add_field(
        name=t("embed.message.add.name"),
        value=t("embed.message.add.value"),
        inline=False
    )
    embed_message.timestamp = date_now()
    return embed_message

def maintenance_embed() -> discord.Embed:
    embed_maintenance = discord.Embed(
        title=t("embed.maintenance.title"),
        description=t("embed.maintenance.description"),
        color=discord.Color.blue()
    )
    embed_maintenance.add_field(
        name=t("embed.bugs.name"),
        value=t("embed.bugs.value"),
        inline=False
    )
    embed_maintenance.timestamp = date_now()
    return embed_maintenance

def get_ephemeral(interaction, default=True):
    EPHEMERAL_GLOBAL = load_bot_config("core").get("EPHEMERAL_GLOBAL", default)
    return EPHEMERAL_GLOBAL if interaction else default

def get_cpu_temperature(config: dict = CONFIG_GENERAL):
    if config.get("DEBUG", True):
        return "90.0"
    try:
        result = subprocess.run(
            ["vcgencmd", "measure_temp"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if result.returncode == 0:
            return result.stdout.strip().replace("temp=", "")
    except Exception:
        pass
    return "N/A"

def cpu_temp_verification(temp_celsius) -> str:
    try:
        t = float(temp_celsius)
    except (ValueError, TypeError):
        return "⚪ Inconnu"

    if t < 45:
        return "🟢 Excellent"
    elif t < 55:
        return "🟢 Normal"
    elif t < 65:
        return "🟡 Chaud"
    elif t < 75:
        return "🟠 Élevé"
    else:
        return "🔴 Critique"

def get_fan_pwm(config: dict = CONFIG_GENERAL):
    try:
        result = subprocess.run(
            ["fan_pwm", "read", "pwm"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "`N/A` — `Inconnu`"

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "default_search": "ytsearch",
    "nocheckcertificate": True,
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

def get_audio_source(query: str) -> dict:
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "default_search": "ytsearch"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)

        if not info:
            raise ValueError("Aucun résultat trouvé pour la requête.")

        if "entries" in info:
            if not info["entries"]:
                raise ValueError("Aucun résultat trouvé pour la requête.")
            info = info["entries"][0]

        if "url" not in info:
            raise ValueError("Aucun lien audio trouvé pour la requête.")

        return {
            "title": info.get("title", "Titre inconnu"),
            "url": info["url"],
            "webpage_url": info.get("webpage_url"),
            "duration": info.get("duration"),
        }


class AudioQueue:
    def __init__(self):
        self.queue = deque()

    def add(self, item):
        self.queue.append(item)

    def next(self):
        if self.queue:
            return self.queue.popleft()
        return None

    def clear(self):
        self.queue.clear()

    def empty(self):
        return len(self.queue) == 0

# fichier de stockage des playlists
PLAYLIST_FILE = Path("common/data/playlists.json")
print(PLAYLIST_FILE)

# dictionnaire global des playlists
playlists = {}  # {number: [url1, url2, ...]}

def save_playlists():
    """Sauvegarde les playlists dans le fichier JSON"""
    try:
        with PLAYLIST_FILE.open("w", encoding="utf-8") as f:
            json.dump(playlists, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde playlists : {e}")
        return False

def load_playlists():
    """Charge les playlists depuis le fichier JSON"""
    global playlists
    if PLAYLIST_FILE.exists():
        try:
            with PLAYLIST_FILE.open("r", encoding="utf-8") as f:
                playlists = json.load(f)
        except Exception as e:
            print(f"❌ Erreur lecture playlists : {e}")
            playlists = {}