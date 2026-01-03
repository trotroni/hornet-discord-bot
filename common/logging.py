import logging
from pathlib import Path
from configuration import BOT_NAME

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logger():
    logger = logging.getLogger(BOT_NAME)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        f"[{BOT_NAME}] %(asctime)s | %(levelname)s | %(message)s"
    )

    fh = logging.FileHandler(LOG_DIR / f"{BOT_NAME}.log", encoding="utf-8")
    fh.setFormatter(formatter)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(sh)

    return logger
