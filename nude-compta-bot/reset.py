# nude-discord/nude-compta-bot/reset.py
# Script de réinitialisation des fichiers de données pour Nude Compta Bot

import json
from pathlib import Path

# Chemins des fichiers de données
DATA_DIR = Path(__file__).parent / "data"
ARCHIVES_FILE = DATA_DIR / "archives.json"
TICKETS_FILE = DATA_DIR / "tickets.json"
EVENTS_FILE = DATA_DIR / "events.log"


def reset_archives():
    """Réinitialise le fichier archives.json avec un objet vide"""
    try:
        with open(ARCHIVES_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        print(f"Archives réinitialisées: {ARCHIVES_FILE.name}")
        return True
    except Exception as e:
        print(f"Erreur lors de la réinitialisation de {ARCHIVES_FILE.name}: {e}")
        return False


def reset_tickets():
    """Réinitialise le fichier tickets.json avec un objet vide"""
    try:
        with open(TICKETS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        print(f"Tickets réinitialisés: {TICKETS_FILE.name}")
        return True
    except Exception as e:
        print(f"Erreur lors de la réinitialisation de {TICKETS_FILE.name}: {e}")
        return False


def reset_events():
    """Supprime toutes les lignes du fichier events.log"""
    try:
        with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
            f.write('')
        print(f"Events réinitialisés: {EVENTS_FILE.name}")
        return True
    except Exception as e:
        print(f"Erreur lors de la réinitialisation de {EVENTS_FILE.name}: {e}")
        return False


def reset():
    """Réinitialise tous les fichiers de données"""
    print("Réinitialisation de tous les fichiers de données...\n")

    results = []
    results.append(reset_archives())
    results.append(reset_tickets())
    results.append(reset_events())

    print()
    if all(results):
        print("Tous les fichiers ont été réinitialisés avec succès")
    else:
        print("Certains fichiers n'ont pas pu être réinitialisés")

    return all(results)


if __name__ == "__main__":
    import sys

    # Vérifier que le dossier data existe
    if not DATA_DIR.exists():
        print(f"Erreur: Le dossier 'data' n'existe pas: {DATA_DIR}")
        sys.exit(1)

    # Menu interactif
    print("=" * 50)
    print("SCRIPT DE RÉINITIALISATION")
    print("=" * 50)
    print("\nQue voulez-vous réinitialiser ?")
    print("1. archives.json")
    print("2. tickets.json")
    print("3. events.log")
    print("4. TOUT réinitialiser")
    print("0. Annuler")
    print()

    try:
        choice = input("Votre choix (0-4): ").strip()

        if choice == "1":
            confirm = input("\nConfirmer la réinitialisation de archives.json ? (oui/non): ")
            if confirm.lower() in ['oui', 'o', 'yes', 'y']:
                reset_archives()
            else:
                print("Annulé")

        elif choice == "2":
            confirm = input("\nConfirmer la réinitialisation de tickets.json ? (oui/non): ")
            if confirm.lower() in ['oui', 'o', 'yes', 'y']:
                reset_tickets()
            else:
                print("Annulé")

        elif choice == "3":
            confirm = input("\nConfirmer la réinitialisation de events.log ? (oui/non): ")
            if confirm.lower() in ['oui', 'o', 'yes', 'y']:
                reset_events()
            else:
                print("Annulé")

        elif choice == "4":
            confirm = input("\nATTENTION: Cela va réinitialiser TOUS les fichiers. Confirmer ? (oui/non): ")
            if confirm.lower() in ['oui', 'o', 'yes', 'y']:
                reset()
            else:
                print("Annulé")

        elif choice == "0":
            print("Annulé")

        else:
            print("Choix invalide")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nAnnulé par l'utilisateur")
        sys.exit(0)