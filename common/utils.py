# common/utils.py
from common.imports import *
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
import asyncio
import time

logger = logging.getLogger(__name__)
t = lang_manager.translation_key

def load_reactions():
    with open("/home/trotroni/nude-discord-bot/hornet-bot/reactions.json", "r", encoding="utf-8") as f:
        return json.load(f)

REACTION_TOPICS = load_reactions()

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
    print("fonction appelée")
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
    except Exception:
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
    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
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
            "thumbnail": info.get("thumbnail"),
            "uploader": info.get("uploader"),
            "view_count": info.get("view_count"),
        }

def format_duration(seconds: int) -> str:
    if not seconds:
        return "00:00"

    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)

    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"
    return f"{minutes}:{seconds:02}"


def progress_bar(current: int, total: int, length: int = 20):
    if not total:
        return "🔴 LIVE"

    filled = int(length * current / total)
    bar = "▬" * filled + "🔘" + "▬" * (length - filled)
    return bar


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

    def list(self):
        return list(self.queue)

    def __len__(self):
        return len(self.queue)

class MusicPlayer:
    def __init__(self):
        self.voice_client = None
        self.current = None
        self.start_time = None
        self.paused_time = 0
        self.is_paused = False
        self.progress_task = None
        self.message = None
        self.queue = AudioQueue()
        self.loop_track = False
        self.loop_queue = False

    async def start_progress_loop(self):
        while self.voice_client and self.voice_client.is_playing():
            current_time = int(time.time() - self.start_time)
            total = self.current.get("duration")

            bar = progress_bar(current_time, total)
            duration_text = f"{format_duration(current_time)} / {format_duration(total)}"

            embed = discord.Embed(
                title="🎵 Lecture en cours",
                description=f"**[{self.current['title']}]({self.current.get('webpage_url')})**\n\n{bar}\n`{duration_text}`",
                color=discord.Color.green()
            )

            if self.current.get("thumbnail"):
                embed.set_thumbnail(url=self.current["thumbnail"])

            if self.current.get("uploader"):
                embed.add_field(name="👤 Auteur", value=self.current["uploader"], inline=True)

            if self.current.get("view_count"):
                embed.add_field(name="👁 Vues", value=f"{self.current['view_count']:,}", inline=True)

            embed.timestamp = date_now()

            try:
                await self.message.edit(embed=embed, view=MusicControls(self))
            except:
                pass

            await asyncio.sleep(5)

    async def play_next(self):
        if self.loop_track and self.current:
            song_to_play = self.current
        else:
            song_to_play = self.queue.next()
            if not song_to_play:
                if self.loop_queue:
                    # Reset la queue
                    self.queue.queue = deque(list(self.queue.list()))
                    song_to_play = self.queue.next()
                else:
                    self.current = None
                    return

        self.current = song_to_play

        source = discord.FFmpegPCMAudio(
            self.current["url"],
            **FFMPEG_OPTIONS
        )

        self.voice_client.play(
            source,
            after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(), self.voice_client.loop
            )
        )

        self.start_time = time.time()
        if self.progress_task:
            self.progress_task.cancel()
        self.progress_task = asyncio.create_task(self.start_progress_loop())


class MusicControls(discord.ui.View):
    def __init__(self, player: MusicPlayer):
        super().__init__(timeout=None)
        self.player = player

    @discord.ui.button(label="⏸ Pause", style=discord.ButtonStyle.gray)
    async def pause(self, interaction: discord.Interaction):
        if self.player.voice_client.is_playing():
            self.player.voice_client.pause()
            self.player.paused_time = time.time()
            self.player.is_paused = True
        await interaction.response.defer()

    @discord.ui.button(label="▶ Resume", style=discord.ButtonStyle.green)
    async def resume(self, interaction: discord.Interaction):
        if self.player.voice_client.is_paused():
            self.player.voice_client.resume()
            self.player.start_time += time.time() - self.player.paused_time
            self.player.is_paused = False
        await interaction.response.defer()

    @discord.ui.button(label="⏭ Skip", style=discord.ButtonStyle.red)
    async def skip(self, interaction: discord.Interaction):
        self.player.voice_client.stop()
        await interaction.response.defer()

    @discord.ui.button(label="🔁 Loop Track", style=discord.ButtonStyle.gray)
    async def loop_track(self, interaction: discord.Interaction):
        self.player.loop_track = not self.player.loop_track
        state = "activé" if self.player.loop_track else "désactivé"
        await interaction.response.send_message(f"🔁 Loop du morceau {state}", ephemeral=ephemeral)

    @discord.ui.button(label="📜 Queue", style=discord.ButtonStyle.blurple)
    async def queue_button(self, interaction: discord.Interaction):
        queue_list = self.player.queue.list()

        if not queue_list:
            await interaction.response.send_message("Queue vide.", ephemeral=ephemeral)
            return

        description = "\n".join(
            [f"{i+1}. {song['title']}" for i, song in enumerate(queue_list)]
        )

        embed = discord.Embed(
            title="📜 File d'attente",
            description=description,
            color=discord.Color.blue()
        )

        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    @discord.ui.button(label="🔂 Loop Queue", style=discord.ButtonStyle.blurple)
    async def loop_queue(self, interaction: discord.Interaction):
        self.player.loop_queue = not self.player.loop_queue
        state = "activé" if self.player.loop_queue else "désactivé"
        await interaction.response.send_message(f"🔂 Loop de la queue {state}", ephemeral=ephemeral)


# fichier de stockage des playlists
PLAYLIST_FILE = Path("/home/trotroni/nude-discord-bot/common/data/playlists.json")
logger.info(f"path playlist : {PLAYLIST_FILE}")


# dictionnaire global des playlists
playlists = {}  # {number: [url1, url2, ...]}

def save_playlists():
    """Sauvegarde les playlists dans le fichier JSON"""
    try:
        with PLAYLIST_FILE.open("w", encoding="utf-8") as f:
            json.dump(playlists, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde playlists : {e}")
        return False

def load_playlists():
    """Charge les playlists depuis le fichier JSON"""
    global playlists
    if PLAYLIST_FILE.exists():
        try:
            with PLAYLIST_FILE.open("r", encoding="utf-8") as f:
                playlists = json.load(f)
        except Exception as e:
            logger.error(f"❌ Erreur lecture playlists : {e}")
            playlists = {}

# utils pour fan controle
CONFIG_PATH = "/etc/fan/fan.conf"
CONFIG_PATH_SAVE = "/home/trotroni/nude-discord-bot/common/data/fan-backup.conf"

def generate_fanconfig(temp_min, temp_max, pwm_min, pwm_max, steps=8, k=3):
    lines = []
    lines.append("debug=false\n\n")
    lines.append("main:\n    1=15\n")

    for i in range(steps + 1):
        T = temp_min + (temp_max - temp_min) * i / steps
        x = (T - temp_min) / (temp_max - temp_min)
        pwm = pwm_min + (pwm_max - pwm_min) * (math.exp(k*x) - 1) / (math.exp(k) - 1)
        lines.append(f"    {round(T,1)}={round(pwm)}\n")

    lines.append("\ndebug:\n")
    lines.append("    1=100\n")

    return "".join(lines)


def write_config(content: str, save_backup=True):
    # Si on doit sauvegarder l'ancienne config
    if save_backup and os.path.exists(CONFIG_PATH):
        shutil.copy(CONFIG_PATH, CONFIG_PATH_SAVE)

    with open(CONFIG_PATH, "w") as f:
        f.write(content)

def restore_config():
    if os.path.exists(CONFIG_PATH_SAVE):
        shutil.copy(CONFIG_PATH_SAVE, CONFIG_PATH)
        return True
    return False

def is_panic_mode():
    if not os.path.exists(CONFIG_PATH):
        return False

    with open(CONFIG_PATH, "r") as f:
        for line in f:
            if line.strip().lower() == "debug=true":
                return True
    return False

class FanConfirmView(View):
    def __init__(self, config_content, backup=True):
        super().__init__(timeout=False)
        self.config_content = config_content
        self.applied = False
        self.backup = backup

    @discord.ui.button(label="Confirmer ✅", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        write_config(self.config_content, save_backup=self.backup)
        self.applied = True
        await interaction.response.edit_message(content="✅ Configuration appliquée !", embed=None, view=None)
        self.stop()

    @discord.ui.button(label="Annuler ❌", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="❌ Configuration annulée.", embed=None, view=None)
        self.stop()