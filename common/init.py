from common.imports import *
from common.config import load_bot_config
import logging
from discord.ext import commands

from common.loggingBot import getLogger
logger = getLogger("init.py")


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
    #logger = logging.getLogger(CONFIG["BOT_NAME"])
    logger = getLogger(CONFIG["BOT_NAME"])
    logging.basicConfig(level=logging.INFO)

    from .langManager import lang_manager
    lang_manager.configure(CONFIG)

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True

    bot = MyBot(
        config=CONFIG,
        command_prefix="/",
        intents=intents,
        help_command=None,
    )

    return bot, CONFIG, logger
