# start.py

import subprocess
import sys
from pathlib import Path
import signal
import time
import logging
from datetime import datetime

_SESSION = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

# Dossier racine du projet
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
    """Lance les deux bots Discord en tant que processus séparés"""
    logger.info("🚀 Démarrage des bots Discord...")

    # Chemins vers les scripts principaux
    core_main = project_root / "nude-core-bot" / "main.py"
    compta_bot = project_root / "nude-compta-bot" / "main.py"

    # Vérifier que les fichiers existent
    if not core_main.exists():
        logger.critical(f"❌ Fichier introuvable: {core_main}")
        sys.exit(1)

    if not compta_bot.exists():
        logger.critical(f"❌ Fichier introuvable: {compta_bot}")
        sys.exit(1)

    # Lancer les bots en tant que processus séparés
    processes = []

    try:
        # Lancer le bot core
        logger.info("🤖 Démarrage du bot core...")
        core_process = subprocess.Popen(
            [sys.executable, str(core_main)],
            cwd=str(project_root / "nude-core-bot"),
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        processes.append(("CoreBot", core_process))

        # Petit délai pour éviter les conflits de démarrage
        time.sleep(1)

        # Lancer le bot compta
        logger.info("💰 Démarrage du bot compta...")
        compta_process = subprocess.Popen(
            [sys.executable, str(compta_bot)],
            cwd=str(project_root / "nude-compta-bot"),
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        processes.append(("ComptaBot", compta_process))

        logger.info("✅ Les deux bots sont lancés!")

        # Attendre que les processus se terminent
        while True:
            # Vérifier si un processus s'est arrêté
            for name, proc in processes:
                if proc.poll() is not None:
                    logger.error(f"⚠️  {name} s'est arrêté avec le code: {proc.returncode}")
                    # Arrêter les autres processus
                    raise KeyboardInterrupt

            time.sleep(1)

    except KeyboardInterrupt:
        logger.error("🛑 Arrêt des bots...")

        # Arrêter proprement tous les processus
        for name, proc in processes:
            if proc.poll() is None:  # Si le processus tourne encore
                logger.error(f"   Arrêt de {name}...")
                proc.terminate()

                # Attendre 5 secondes max
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

        # Arrêter tous les processus en cas d'erreur
        for name, proc in processes:
            if proc.poll() is None:
                proc.terminate()
                proc.wait()

        sys.exit(1)


if __name__ == "__main__":
    main()