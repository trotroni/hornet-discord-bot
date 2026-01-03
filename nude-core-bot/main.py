from common.init import bot, CONFIG, logger
from common.langManager import lang_manager

@bot.event
async def on_ready():
    logger.info(f"✅ Bot connecté en tant que {bot.user}")
    try:
        lang_manager.load_languages()
    except Exception as e:
        logger.critical(f"Impossible de charger les langues : {e}")
        await bot.close()
        return

    # Charger commandes et autres setup si nécessaire
    logger.info("✅ Bot prêt")

if __name__ == "__main__":
    bot.run(CONFIG["TOKEN"])
