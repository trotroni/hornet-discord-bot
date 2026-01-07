import logging
from pathlib import Path
from datetime import datetime

SESSION_DATE = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Dossier de logs global
BASE_LOG_DIR = Path("logs")
BASE_LOG_DIR.mkdir(exist_ok=True)

# Dossier de session
SESSION_LOG_DIR = BASE_LOG_DIR / SESSION_DATE
SESSION_LOG_DIR.mkdir(exist_ok=True)


def getLogger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    # Évite les doublons
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        f"[{name}] | %(asctime)s | %(levelname)s | %(message)s"
    )

    # Fichier de log dans le dossier de session
    log_file = SESSION_LOG_DIR / f"{name}_{SESSION_DATE}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Log console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
