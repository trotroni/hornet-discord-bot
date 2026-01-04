from common.init import create_bot
from common.langManager import lang_manager

bot, CONFIG, logger = create_bot("core")

@bot.event
async def on_ready():
    logger.info(f"✅ Core bot connecté : {bot.user}")

    try:
        lang_manager.load_languages()
    except Exception as e:
        logger.critical(f"❌ Langues non chargées : {e}")
        await bot.close()
        return

    logger.info("✅ Core bot prêt")


if __name__ == "__main__":
    bot.run(CONFIG["TOKEN"])
