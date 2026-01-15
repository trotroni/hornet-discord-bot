# nude-core-bot/main.py
from common.imports import *
from common.init import create_bot
from common.langManager import lang_manager
from common.utils import command_log, date_now

### config
bot, CONFIG, logger = create_bot("core")
guild_obj = discord.Object(id=CONFIG["GUILD_ID"])
START_TIME = date_now()

@bot.event
async def on_ready():
    logger.info(f"✅ Core bot connecté : {bot.user}")

    try:
        lang_manager.load_languages()
    except Exception as e:
        logger.critical(f"❌ Langues non chargées : {e}")
        await bot.close()
        return

    logger.info("✅ Core bot prêt")

# config translation
t = lang_manager.translation_key

### correction auto
async def on_message(message: discord.Message):
    # reponse auto
    if message.author == bot.user:
        return

    content = message.content.lower()

    corrections = {
        "salut bot": "Salut ! Comment puis-je t'aider aujourd'hui ?",
        "aide moi": "Bien sûr ! Que puis-je faire pour toi ?",
        "merci bot": "De rien ! N'hésite pas si tu as d'autres questions.",
    }

    for trigger, response in corrections.items():
        if trigger in content:
            await message.channel.send(response)
            logger.info(f"Correction automatique appliquée pour {message.author} dans le message : {message.content}")
            break



### COMMANDES SLASH

# /ping
@bot.tree.command(name="ping", description=t("Teste la réactivité du bot"))
async def ping(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    embed = discord.Embed(
        title=t("core.ping.response"),
        color=discord.Color.pink()
    )
    embed.timestamp = date_now()
    await interaction.response.send_message(embed=embed, ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

# /stat
@bot.tree.command(name="stat", description="Stat sur le bot")
async def info(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    # Membres locaux
    guild = interaction.guild
    if guild is None:
        users_list_chunks = ["Commande utilisable uniquement dans un serveur"]
    else:
        members = sorted([member.mention for member in guild.members])
        # On découpe en chunks de 1000 caractères pour ne pas dépasser la limite
        users_list_chunks = []
        chunk = ""
        for m in members:
            if len(chunk) + len(m) + 2 > 1000:  # +2 pour ", "
                users_list_chunks.append(chunk.rstrip(", "))
                chunk = ""
            chunk += m + ", "
        if chunk:
            users_list_chunks.append(chunk.rstrip(", "))

    # Serveurs
    servers_list = ", ".join(f"`{g.name}`" for g in bot.guilds)
    servers_count = len(bot.guilds)

    # Version
    version = CONFIG["VERSION"]

    # Uptime
    delta = date_now() - START_TIME
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    uptime_str = f"{days}j {hours}h {minutes}m"

    # Création de embed
    embed = discord.Embed(
        title=t("core.stat.title"),
        color=discord.Color.pink()
    )

    # Membres locaux
    for i, chunk in enumerate(users_list_chunks):
        embed.add_field(
            name = t("core.stat.members", member_count = interaction.guild.member_count),
            value=chunk,
            inline=False
        )

    embed.add_field(
        name=t("core.stat.servers", servers_count = servers_count),
        value=servers_list,
        inline=False
    )
    embed.add_field(
        name=t("core.stat.version"),
        value=f"`{version}`",
        inline=True
    )
    embed.add_field(
        name=t("core.stat.uptime"),
        value=f"`{uptime_str}`",
        inline=True
    )

    embed.timestamp = date_now()

    await interaction.followup.send(
        embed=embed,
        ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
    )

    embed = discord.Embed(
        title="Il se peut que certaines fonctionnalités soient encore en cours de développement.",
        color=discord.Color.yellow()
    )

    embed.add_field(
        name="Le bot peut être instable ou comporter des bugs.",
        #value=f"`{version}`",
        inline=True
    )
    await interaction.followup.send(
        embed=embed,
        ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
    )

# /help
@bot.tree.command(name="help", description="Affiche toutes les commandes disponibles")
async def help(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    embed = discord.Embed(
        title=t("core.general.travaux"),
        color=discord.Color.yellow()
    )
    embed.timestamp = date_now()
    await interaction.response.send_message(embed=embed, ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
"""async def help_command(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    embed = discord.Embed(title=t("help_title", interaction), color=discord.Color.blue())
    embed.add_field(name=t("help_system", interaction),
                    value=f"🟢 `/ping`\n🟡 `/reboot`\n🟡 `/upgrade`\n🟡 `/bot.update`",
                    inline=False)
    embed.add_field(name=t("help_csv", interaction),
                    value=f"🟢 `/create`\n🟢 `/modif`\n🟢 `/delete`\n🟢 `/list`\n🟢 `/reload_commands`",
                    inline=False)
    embed.add_field(name="⚠️ Modération",
                    value=f"🟠 `/warn`\n🟠 `/warns`\n🟠 `/unwarn`",
                    inline=False)
    embed.add_field(name="📜 Logs",
                    value=f"🔵 `/logs`\n🔵 `/systemlog`",
                    inline=False)
    embed.add_field(name=t("help_lang", interaction),
                    value=f"🟢 `/language`", inline=False)
    embed.set_footer(text=t("help_footer", interaction))
    embed.timestamp = date_now()
    await interaction.response.send_message(embed=embed, ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)
"""

# /language
@bot.tree.command(name="language", description="Change la langue du bot")
@app_commands.describe(lang="Code de la langue (ex: fr, en)")
async def language_command(interaction: discord.Interaction, lang: str = None):
    # Log de la commande
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)

    # Création de l'embed
    embed = discord.Embed(color=discord.Color.blue())

    # Si aucune langue n'est fournie → afficher état actuel + liste
    if lang is None:
        current_lang = lang_manager.user_preferences.get(interaction.user.id, CONFIG["DEFAULT_LANGUAGE"])

        embed.title = t("core.language.title")
        embed.description = t("core.language.current", language = current_lang) + "\n\n"
        embed.description += t("core.language.available") + "\n"

        # Liste des langues disponibles
        for code in sorted(lang_manager.available_languages):
            # si available_languages est un dict {code: nom_lisible}
            lang_name = lang_manager.available_languages.get(code, code) if isinstance(lang_manager.available_languages, dict) else code
            embed.description += f"• `{code}` - {lang_name}\n"

        embed.set_footer(text=t("core.language.usage"))
        embed.timestamp = date_now()
        await interaction.response.send_message(embed=embed, ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    # Si une langue est fournie → tenter de changer
    else:
        lang = lang.lower().strip()
        if lang_manager.set_user_language(interaction.user.id, lang):
            # succès
            lang_name = lang_manager.available_languages.get(lang, lang) if isinstance(lang_manager.available_languages, dict) else lang
            embed.title = t("core.language.title")
            embed.description = t("core.language.changed", language = lang_name)
            embed.color = discord.Color.green()
        else:
            # échec
            embed.title = t("core.language.title")
            embed.description = t("core.language.invalid", lang = lang)
            embed.color = discord.Color.red()

        embed.timestamp = date_now()
        await interaction.response.send_message(embed=embed, ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

# /list
@bot.tree.command(name="list", description="Liste toutes les commandes personnalisées")
async def list_commands(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    if not custom_commands:
        await interaction.response.send_message(t("list_empty", interaction), ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)
        return
    embed = discord.Embed(title=t("list_title", interaction), color=discord.Color.green())
    embed.description = "\n".join([f"• `/{name}`" for name in sorted(custom_commands.keys())])
    embed.set_footer(text=t("list_footer", interaction, count=len(custom_commands)))
    embed.timestamp = date_now()
    await interaction.response.send_message(embed=embed, ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)

# /create
@bot.tree.command(name="create", description="Crée une nouvelle commande personnalisée")
@app_commands.describe(name="Nom de la commande", response="Réponse du bot")
async def create_command(interaction: discord.Interaction, name: str, response: str):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    name_lower = name.lower().strip()

    if name_lower in custom_commands:
        await interaction.response.send_message(
            t(
                "create_exists",
                interaction,
                name=name_lower
            ),
            ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
        )
        return
    custom_commands[name_lower] = response.strip()
    if save_custom_commands():
        await interaction.response.send_message(
            t(
                "create_success",
                interaction,
                name=name_lower
            ),
            ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
        )
    else:
        await interaction.response.send_message(
            t(
                "create_error",
                interaction
            ),
            ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
        )

# /modif
@bot.tree.command(name="modif", description="Modifie le nom et/ou la réponse d'une commande personnalisée")
@app_commands.describe(
    old_name="Nom actuel de la commande à modifier",
    new_name="Nouveau nom de la commande (optionnel)",
    new_response="Nouvelle réponse du bot (optionnel)"
)
async def modify_command(
    interaction: discord.Interaction,
    old_name: str,
    new_name: Optional[str] = None,
    new_response: Optional[str] = None
):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    old_name_lower = old_name.lower().strip()

    # Vérifie si la commande existe
    if old_name_lower not in custom_commands:
        await interaction.response.send_message(
            t("modif_not_found", interaction, name=old_name_lower),
            ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
        )
        return

    # Aucun changement fourni
    if not new_name and not new_response:
        await interaction.response.send_message(
            t("modif_no_change", interaction, name=old_name_lower),
            ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
        )
        return

    # Sauvegarde de la commande originale
    old_response = custom_commands[old_name_lower]
    success = False

    try:
        # Si un nouveau nom est fourni
        if new_name:
            new_name_lower = new_name.lower().strip()
            # Empêche d'écraser une autre commande existante
            if new_name_lower != old_name_lower and new_name_lower in custom_commands:
                await interaction.response.send_message(
                    t("modif_name_exists", interaction, name=new_name_lower),
                    ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
                )
                return
            # Déplace la commande
            custom_commands[new_name_lower] = custom_commands.pop(old_name_lower)
            old_name_lower = new_name_lower  # met à jour la clé

        # Si une nouvelle réponse est donnée
        if new_response:
            custom_commands[old_name_lower] = new_response.strip()

        # Sauvegarde
        success = save_custom_commands()

    except Exception as e:
        logger.error(f"Erreur lors de la modification d'une commande : {e}")
        success = False

    if success:
        await interaction.response.send_message(
            t("modif_success", interaction, name=old_name_lower),
            ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
        )
    else:
        await interaction.response.send_message(
            t("modif_error", interaction, name=old_name_lower),
            ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
        )

# /delete
@bot.tree.command(name="delete", description="Supprime une commande personnalisée existante")
@app_commands.describe(name="Nom de la commande à supprimer")
async def delete_command(interaction: discord.Interaction, name: str):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    name_lower = name.lower().strip()

    # Vérifie si la commande existe
    if name_lower not in custom_commands:
        await interaction.response.send_message(
            t("delete_not_found", interaction, name=name_lower),
            ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
        )
        return

    # Supprime la commande
    try:
        del custom_commands[name_lower]

        # Sauvegarde les changements
        if save_custom_commands():
            await interaction.response.send_message(
                t("delete_success", interaction, name=name_lower),
                ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
            )
        else:
            await interaction.response.send_message(
                t("delete_error", interaction, name=name_lower),
                ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
            )

    except Exception as e:
        logger.error(f"Erreur lors de la suppression d'une commande : {e}")
        await interaction.response.send_message(
            t("delete_exception", interaction, name=name_lower),
            ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
        )

# /warn
@bot.tree.command(name="warn", description="Met un warn à un utilisateur")
@app_commands.describe(user="Utilisateur", reason="Raison")
async def warn_command(interaction: discord.Interaction, user: discord.Member, reason: str):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)

    if not is_admin(interaction):
        await interaction.response.send_message(
            t("permission_denied", interaction),
            ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
        )
        return

    uid = user.id
    warns_data.setdefault(uid, {"count": 0, "reasons": []})
    warns_data[uid]["count"] += 1
    warns_data[uid]["reasons"].append(reason)
    save_warns(warns_data)

    await interaction.response.send_message(
        f"{user.mention} reçoit un warn ({reason}). Total: {warns_data[uid]['count']}",
        ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
    )

    if warns_data[uid]["count"] >= WARN_LIMIT:
        await interaction.channel.send(f"{user.mention} kick temporaire ({KICK_DURATION}s)")
        try:
            # CORRECTION: Utiliser datetime.now(timezone.utc) au lieu de utcnow()
            timeout_until = datetime.now(timezone.utc) + timedelta(seconds=KICK_DURATION)
            await user.edit(timed_out_until=timeout_until)
        except Exception as e:
            logger.error(f"Erreur kick temporaire: {e}")

# /warns
@bot.tree.command(name="warns", description="Voir warns utilisateur")
@app_commands.describe(user="Utilisateur")
async def warns_check(interaction: discord.Interaction, user: discord.Member):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    uid = user.id
    data = warns_data.get(uid)
    if not data:
        await interaction.response.send_message(f"{user.mention} n'a aucun warn.", ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)
        return
    msg = f"Warns pour {user.mention} :\n"
    for i, reason in enumerate(data["reasons"], start=1):
        msg += f"{i}. {reason}\n"
    await interaction.response.send_message(msg, ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)

# /unwarn
@bot.tree.command(name="unwarn", description="Supprime un warn d'un utilisateur")
@app_commands.describe(user="Utilisateur", number="Numéro du warn à supprimer (optionnel)")
async def unwarn_command(interaction: discord.Interaction, user: discord.Member, number: int = None):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    if not is_admin(interaction):
        await interaction.response.send_message("permission_denied", ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)
        return
    uid = user.id
    data = warns_data.get(uid)
    if not data or data["count"] == 0:
        await interaction.response.send_message(f"{user.mention} n'a aucun warn.", ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)
        return
    if number is None:
        removed_reason = data["reasons"].pop()
        data["count"] -= 1
        action = f"Le dernier warn a été supprimé : {removed_reason}"
    else:
        if number < 1 or number > data["count"]:
            await interaction.response.send_message(f"Numéro de warn invalide. Total: {data['count']}", ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)
            return
        removed_reason = data["reasons"].pop(number - 1)
        data["count"] -= 1
        action = f"Le warn #{number} a été supprimé : {removed_reason}"
    if data["count"] == 0:
        warns_data.pop(uid)
    else:
        warns_data[uid] = data
    save_warns(warns_data)
    await interaction.response.send_message(f"{user.mention} - {action}", ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)

#a finir
# /report
@bot.tree.command(name="report", description="Signale un groupe de message au staff")
@app_commands.describe(nombre="Nombre de messages à signaler (10-50)", reason="Raison du signalement")
async def report_command(interaction: discord.Interaction, nombre: int, reason: str):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.send_message(
        "🚧 Fonctionnalité en construction.",
        ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
    )

# /logs
@bot.tree.command(name="logs", description="Affiche les derniers logs du bot")
async def logs_command(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    try:
        log_files = sorted(LOGS_DIR.glob("bot.*.log"), reverse=True)
        if not log_files:
            await interaction.followup.send("❌ Aucun fichier de log trouvé.", ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)
            return
        latest_file = log_files[0]
        content = latest_file.read_text(encoding="utf-8")[-1900:]
        embed = discord.Embed(title=f"📜 Logs Bot ({latest_file.name})",
                              description=f"```{content}```",
                              color=discord.Color.green())
        await interaction.followup.send(embed=embed, ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur lecture logs: {e}", ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)

# /reboot
@bot.tree.command(name="reboot", description="Redémarre le bot")
async def reboot_command(interaction: discord.Interaction):
    cmd_user = interaction.user
    cmd_name = interaction.command.name
    logger.info(f"L'utilisateur {cmd_user} a exécuté la commande {cmd_name}")

    if not is_admin(interaction):
        await interaction.response.send_message(
            t("permission_denied", interaction),
            ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
        )
        return

    await interaction.response.send_message(
        "🔄 Redémarrage du bot...",
        ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
    )

    logger.info("🔄 Redémarrage demandé par %s", interaction.user)
    await bot.close()
    os.execv(sys.executable, [sys.executable] + sys.argv)

@bot.tree.command(name="upgrade", description="Met à jour le bot depuis Git")
async def upgrade_command(interaction: discord.Interaction):
    cmd_user = interaction.user
    cmd_name = interaction.command.name
    logger.info(f"L'utilisateur {cmd_user} a exécuté la commande {cmd_name}")

    if not is_admin(interaction):
        await interaction.response.send_message(
            t("permission_denied", interaction),
            ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
        )
        return  # Ce return est correct ici

    # Code exécuté seulement si admin
    await interaction.response.send_message(
        "⬆️ Mise à jour du bot en cours...",
        ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
    )
    logger.info("⬆️ Mise à jour demandée par %s", interaction.user)

    try:
        result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        output = result.stdout + "\n" + result.stderr
        logger.info("Git pull output:\n%s", output)
        await bot.close()
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour: {e}")
        await interaction.followup.send(
            f"❌ Erreur mise à jour: {e}",
            ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
        )

# ----------- Test -----------
@bot.tree.command(name="test", description="Commande de test")
async def test_command(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    embed = discord.Embed(
        title=t("core.info.test"),
        color=discord.Color.pink()
    )
    embed.timestamp = date_now()
    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    bot.run(CONFIG["TOKEN"])
