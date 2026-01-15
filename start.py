# start.py

import subprocess
import sys
from pathlib import Path
import time
import logging
from datetime import datetime

_SESSION = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

# Racine du projet
project_root = Path(__file__).parent

logs_dir = project_root / "logs" / _SESSION.split("_")[0]
logs_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="[start.py] | launcher | %(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            logs_dir / f"launcher_{_SESSION}.log",
            encoding="utf-8"
        ),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    logger.info("🚀 Démarrage des bots Discord...")

    processes = []

    try:
        # ===== BOT CORE =====
        logger.info("🤖 Démarrage du bot core...")
        core_process = subprocess.Popen(
            [sys.executable, "-m", "nude-core-bot.main"],
            cwd=str(project_root),
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        processes.append(("CoreBot", core_process))

        time.sleep(1)

        # ===== BOT COMPTA =====
        logger.info("💰 Démarrage du bot compta...")
        compta_process = subprocess.Popen(
            [sys.executable, "-m", "nude-compta-bot.main"],
            cwd=str(project_root),
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        processes.append(("ComptaBot", compta_process))

        logger.info("✅ Les deux bots sont lancés!")

        while True:
            for name, proc in processes:
                if proc.poll() is not None:
                    logger.error(f"⚠️  {name} s'est arrêté avec le code: {proc.returncode}")
                    raise KeyboardInterrupt
            time.sleep(1)

    except KeyboardInterrupt:
        logger.error("🛑 Arrêt des bots...")

        for name, proc in processes:
            if proc.poll() is None:
                logger.error(f"   Arrêt de {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.critical(f"   ⚠️  Forçage de l'arrêt de {name}...")
                    proc.kill()
                    proc.wait()

        logger.info("✅ Tous les bots sont arrêtés")

    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        logger.exception(e)

        for _, proc in processes:
            if proc.poll() is None:
                proc.terminate()
                proc.wait()

        sys.exit(1)


if __name__ == "__main__":
    main()
