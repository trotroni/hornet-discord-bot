# nude-core-bot/main.py
from common.imports import *
from common.init import create_bot
from common.langManager import lang_manager
from common.utils import command_log, date_now, send_with_warning, get_cpu_temperature, cpu_temp_verification, custom_commands, save_custom_commands, load_custom_commands


### config
bot, CONFIG, logger = create_bot("core")
guild_obj = discord.Object(id=CONFIG["GUILD_ID"])
START_TIME = date_now()
load_custom_commands()


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
    """

    channel = bot.get_channel(1417564003760082978)

    if channel is None:
        print("❌ Channel général introuvable")
        return

    embed = discord.Embed(
        title="C'est bon !",
        description="J'en ai marre !",
        color=discord.Color.green()
    )
    embed.timestamp = discord.utils.utcnow()

    await channel.send(embed=embed)
    
    if not cpu_temp_task.is_running():
        cpu_temp_task.start()
        logger.info("🧠 Task CPU démarrée")
    else:
        logger.warning("⚠️ Task CPU déjà en cours")
"""
# config translation
t = lang_manager.translation_key

### correction auto
@bot.event
async def on_message(message: discord.Message):
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

# -------------- TÂCHES PÉRIODIQUES --------------
"""
# mesure température CPU
@tasks.loop(minutes=3)
async def cpu_temp_task():
    temp = get_cpu_temperature()
    status = cpu_temp_verification(temp)

    if temp < 50:
        title = "✅ Température CPU normale"
        desc = "Tout est OK."
        color = discord.Color.green()

    elif temp < 65:
        title = "🌡 Température CPU"
        desc = f"Température : `{temp}°C`\nÉtat : `{status}`"
        color = discord.Color.yellow()

    elif temp < 70:
        title = "⚠️ Alerte Température CPU"
        desc = (
            f"Température élevée : `{temp}°C`\n"
            "Vérifiez le refroidissement."
        )
        color = discord.Color.orange()

    else:
        title = "🚨 TEMPÉRATURE CRITIQUE"
        desc = (
            f"Température critique : `{temp}°C`\n"
            "**Arrêt du bot recommandé !**"
        )
        color = discord.Color.red()

    channel = bot.get_channel(CONFIG["NERD_CHANNEL_ID"])
    if not channel:
        logger.error("❌ Channel CPU introuvable")
        return

    embed = discord.Embed(title=title, description=desc, color=color)
    embed.timestamp = discord.utils.utcnow()

    await channel.send(embed=embed)
"""

"""
@tasks.loop(minutes=1)
async def cpu_temp_task():
    temp_raw = get_cpu_temperature()  # peut renvoyer "N/A" ou un string
    try:
        temp = float(temp_raw.replace("°C", "").strip())
    except (ValueError, TypeError):
        temp = None

    status = cpu_temp_verification(temp) if temp is not None else "⚪ Inconnu"

    # Définition des titres, descriptions et couleurs selon température
    if temp is None:
        title = "❌ Température CPU inconnue"
        desc = f"Impossible de lire la température\nÉtat : `{status}`"
        color = discord.Color.red()
    elif temp < 50:
        title = "✅ Température CPU normale"
        desc = f"Température : `{temp}°C`\nÉtat : `{status}`"
        color = discord.Color.green()
    elif temp < 65:
        title = "🌡 Température CPU élevée"
        desc = f"Température : `{temp}°C`\nÉtat : `{status}`"
        color = discord.Color.yellow()
    elif temp < 75:
        title = "⚠️ Température CPU critique"
        desc = f"Température : `{temp}°C`\nVérifiez le refroidissement."
        color = discord.Color.orange()
    else:
        title = "🚨 TEMPÉRATURE CRITIQUE"
        desc = f"Température : `{temp}°C`\n**Arrêt recommandé !**"
        color = discord.Color.red()

    # Récupération du channel via la config
    channel_id = CONFIG.get("NOTIF_CHANNEL_ID")  # ou NOTIF_CHANNEL_ID si tu préfères
    if not channel_id:
        logger.error("❌ Channel CPU introuvable : NERD_CHANNEL_ID non défini")
        return

    try:
        channel = bot.get_channel(int(channel_id))
    except Exception:
        channel = None

    if not channel:
        logger.error("❌ Channel CPU introuvable : le bot n'a pas accès ou ID incorrect")
        return

    # Création de l'embed
    embed = discord.Embed(title=title, description=desc, color=color)
    embed.set_footer(text="Monitoring CPU")
    embed.timestamp = discord.utils.utcnow()

    # Envoi de l'embed
    await channel.send(embed=embed)
    logger.info(f"✅ Embed CPU envoyé : {title} | Temp: {temp_raw}")

# --- AVANT LE LANCEMENT DU TASK ---
@cpu_temp_task.before_loop
async def before_cpu_task():
    await bot.wait_until_ready()
"""
# ---------------- COMMANDES SLASH ----------------

# /ping
@bot.tree.command(name="biere", description="Teste l'alcoolémie du bot")
async def ping(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    embed = discord.Embed(title=t("core.ping.response"), color=discord.Color.pink())
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])


# /stat
@bot.tree.command(name="stat", description="Stat sur le bot")
async def info(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    guild = interaction.guild
    if guild is None:
        users_list_chunks = ["Commande utilisable uniquement dans un serveur"]
    else:
        members = sorted([member.mention for member in guild.members])
        users_list_chunks = []
        chunk = ""
        for m in members:
            if len(chunk) + len(m) + 2 > 1000:
                users_list_chunks.append(chunk.rstrip(", "))
                chunk = ""
            chunk += m + ", "
        if chunk:
            users_list_chunks.append(chunk.rstrip(", "))

    servers_list = ", ".join(f"`{g.name}`" for g in bot.guilds)
    servers_count = len(bot.guilds)

    version = CONFIG["VERSION"]
    delta = date_now() - START_TIME
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    uptime_str = f"{days}j {hours}h {minutes}m"

    embed = discord.Embed(title=t("core.stat.title"), color=discord.Color.pink())
    for chunk in users_list_chunks:
        embed.add_field(name=t("core.stat.members", member_count=interaction.guild.member_count),
                        value=chunk, inline=False)
    embed.add_field(name=t("core.stat.servers", servers_count=servers_count), value=servers_list, inline=False)
    embed.add_field(name=t("core.stat.version"), value=f"`{version}`", inline=True)
    embed.add_field(name=t("core.stat.uptime"), value=f"`{uptime_str}`", inline=True)

    cpu_temp_str = get_cpu_temperature()
    try:
        cpu_temp = float(cpu_temp_str.replace("'C", ""))
        status = cpu_temp_verification(cpu_temp)
        value = f"`{cpu_temp:.1f}°C` — `{status}`"
    except (ValueError, TypeError):
        value = "`N/A` — ⚪ Inconnu"

    embed.add_field(
        name=t("core.stat.cpu_temp"),
        value=value,
        inline=True
    )

    embed.timestamp = date_now()

    await send_with_warning(interaction, embeds=[embed])


# /help
@bot.tree.command(name="help", description="Affiche toutes les commandes disponibles")
async def help_command(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    embed = discord.Embed(title=t("core.help_title", interaction), color=discord.Color.blue())
    embed.add_field(name=t("core.help.system", interaction),
                    value="🟢 `/ping`\n🟡 `/reboot`\n🟡 `/upgrade`\n🟡 `/bot.update`", inline=False)
    embed.add_field(name=t("core.help.csv", interaction),
                    value="🟢 `/create`\n🟢 `/modif`\n🟢 `/delete`\n🟢 `/list`\n🟢 `/reload_commands`", inline=False)
    embed.add_field(name="⚠️ Modération",
                    value="🟠 `/warn`\n🟠 `/warns`\n🟠 `/unwarn`", inline=False)
    embed.add_field(name="📜 Logs",
                    value="🔵 `/logs`\n🔵 `/systemlog`", inline=False)
    embed.add_field(name=t("core.help.lang", interaction), value="🟢 `/language`", inline=False)
    embed.set_footer(text=t("core.help.footer", interaction))
    embed.timestamp = date_now()

    await send_with_warning(interaction, embeds=[embed])


# /language
@bot.tree.command(name="language", description="Change la langue du bot")
@app_commands.describe(lang="Code de la langue (ex: fr, en)")
async def language_command(interaction: discord.Interaction, lang: str = None):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    embed = discord.Embed(color=discord.Color.blue())
    if lang is None:
        current_lang = lang_manager.user_preferences.get(interaction.user.id, CONFIG["DEFAULT_LANGUAGE"])
        embed.title = t("core.language.title")
        embed.description = t("core.language.current", language=current_lang) + "\n\n" + t("core.language.available") + "\n"
        for code in sorted(lang_manager.available_languages):
            lang_name = lang_manager.available_languages.get(code, code) if isinstance(lang_manager.available_languages, dict) else code
            embed.description += f"• `{code}` - {lang_name}\n"
        embed.set_footer(text=t("core.language.usage"))
    else:
        lang = lang.lower().strip()
        if lang_manager.set_user_language(interaction.user.id, lang):
            lang_name = lang_manager.available_languages.get(lang, lang) if isinstance(lang_manager.available_languages, dict) else lang
            embed.title = t("core.language.title")
            embed.description = t("core.language.changed", language=lang_name)
            embed.color = discord.Color.green()
        else:
            embed.title = t("core.language.title")
            embed.description = t("core.language.invalid", lang=lang)
            embed.color = discord.Color.red()

    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])


# /list
@bot.tree.command(name="list", description="Liste toutes les commandes personnalisées")
async def list_commands(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    embed = discord.Embed(title=t("core.list.title", interaction), color=discord.Color.green())
    if not custom_commands:
        embed.description = t("core.list.empty", interaction)
    else:
        embed.description = "\n".join([f"• `/{name}`" for name in sorted(custom_commands.keys())])
    embed.set_footer(text=t("core.list.footer", interaction, count=len(custom_commands)))
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])


# /create
@bot.tree.command(name="create", description="Crée une nouvelle commande personnalisée")
@app_commands.describe(name="Nom de la commande", response="Réponse du bot")
async def create_command(interaction: discord.Interaction, name: str, response: str):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    embed = discord.Embed(color=discord.Color.blue())
    name_lower = name.lower().strip()
    if name_lower in custom_commands:
        embed.title = "Commande existante"
        embed.description = t("core.create.exists", interaction, name=name_lower)
        embed.color = discord.Color.red()
    else:
        custom_commands[name_lower] = response.strip()
        if save_custom_commands():
            embed.title = "Commande créée"
            embed.description = t("core.create.success", interaction, name=name_lower)
            embed.color = discord.Color.green()
        else:
            embed.title = "Erreur"
            embed.description = t("core.create.error", interaction)
            embed.color = discord.Color.red()
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

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
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    embed = discord.Embed(color=discord.Color.blue())
    old_name_lower = old_name.lower().strip()

    if old_name_lower not in custom_commands:
        embed.title = "Commande introuvable"
        embed.description = t("core.modif.not_found", interaction, name=old_name_lower)
        embed.color = discord.Color.red()
    elif not new_name and not new_response:
        embed.title = "Aucune modification"
        embed.description = t("core.modif.no_change", interaction, name=old_name_lower)
        embed.color = discord.Color.orange()
    else:
        try:
            if new_name:
                new_name_lower = new_name.lower().strip()
                if new_name_lower != old_name_lower and new_name_lower in custom_commands:
                    embed.title = "Nom déjà utilisé"
                    embed.description = t("core.modif_name_exists", interaction, name=new_name_lower)
                    embed.color = discord.Color.red()
                    await send_with_warning(interaction, embeds=[embed])
                    return
                custom_commands[new_name_lower] = custom_commands.pop(old_name_lower)
                old_name_lower = new_name_lower
            if new_response:
                custom_commands[old_name_lower] = new_response.strip()
            if save_custom_commands():
                embed.title = "Modification réussie"
                embed.description = t("core.modif_success", interaction, name=old_name_lower)
                embed.color = discord.Color.green()
            else:
                embed.title = "Erreur"
                embed.description = t("core.modif_error", interaction, name=old_name_lower)
                embed.color = discord.Color.red()
        except Exception as e:
            logger.error(f"Erreur lors de la modification d'une commande : {e}")
            embed.title = "Erreur"
            embed.description = f"Exception : {e}"
            embed.color = discord.Color.red()

    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])


# /delete
@bot.tree.command(name="delete", description="Supprime une commande personnalisée existante")
@app_commands.describe(name="Nom de la commande à supprimer")
async def delete_command(interaction: discord.Interaction, name: str):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    embed = discord.Embed(color=discord.Color.blue())
    name_lower = name.lower().strip()

    if name_lower not in custom_commands:
        embed.title = "Commande introuvable"
        embed.description = t("core.delete_not_found", interaction, name=name_lower)
        embed.color = discord.Color.red()
    else:
        try:
            del custom_commands[name_lower]
            if save_custom_commands():
                embed.title = "Commande supprimée"
                embed.description = t("core.delete_success", interaction, name=name_lower)
                embed.color = discord.Color.green()
            else:
                embed.title = "Erreur"
                embed.description = t("core.delete_error", interaction, name=name_lower)
                embed.color = discord.Color.red()
        except Exception as e:
            logger.error(f"Erreur lors de la suppression d'une commande : {e}")
            embed.title = "Erreur"
            embed.description = t("core.delete_exception", interaction, name=name_lower)
            embed.color = discord.Color.red()

    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])


# /warn
@bot.tree.command(name="warn", description="Met un warn à un utilisateur")
@app_commands.describe(user="Utilisateur", reason="Raison")
async def warn_command(interaction: discord.Interaction, user: discord.Member, reason: str):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    embed = discord.Embed(color=discord.Color.blue())

    if not is_admin(interaction):
        embed.title = "Permission refusée"
        embed.description = t("core.permission_denied", interaction)
        embed.color = discord.Color.red()
        embed.timestamp = date_now()
        await send_with_warning(interaction, embeds=[embed])
        return

    uid = user.id
    warns_data.setdefault(uid, {"count": 0, "reasons": []})
    warns_data[uid]["count"] += 1
    warns_data[uid]["reasons"].append(reason)
    save_warns(warns_data)

    embed.title = "Warn attribué"
    embed.description = f"{user.mention} reçoit un warn ({reason}). Total: {warns_data[uid]['count']}"
    embed.color = discord.Color.orange()
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

    if warns_data[uid]["count"] >= WARN_LIMIT:
        try:
            timeout_until = datetime.now(timezone.utc) + timedelta(seconds=KICK_DURATION)
            await user.edit(timed_out_until=timeout_until)
            await interaction.channel.send(f"{user.mention} kick temporaire ({KICK_DURATION}s)")
        except Exception as e:
            logger.error(f"Erreur kick temporaire: {e}")


# /warns
@bot.tree.command(name="warns", description="Voir warns utilisateur")
@app_commands.describe(user="Utilisateur")
async def warns_check(interaction: discord.Interaction, user: discord.Member):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    embed = discord.Embed(color=discord.Color.blue())

    uid = user.id
    data = warns_data.get(uid)
    if not data:
        embed.title = "Aucun warn"
        embed.description = f"{user.mention} n'a aucun warn."
        embed.color = discord.Color.green()
    else:
        embed.title = f"Warns pour {user.display_name}"
        embed.description = "\n".join([f"{i+1}. {r}" for i, r in enumerate(data["reasons"])])
        embed.color = discord.Color.orange()

    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])


# /unwarn
@bot.tree.command(name="unwarn", description="Supprime un warn d'un utilisateur")
@app_commands.describe(user="Utilisateur", number="Numéro du warn à supprimer (optionnel)")
async def unwarn_command(interaction: discord.Interaction, user: discord.Member, number: int = None):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    embed = discord.Embed(color=discord.Color.blue())

    if not is_admin(interaction):
        embed.title = "Permission refusée"
        embed.description = t("core.permission_denied", interaction)
        embed.color = discord.Color.red()
        embed.timestamp = date_now()
        await send_with_warning(interaction, embeds=[embed])
        return

    uid = user.id
    data = warns_data.get(uid)
    if not data or data["count"] == 0:
        embed.title = "Aucun warn"
        embed.description = f"{user.mention} n'a aucun warn."
        embed.color = discord.Color.green()
        embed.timestamp = date_now()
        await send_with_warning(interaction, embeds=[embed])
        return

    if number is None:
        removed_reason = data["reasons"].pop()
        data["count"] -= 1
        action = f"Le dernier warn a été supprimé : {removed_reason}"
    else:
        if number < 1 or number > data["count"]:
            embed.title = "Numéro invalide"
            embed.description = f"Numéro de warn invalide. Total: {data['count']}"
            embed.color = discord.Color.red()
            embed.timestamp = date_now()
            await send_with_warning(interaction, embeds=[embed])
            return
        removed_reason = data["reasons"].pop(number - 1)
        data["count"] -= 1
        action = f"Le warn #{number} a été supprimé : {removed_reason}"

    if data["count"] == 0:
        warns_data.pop(uid)
    else:
        warns_data[uid] = data

    embed.title = "Warn supprimé"
    embed.description = f"{user.mention} - {action}"
    embed.color = discord.Color.green()
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])


# /report
@bot.tree.command(name="report", description="Signale un groupe de message au staff")
@app_commands.describe(nombre="Nombre de messages à signaler (10-50)", reason="Raison du signalement")
async def report_command(interaction: discord.Interaction, nombre: int, reason: str):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    embed = discord.Embed(
        title="🚧 Fonctionnalité en construction",
        description=f"Signalement : {nombre} messages pour '{reason}'",
        color=discord.Color.yellow()
    )
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])


# /logs
@bot.tree.command(name="logs", description="Affiche les derniers logs du bot")
async def logs_command(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    embed = discord.Embed(color=discord.Color.blue())

    try:
        log_files = sorted(LOGS_DIR.glob("bot.*.log"), reverse=True)
        if not log_files:
            embed.title = "Logs"
            embed.description = "❌ Aucun fichier de log trouvé."
            embed.color = discord.Color.red()
        else:
            latest_file = log_files[0]
            content = latest_file.read_text(encoding="utf-8")[-1900:]
            embed.title = f"📜 Logs Bot ({latest_file.name})"
            embed.description = f"```{content}```"
            embed.color = discord.Color.green()
    except Exception as e:
        embed.title = "Erreur"
        embed.description = f"❌ Erreur lecture logs: {e}"
        embed.color = discord.Color.red()

    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])


# /reboot
@bot.tree.command(name="reboot", description="Redémarre le bot")
async def reboot_command(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    embed = discord.Embed(color=discord.Color.blue())

    embed.title = "Redémarrage"
    embed.description = "🔄 Redémarrage du bot..."
    embed.color = discord.Color.orange()
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

    logger.info("🔄 Redémarrage demandé par %s", interaction.user)
    await bot.close()
    os.execv(sys.executable, [sys.executable] + sys.argv)


# /upgrade
@bot.tree.command(name="upgrade", description="Met à jour le bot depuis Git")
async def upgrade_command(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    embed = discord.Embed(color=discord.Color.blue())

    if not is_admin(interaction):
        embed.title = "Permission refusée"
        embed.description = t("core.permission_denied", interaction)
        embed.color = discord.Color.red()
        embed.timestamp = date_now()
        await send_with_warning(interaction, embeds=[embed])
        return

    embed.title = "Mise à jour"
    embed.description = "⬆️ Mise à jour du bot en cours..."
    embed.color = discord.Color.orange()
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

    try:
        result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        output = result.stdout + "\n" + result.stderr
        logger.info("Git pull output:\n%s", output)
        await bot.close()
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour: {e}")
        embed.title = "Erreur"
        embed.description = f"❌ Erreur mise à jour: {e}"
        embed.color = discord.Color.red()
        embed.timestamp = date_now()
        await send_with_warning(interaction, embeds=[embed])


# /test
@bot.tree.command(name="test", description="Commande de test")
async def test_command(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    embed = discord.Embed(title=t("core.info.test"), color=discord.Color.pink())
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])


if __name__ == "__main__":
    bot.run(CONFIG["TOKEN"])
