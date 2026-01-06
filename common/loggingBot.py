# common/loggingBot.py
import logging
from pathlib import Path
from datetime import datetime

def getLogger(name: str):
    LOG_DIR = Path("logs")
    LOG_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger  # éviter doublons

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(f"[{name}] %(asctime)s | %(levelname)s | %(message)s")

    log_file = LOG_DIR / f"{name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(formatter)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger
