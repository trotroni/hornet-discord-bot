# common/init.py

import logging
from pathlib import Path
import discord
from discord.ext import commands

from common.config import load_bot_config
from common.loggingBot import configure_logging


class MyBot(commands.Bot):
    def __init__(self, config: dict, **kwargs):
        self.CONFIG = config
        super().__init__(**kwargs)

    async def setup_hook(self):
        guild = discord.Object(id=self.CONFIG["GUILD_ID"])
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)


def create_bot(bot_type: str):
    CONFIG = load_bot_config(bot_type)

    configure_logging(
        bot_name=CONFIG["BOT_NAME"],
        base_dir=Path(__file__).parent.parent
    )

    logger = logging.getLogger(__name__)
    logger.info("🟢 Logging initialisé")

    from common.langManager import lang_manager
    lang_manager.configure(CONFIG)

    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    intents.guilds = True

    bot = MyBot(
        config=CONFIG,
        command_prefix="/",
        intents=intents,
        help_command=None,
    )

    return bot, CONFIG, logger
