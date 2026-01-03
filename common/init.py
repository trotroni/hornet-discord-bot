from .imports import *
from .config import load_bot_config
import logging
from discord.ext import commands

# Charger config
CONFIG = load_bot_config("core")  # ou "compta"
logger = logging.getLogger(CONFIG["BOT_NAME"])

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Classe du bot
class MyBot(commands.Bot):
    async def setup_hook(self):
        guild = discord.Object(id=CONFIG["GUILD_ID"])
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

# Instanciation du bot
bot = MyBot(command_prefix="/", intents=intents)
