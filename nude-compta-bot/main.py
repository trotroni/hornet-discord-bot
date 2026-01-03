"""========================
# IMPORTS
# =========================
import discord
import os

from discord import app_commands, Embed, Interaction
from discord.ext import commands
from discord import AllowedMentions
from dotenv import load_dotenv
from datetime import datetime, UTC
from tickets import create_ticket, rembourse, calcul_solde, close_ticket
from utils import generate_ticket_id, cents_to_euros, euros_to_cents, embed_color
from storage import load_json

version = "v.0.0.0-test - 2025-12-23 - 16:30"
"""# IMPORTS
"""========================
# Chemins des fichiers
# =========================
BASE_DIR = Path(__file__).parent
COMMANDS_CSV = BASE_DIR / "commands.csv"
LOGS_DIR = BASE_DIR / "logs"
LANG_DIR = BASE_DIR.parent / "languages"
WARN_FILE = BASE_DIR / "warns.csv"

# Créer les dossiers/fichiers si nécessaires
LOGS_DIR.mkdir(exist_ok=True)
LANG_DIR.mkdir(exist_ok=True)
COMMANDS_CSV.touch(exist_ok=True)
WARN_FILE.touch(exist_ok=True)
"""# Chemins des fichiers
"""========================
# lancement chrono
# =========================
start = time.perf_counter()
"""# lancement chrono
"""========================
# LOGGING
# =========================
log_filename = LOGS_DIR / f"bot.{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("nude-compta-bot")
"""# LOGGING

"""========================
# CONFIGURATION ET INITIALISATION
# =========================
load_dotenv(dotenv_path="../var.env")

NUDE_COMPTA_TOKEN = os.getenv("NUDE_COMPTA_TOKEN")
GUILD_ID_STR = os.getenv("GUILD_ID")
GUILD_ID = int(GUILD_ID_STR)
guild_obj = discord.Object(id=GUILD_ID)
CHANNEL_ID_NOTIF = os.getenv("CHANNEL_ID_NOTIF")

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "fr")
EPHEMERAL_ENV = os.getenv("EPHEMERAL_ENV", "true").lower()
EPHEMERAL_GLOBAL = EPHEMERAL_ENV == "true"
VERSION = os.getenv("VERSION")

if not NUDE_COMPTA_TOKEN:
    logger.error("❌ NUDE_COMPTA_TOKEN manquant dans les fichiers .env")
    raise ValueError("❌ NUDE_COMPTA_TOKEN manquant dans les fichiers .env")
elif not GUILD_ID_STR:
    logger.error("❌ GUILD_ID_STR manquant dans les fichiers .env")
    raise ValueError("❌ GUILD_ID_STR manquant dans les fichiers .env")
    if not GUILD_ID:
        logger.error("❌ Échec de la convertion de GUILD_ID en 'int'")
        raise ValueError("❌ Échec de la convertion de GUILD_ID en 'int'")
        if guild_obj is None:
            logger.error("❌ GUILD_ID invalide, impossible de créer l'objet guild")
            raise ValueError("❌ GUILD_ID invalide, impossible de créer l'objet guild")
elif not CHANNEL_ID_NOTIF:
    logger.error("❌ CHANNEL_ID_NOTIF manquant dans les fichiers .env")
    raise ValueError("❌ CHANNEL_ID_NOTIF manquant dans les fichiers .env")

elif not DEFAULT_LANGUAGE:
    logger.error("❌ DEFAULT_LANGUAGE manquant dans les fichiers .env")
    raise ValueError("❌ DEFAULT_LANGUAGE manquant dans les fichiers .env")
elif EPHEMERAL_ENV not in ["true", "false"]:
    logger.error("❌ EPHEMERAL_ENV doit être 'true' ou 'false'") 
    raise ValueError("❌ EPHEMERAL_ENV doit être 'true' ou 'false'")

logger.info(f"✅ Configuration chargée: GUILD_ID={GUILD_ID}, CHANNEL_ID_NOTIF={CHANNEL_ID_NOTIF}, ADMIN_ROLE_ID={ADMIN_ROLE_ID}, DEFAULT_LANGUAGE={DEFAULT_LANGUAGE}, EPHEMERAL_GLOBAL={EPHEMERAL_GLOBAL}")

"""# CONFIGURATION ET INITIALISATION
"""========================
# GESTION DES LANGUES
# =========================
class LanguageManager:
    def __init__(self):
        self.translations = {}
        self.available_languages = []
        self.user_preferences = {}

    def load_languages(self):
        self.translations.clear()
        self.available_languages.clear()
        files = list(LANG_DIR.glob("*.json"))
        print("LANG_DIR =", LANG_DIR)
        print("Existe :", LANG_DIR.exists())
        print("Fichiers :", list(LANG_DIR.glob("*.json")))
        if not files:
            logger.error(f"❌ Aucun fichier de langue dans {LANG_DIR}")
            raise FileNotFoundError("Aucun fichier de traduction")
        for file in files:
            lang_code = file.stem
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
                    self.available_languages.append(lang_code)
                logger.info(f"✅ Langue chargée : {lang_code}")
            except Exception as e:
                logger.error(f"❌ Erreur chargement {file}: {e}")
        if not self.available_languages:
            raise ValueError("Aucune langue valide chargée")

    def get(self, key: str, user_id: int = None, **kwargs) -> str:
        lang = self.user_preferences.get(user_id, DEFAULT_LANGUAGE)
        if lang not in self.translations:
            lang = DEFAULT_LANGUAGE

        data = self.translations.get(lang, {})
        for part in key.split("."):
            if not isinstance(data, dict):
                return f"[{key}]"
            data = data.get(part)

        if data is None:
            return f"[{key}]"

        try:
            return data.format(**kwargs)
        except KeyError as e:
            logger.warning(f"⚠️ Variable manquante pour '{key}': {e}")
            return data

    def set_user_language(self, user_id: int, language: str) -> bool:
        if language in self.available_languages:
            self.user_preferences[user_id] = language
            return True
        return False

    def get_language_name(self, lang_code: str) -> str:
        return self.translations.get(lang_code, {}).get("language_name", lang_code)

lang_manager = LanguageManager()
"""# GESTION DES LANGUES
"""========================
# CONFIG BOT
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True
bot = commands.Bot(command_prefix="!", intents=INTENTS)
"""# INITIALISATION DU BOT

"""========================
# ON_READY
@bot.event
async def on_ready():
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print("Erreur : le bot n'a pas accès à la guild")
        return
    await bot.tree.sync(guild=guild)
    print(f"Bot connecté : {bot.user} - commandes synchronisées sur la guild {guild.name}")

    if CHANNEL_ID_NOTIF:
        channel = bot.get_channel(int(CHANNEL_ID_NOTIF))
        if channel:
            embed = discord.Embed(
                title=lang_manager.get("bot.online_title"),
                description=lang_manager.get("bot.online_description"),
                color=discord.Color.pink()
            )

            embed.add_field(name="Date", value=datetime.now().strftime("%Y-%m-%d"), inline=True)
            embed.add_field(name="Heure", value=datetime.now().strftime("%H:%M:%S"), inline=True)
            embed.add_field(name="Version", value=VERSION, inline=True)

            embed.set_footer(
                text=lang_manager.get(
                    "bot.online_footer",
                    end=time.perf_counter() - start
                )
            )

            await channel.send(embed=embed)
            logger.info(f"✅ Message de démarrage envoyé")
"""# ÉVÉNEMENTS
"""========================
# COMMANDES SLASH
# =========================
# /p2p_ticket
@bot.tree.command(name="p2p_ticket", description="Créer un ticket p2p", guild=guild_obj)
@app_commands.describe(debiteur="Utilisateur qui doit", crediteur="Utilisateur qui reçoit", montant="Montant en euros", motif="Motif de la dette")
async def p2p_ticket(interaction: discord.Interaction, debiteur: discord.Member, crediteur: discord.Member, montant: float, motif: str):
    await interaction.response.defer()
    if debiteur.id == crediteur.id:
        await interaction.response.followup.send("Un utilisateur ne peut pas se devoir à lui-même.", ephemeral=False)
        return
    if montant <= 0:
        await interaction.response.followup.send("Le montant doit être positif.", ephemeral=False)
        return

    montant_c = euros_to_cents(montant)
    ticket_id = generate_ticket_id("p2p")
    debiteurs = [{"user_id": str(debiteur.id), "part": montant_c}]

    try:
        create_ticket(ticket_id, "p2p", str(interaction.user.id), debiteurs, str(crediteur.id), montant_c, motif)
    except Exception as e:
        await interaction.response.followup.send(f"Erreur : {e}", ephemeral=False)
        return

    embed = discord.Embed(
        title=f"Nouveau ticket P2P ({ticket_id})",
        description=f"{debiteur.mention} doit `{montant:.2f}€` à {crediteur.mention}",
        color=embed_color("p2p")
    )
    embed.add_field(name="Motif", value=f"`{motif}`", inline=False)
        
    await interaction.response.followup.send(embed=embed,allowed_mentions=AllowedMentions(users=True))

# /split_ticket
@bot.tree.command(name="split_ticket", description="Créer un ticket avec plusieurs débiteurs", guild=guild_obj)
@app_commands.describe(debiteurs="Liste des utilisateurs TOTALES, le premier aura la part du cents en plus", crediteur="Utilisateur qui reçoit", montant="Montant total", motif="Motif de la dette")
async def split_ticket(interaction: discord.Interaction, debiteurs: str, crediteur: discord.Member, montant: float, motif: str):
    await interaction.response.defer()
    
    mentions = debiteurs.split()
    if not mentions:
        await interaction.response.followup.send(
            "Vous devez mentionner au moins un débiteur.",
            ephemeral=False
        )
        return

    if montant <= 0:
        await interaction.response.followup.send(
            "Le montant doit être positif.",
            ephemeral=False
        )
        return

    # Calcul en centimes
    montant_c = euros_to_cents(montant)
    nb = len(mentions)

    parts = montant_c // nb
    reste = montant_c - (parts * nb)

    debiteurs_list = []
    for idx, u in enumerate(mentions):
        user_id = u.strip("<@!>")
        part = parts + (reste if idx == 0 else 0)
        debiteurs_list.append({
            "user_id": user_id,
            "part": part
        })

    # Création du ticket
    ticket_id = generate_ticket_id("groupe")
    try:
        create_ticket(
            ticket_id,
            "groupe",
            str(interaction.user.id),
            debiteurs_list,
            str(crediteur.id),
            montant_c,
            motif
        )
    except Exception as e:
        await interaction.response.followup.send(
            f"Erreur : {e}",
            ephemeral=False
        )
        return

    # Préparation affichage
    part_base_e = parts / 100
    montant_total_e = montant_c / 100

    lignes = []

    # Si il y a un centime en trop, on sépare le premier
    if reste > 0:
        part_premier_e = (parts + reste) / 100
        premier = debiteurs_list[0]
        autres = debiteurs_list[1:]

        if premier["user_id"] != str(crediteur.id):
            lignes.append(
                f"<@{premier['user_id']}> doit `{part_premier_e:.2f}€` à {crediteur.mention}"
            )

        autres_valides = [
            d for d in autres if d["user_id"] != str(crediteur.id)
        ]
        if autres_valides:
            verbe = "doit" if len(autres_valides) == 1 else "doivent"
            mentions = ", ".join(f"<@{d['user_id']}>" for d in autres_valides)
            lignes.append(
                f"{mentions} {verbe} `{part_base_e:.2f}€` à {crediteur.mention}"
            )

    # Sinon, tout le monde paie le même montant → une seule ligne
    else:
        debiteurs_valides = [
            d for d in debiteurs_list if d["user_id"] != str(crediteur.id)
        ]
        if debiteurs_valides:
            verbe = "doit" if len(debiteurs_valides) == 1 else "doivent"
            mentions = ", ".join(f"<@{d['user_id']}>" for d in debiteurs_valides)
            lignes.append(
                f"{mentions} {verbe} `{part_base_e:.2f}€` à {crediteur.mention}"
            )

    description = "\n".join(lignes)
    
    # Embed
    embed = discord.Embed(
        title=f"Nouveau ticket groupe ({ticket_id})",
        description=description,
        color=embed_color("groupe"),
        timestamp=datetime.utcnow()
    )

    embed.add_field(
        name="Motif",
        value=f"`{motif}`",
        inline=False
    )

    embed.add_field(
        name="Total du ticket",
        value=f"`{montant_total_e:.2f}€`",
        inline=False
    )

    await interaction.followup.send(
        embed=embed,
        allowed_mentions=discord.AllowedMentions(users=True)
    )

# /rembourse
@bot.tree.command(name="rembourse", description="Rembourser un ticket", guild=guild_obj)
@app_commands.describe(ticket_id="ID du ticket", montant="Montant remboursé")
async def rembourse_cmd(interaction: discord.Interaction, ticket_id: str, montant: float):
    if montant <= 0:
        await interaction.response.send_message("Montant invalide.", ephemeral=False)
        return
    montant_c = euros_to_cents(montant)
    try:
        rembourse(ticket_id, montant_c, str(interaction.user.id))
    except Exception as e:
        await interaction.response.send_message(f"Erreur : {e}", ephemeral=False)
        return
    embed = discord.Embed(
        title=f"Remboursement sur {ticket_id}",
        description=f"Montant remboursé : {montant:.2f}€",
        color=embed_color("remboursement")
    )
    await interaction.response.send_message(embed=embed,allowed_mentions=AllowedMentions(users=True))

# /solde
@bot.tree.command(name="solde", description="Voir le solde d'un utilisateur", guild=guild_obj)
@app_commands.describe(utilisateur="Utilisateur (optionnel)")
async def solde(interaction: discord.Interaction, utilisateur: discord.Member | None = None):
    user = utilisateur or interaction.user
    s = calcul_solde(str(user.id))

    embed = discord.Embed(
        title=f"Solde de {user.display_name}",
        color=embed_color("solde")
    )

    if not s["detail"]:
        embed.description = "Aucune dette ou crédit."
    else:
        for uid, vals in s["detail"].items():
            # Récupère le membre en toute sécurité
            member = interaction.guild.get_member(int(uid))
            if not member:
                try:
                    member = await interaction.guild.fetch_member(int(uid))
                except discord.NotFound:
                    member = None

            # Nom lisible et mention si dispo
            display_name = member.display_name if member else f"Utilisateur ({uid})"
            mention = member.mention if member else f"<@{uid}>"

            # On met la mention dans le field.value pour qu'elle soit cliquable
            embed.add_field(
                name=display_name,
                value=(
                    f"{mention}\n"
                    f"Doit : {cents_to_euros(vals['doit'])}\n"
                    f"Reçoit : {cents_to_euros(vals['recoit'])}"
                ),
                inline=True
            )

    embed.add_field(
        name="Total net",
        value=cents_to_euros(s["solde"]),
        inline=False
    )

    await interaction.response.send_message(
        embed=embed,
        allowed_mentions=discord.AllowedMentions(users=True)
    )

# /debug
@bot.tree.command(name="debug",description="Liste tous les membres du serveur pour debug",guild=guild_obj)
async def debug_members(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("Cette commande doit être utilisée sur un serveur.", ephemeral=False)
        return

    guild = interaction.guild
    members = guild.members

    embed = discord.Embed(
        title=f"Membres du serveur {guild.name}",
        color=embed_color("debug")
    )

    if not members:
        embed.description = "Aucun membre trouvé. Vérifie que l'intent 'members' est activé."
    else:
        for m in members:
            embed.add_field(
                name=m.display_name,
                value=f"ID: {m.id}\nMention: {m.mention}",
                inline=False
            )
    embed.add_field(
        name="Code Version", 
        value=f"{version}\nGit : https://github.com/Trotroni/COMPTA", 
        inline=False
    )

    await interaction.response.send_message(embed=embed, ephemeral=False)

# /close_ticket
@bot.tree.command(name="close_ticket", description="Clore un ticket et archiver", guild=guild_obj)
@app_commands.describe(ticket_id="ID du ticket")
async def close_ticket_cmd(interaction: discord.Interaction, ticket_id: str):
    try:
        close_ticket(ticket_id, str(interaction.user.id))
    except Exception as e:
        await interaction.response.send_message(f"Erreur : {e}", ephemeral=False)
        return
    embed = discord.Embed(
        title=f"Ticket {ticket_id} fermé", 
        color=embed_color("close_ticket")
    )
    await interaction.response.send_message(embed=embed,allowed_mentions=AllowedMentions(users=True))

# /set
@bot.tree.command(name="set", description="Définir une dette", guild=guild_obj)
@app_commands.describe(debiteur="Utilisateur qui doit", crediteur="Utilisateur qui reçoit", montant="Montant", motif="Motif")
async def set_cmd(interaction: discord.Interaction, debiteur: discord.Member, crediteur: discord.Member, montant: float, motif: str):
    if montant <= 0:
        await interaction.response.send_message("Montant invalide.", ephemeral=False)
        return
    montant_c = euros_to_cents(montant)
    ticket_id = generate_ticket_id("p2p")
    try:
        create_ticket(ticket_id, "p2p", str(interaction.user.id), [{"user_id": str(debiteur.id), "part": montant_c}], str(crediteur.id), montant_c, motif)
    except Exception as e:
        await interaction.response.send_message(f"Erreur : {e}", ephemeral=False)
        return
    embed = discord.Embed(
        title=f"Dette définie ({ticket_id})",
        description=f"{debiteur.display_name} doit {montant:.2f}€ à {crediteur.display_name}",
        color=embed_color("set")
    )
    embed.add_field(name="Motif", value=motif, inline=False)
    await interaction.response.send_message(embed=embed,allowed_mentions=AllowedMentions(users=True))

# /historique
@bot.tree.command(name="historique", description="Liste complète des tickets d'un utilisateur", guild=guild_obj)
@app_commands.describe(utilisateur="Utilisateur concerné")
async def audit(interaction: discord.Interaction, utilisateur: discord.Member):
    tickets = load_json("tickets.json")
    embed = discord.Embed(
        title=f"Tickets de {utilisateur.display_name}", 
        color=embed_color("audit")
    )
    count = 0
    for tid, t in tickets.items():
        found = False
        for d in t["debiteurs"]:
            if d["user_id"] == str(utilisateur.id):
                found = True
        if t["crediteur_id"] == str(utilisateur.id):
            found = True
        if found:
            count += 1
            debs = ", ".join([f"<@{d['user_id']}>({cents_to_euros(d['part'])})" for d in t["debiteurs"]])
            embed.add_field(
                name=f"{tid} - {t['type']}",
                value=f"Debiteurs : {debs}\nCrediteur : <@{t['crediteur_id']}>\nReste : {cents_to_euros(t['reste_du'])}\nMotif : {t['motif']}",
                inline=False
            )
    if count == 0:
        embed.description = "Aucun ticket trouvé."
    await interaction.response.send_message(embed=embed,allowed_mentions=AllowedMentions(users=True))

# /earliest
@bot.tree.command(name="earliest", description="Liste le plus ancien ticket actif", guild=guild_obj)
async def earliest_tickets(interaction: Interaction):
    await interaction.response.defer()
    tickets = load_json("tickets.json")

    if not tickets:
        embed = Embed(
            title="Tickets Actifs",
            description="Aucun ticket actif.",
            color=embed_color("earliest")
        )
        await interaction.response.send_message(embed=embed,allowed_mentions=AllowedMentions(users=True))
        return

    for tid, t in tickets.items():
        deb_names = ",\n ".join([f"<@{d['user_id']}>" for d in t["debiteurs"]])
        montant_rest = t["reste_du"] / 100

        embed = Embed(
            title=f"Ticket {tid}",
            color=embed_color("earliest")
        )
        embed.add_field(name="Créateur", value=f"<@{t['createur_id']}>", inline=True)
        embed.add_field(name="Débiteur(s)", value=f"{deb_names}", inline=True)
        embed.add_field(name="Créditeur", value=f"<@{t['crediteur_id']}>", inline=True)
        embed.add_field(name="Montant restant", value=f"`{montant_rest:.2f}€`", inline=False)
        embed.add_field(name="Motif", value=f"`{t['motif']}`", inline=True)

      # view = View()
      # view.add_item(Button(label="Rembourser", style=discord.ButtonStyle.green, custom_id=f"remb_{tid}"))
      # view.add_item(Button(label="Fermer", style=discord.ButtonStyle.danger, custom_id=f"close_{tid}"))

    await interaction.followup.send(embed=embed, allowed_mentions=AllowedMentions(users=True))
"""# COMMANDES SLASH
"""========================
# LANCEMENT BOT
# =========================
bot.run(NUDE_COMPTA_TOKEN)
"""# LANCEMENT BOT