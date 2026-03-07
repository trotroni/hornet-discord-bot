# common/tickets.py

from common.storage import load_json, save_json, log_event
from common.utils_compta import now_iso

# CRÉATION DE TICKET
def create_ticket(
    ticket_id,
    type_ticket,
    createur_id,
    debiteurs,
    crediteur_id,
    montant_centimes,
    motif
):
    if montant_centimes <= 0:
        raise ValueError("Le montant doit être positif")

    tickets = load_json("tickets.json")

    if ticket_id in tickets:
        raise ValueError("ID de ticket déjà existant")

    tickets[ticket_id] = {
        "type": type_ticket,
        "createur_id": createur_id,
        "debiteurs": debiteurs,
        "crediteur_id": crediteur_id,
        "motif": motif,
        "montant_total": montant_centimes,
        "reste_du": montant_centimes,
        "date_creation": now_iso()
    }

    save_json("tickets.json", tickets)

    log_event({
        "timestamp": now_iso(),
        "event": "CREATE",
        "ticket_id": ticket_id,
        "montant": montant_centimes,
        "auteur_id": createur_id
    })

# REMBOURSEMENT
def rembourse(ticket_id, montant_centimes, auteur_id):
    if montant_centimes <= 0:
        raise ValueError("Montant invalide")

    tickets = load_json("tickets.json")

    if ticket_id not in tickets:
        raise ValueError("Ticket introuvable")

    ticket = tickets[ticket_id]

    if montant_centimes > ticket["reste_du"]:
        raise ValueError("Le montant dépasse la dette restante")

    ticket["reste_du"] -= montant_centimes

    log_event({
        "timestamp": now_iso(),
        "event": "REMBOURSE",
        "ticket_id": ticket_id,
        "montant": montant_centimes,
        "auteur_id": auteur_id
    })

    if ticket["reste_du"] == 0:
        close_ticket(ticket_id, auteur_id)
    else:
        save_json("tickets.json", tickets)

# CLÔTURE & ARCHIVAGE
def close_ticket(ticket_id, auteur_id):
    tickets = load_json("tickets.json")
    archives = load_json("archives.json")

    if ticket_id not in tickets:
        raise ValueError("Ticket introuvable")

    ticket = tickets.pop(ticket_id)
    ticket["date_cloture"] = now_iso()

    archives[ticket_id] = ticket

    save_json("tickets.json", tickets)
    save_json("archives.json", archives)

    log_event({
        "timestamp": now_iso(),
        "event": "CLOSE",
        "ticket_id": ticket_id,
        "auteur_id": auteur_id
    })

# CALCUL DU SOLDE
def calcul_solde(user_id):
    tickets = load_json("tickets.json")

    detail = {}
    total_doit = 0
    total_recoit = 0

    for ticket in tickets.values():
        for d in ticket["debiteurs"]:
            uid = d["user_id"]
            part = d["part"]
            if uid == user_id:
                total_doit += part
                detail.setdefault(ticket["crediteur_id"], {"doit": 0, "recoit": 0})
                detail[ticket["crediteur_id"]]["doit"] += part

        if ticket["crediteur_id"] == user_id:
            total_recoit += ticket["reste_du"]
            for d in ticket["debiteurs"]:
                uid = d["user_id"]
                part = d["part"]
                detail.setdefault(uid, {"doit": 0, "recoit": 0})
                detail[uid]["recoit"] += part

    return {
        "detail": detail,  # { user_id: {doit: X, recoit: Y}, ... }
        "doit": total_doit,
        "recoit": total_recoit,
        "solde": total_recoit - total_doit
    }