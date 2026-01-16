from .imports import *
from common.config import CONFIG_CORE, CONFIG_COMPTA
from datetime import datetime, timezone
from common.langManager import lang_manager
import discord
import logging

logger = logging.getLogger(__name__)
t = lang_manager.translation_key

def date_now():
    return datetime.now(timezone.utc)

def command_log(command_name: str, user_id: int, user_name: str) -> None:
    logger.info(f"[{user_name}->id: {user_id}] a exécuté la commande [/{command_name}]")

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
        color=discord.Color.dark_red()
    )
    embed_message.add_field(
        name=t("embed.message.name"),
        value=t("embed.message.value"),
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

async def send_with_warning(
    interaction: discord.Interaction,
    embeds: list[discord.Embed],
    ephemeral: bool = True,
    config: dict = CONFIG_CORE
    ):
    if config.get("MESSAGE", False):
        embeds.append(message_embed())
    if config.get("TRAVAUX", False):
        embeds.append(travaux_embed())
    if config.get("MAINTENANCE", False):
        embeds.append(maintenance_embed())

    await interaction.followup.send(embeds=embeds, ephemeral=ephemeral)

def get_ephemeral(interaction, default=True):
    EPHEMERAL_GLOBAL = load_bot_config("ephemeral")
    print(EPHEMERAL_GLOBAL)
    return EPHEMERAL_GLOBAL if interaction else default