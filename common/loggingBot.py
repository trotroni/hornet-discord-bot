# common/loggingBot.py

import logging
from pathlib import Path
from datetime import datetime

# Timestamp unique par process (donc par bot)
_SESSION = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

# Contexte global du process
_LOG_CONTEXT = {
    "bot": "UNKNOWN"
}


class BotContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.bot = _LOG_CONTEXT["bot"]
        return True


def configure_logging(bot_name: str, base_dir: Path) -> None:
    _LOG_CONTEXT["bot"] = bot_name

    # 📁 Dossier logs unique (SANS date)
    logs_dir = base_dir / "logs" / _SESSION.split("_")[0]
    logs_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Évite les doublons si relancé
    if root_logger.handlers:
        return

    formatter = logging.Formatter(
        "[%(filename)s] | %(bot)s | %(asctime)s | %(levelname)s | %(message)s"
    )

    # 📝 Date + heure DANS le nom du fichier
    log_file = logs_dir / f"{bot_name}_{_SESSION}.log"

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )
    stream_handler = logging.StreamHandler()

    for handler in (file_handler, stream_handler):
        handler.setFormatter(formatter)
        handler.addFilter(BotContextFilter())
        root_logger.addHandler(handler)