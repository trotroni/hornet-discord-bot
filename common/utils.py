from .imports import *
from common.config import CONFIG_CORE, CONFIG_COMPTA
from datetime import datetime, timezone
import discord
import logging

logger = logging.getLogger(__name__)

def date_now():
    return datetime.now(timezone.utc)

def command_log(command_name: str, user_id: int, user_name: str) -> None:
    logger.info(f"[{user_name}->id: {user_id}] a exécuté la commande [/{command_name}]")

def get_warning_embed() -> discord.Embed:
    embed_warning = discord.Embed(
        title="⚠️ Travaux en cours",
        description="Certaines fonctionnalités peuvent être instables.",
        color=discord.Color.yellow()
    )
    embed_warning.add_field(
        name="Maintenance",
        value="Merci de votre compréhension, le bot peut avoir des bugs.",
        inline=False
    )
    embed_warning.timestamp = date_now()
    return embed_warning

async def send_with_warning(
    interaction: discord.Interaction,
    embeds: list[discord.Embed],
    ephemeral: bool = True,
    config: dict = CONFIG_CORE  # par défaut core
):
    if config.get("TRAVAUX", False):
        embeds.append(get_warning_embed())
    await interaction.followup.send(embeds=embeds, ephemeral=ephemeral)

def get_ephemeral(interaction, default=True):
    EPHEMERAL_GLOBAL = load_bot_config("ephemeral")
    print(EPHEMERAL_GLOBAL)
    return EPHEMERAL_GLOBAL if interaction else default