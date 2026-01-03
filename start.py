# nude-discord/main.py

import subprocess
import sys
from pathlib import Path
import signal
import time

# Dossier racine du projet
project_root = Path(__file__).parent


def main():
    """Lance les deux bots Discord en tant que processus séparés"""
    print("🚀 Démarrage des bots Discord...")

    # Chemins vers les scripts principaux
    core_main = project_root / "nude-core-bot" / "main.py"
    compta_bot = project_root / "nude-compta-bot" / "main.py"

    # Vérifier que les fichiers existent
    if not core_main.exists():
        print(f"❌ Fichier introuvable: {core_main}")
        sys.exit(1)

    if not compta_bot.exists():
        print(f"❌ Fichier introuvable: {compta_bot}")
        sys.exit(1)

    # Lancer les bots en tant que processus séparés
    processes = []

    try:
        # Lancer le bot core
        print("🤖 Démarrage du bot core...")
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
        print("💰 Démarrage du bot compta...")
        compta_process = subprocess.Popen(
            [sys.executable, str(compta_bot)],
            cwd=str(project_root / "nude-compta-bot"),
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        processes.append(("ComptaBot", compta_process))

        print("\n✅ Les deux bots sont lancés!")
        print("   Appuie sur Ctrl+C pour arrêter\n")

        # Attendre que les processus se terminent
        while True:
            # Vérifier si un processus s'est arrêté
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n⚠️  {name} s'est arrêté avec le code: {proc.returncode}")
                    # Arrêter les autres processus
                    raise KeyboardInterrupt

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Arrêt des bots...")

        # Arrêter proprement tous les processus
        for name, proc in processes:
            if proc.poll() is None:  # Si le processus tourne encore
                print(f"   Arrêt de {name}...")
                proc.terminate()

                # Attendre 5 secondes max
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"   ⚠️  Forçage de l'arrêt de {name}...")
                    proc.kill()
                    proc.wait()

        print("✅ Tous les bots sont arrêtés")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

        # Arrêter tous les processus en cas d'erreur
        for name, proc in processes:
            if proc.poll() is None:
                proc.terminate()
                proc.wait()

        sys.exit(1)


if __name__ == "__main__":
    main()