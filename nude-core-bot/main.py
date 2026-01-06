# nude-core-bot/main.py
from common.init import create_bot
from common.langManager import lang_manager
from common.imports import *
#from common.loggingBot import getLogger

bot, CONFIG, logger = create_bot("core")

guild_obj = discord.Object(id=CONFIG["GUILD_ID"])

t = lang_manager.get

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

# COMMANDES SLASH

# /ping
@bot.tree.command(name="ping", description="Teste la réactivité du bot")
async def ping(interaction: discord.Interaction):
    embed = discord.Embed(
        title=t(f"info.ping.response"),
        description=t("bot.online_description"),
        color=discord.Color.pink()
    )
    await interaction.response.send_message(embed=embed)

# /info
@bot.tree.command(name="info", description="Info sur le bot")
async def info(interaction: discord.Interaction):
    user = interaction.user
    name = interaction.command.name
    logger.info(f"L'utilisateur {user} a exécuté la commande {name}")
    await interaction.response.send_message(
        t(
            "info.response",
            interaction,
            version=VERSION
        ),
        ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)

# /help
@bot.tree.command(name="help", description="Affiche toutes les commandes disponibles")
async def help_command(interaction: discord.Interaction):
    user = interaction.user
    name = interaction.command.name
    logger.info(f"L'utilisateur {user} a exécuté la commande {name}")
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
    await interaction.response.send_message(embed=embed, ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)

# /language
@bot.tree.command(name="language", description="Change la langue du bot")
@app_commands.describe(lang="Code de la langue (ex: fr, en)")
async def language_command(interaction: discord.Interaction, lang: str = None):
    user = interaction.user
    name = interaction.command.name
    logger.info(f"L'utilisateur {user} a exécuté la commande {name}")
    if lang is None:
        embed = discord.Embed(title=t("language_title", interaction), color=discord.Color.blue())
        current_lang = lang_manager.user_preferences.get(interaction.user.id, DEFAULT_LANGUAGE)
        embed.description = t("language_current", interaction, language=lang_manager.get_language_name(current_lang)) + "\n\n"
        embed.description += t("language_available", interaction) + "\n"
        for lang_code in sorted(lang_manager.available_languages):
            embed.description += f"• `{lang_code}` - {lang_manager.get_language_name(lang_code)}\n"
        embed.set_footer(text=t("language_usage", interaction))
        await interaction.response.send_message(embed=embed, ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)
    else:
        lang = lang.lower().strip()
        if lang_manager.set_user_language(interaction.user.id, lang):
            await interaction.response.send_message(t("language_changed", interaction, language=lang_manager.get_language_name(lang)), ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)
        else:
            await interaction.response.send_message(t("language_invalid", interaction, lang=lang), ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)

# /list
@bot.tree.command(name="list", description="Liste toutes les commandes personnalisées")
async def list_commands(interaction: discord.Interaction):
    user = interaction.user
    name = interaction.command.name
    logger.info(f"L'utilisateur {user} a exécuté la commande {name}")
    if not custom_commands:
        await interaction.response.send_message(t("list_empty", interaction), ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)
        return
    embed = discord.Embed(title=t("list_title", interaction), color=discord.Color.green())
    embed.description = "\n".join([f"• `/{name}`" for name in sorted(custom_commands.keys())])
    embed.set_footer(text=t("list_footer", interaction, count=len(custom_commands)))
    await interaction.response.send_message(embed=embed, ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)

# /create
@bot.tree.command(name="create", description="Crée une nouvelle commande personnalisée")
@app_commands.describe(name="Nom de la commande", response="Réponse du bot")
async def create_command(interaction: discord.Interaction, name: str, response: str):
    user = interaction.user

    logger.info(f"L'utilisateur {user} a exécuté la commande {name}")

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
    user = interaction.user
    name = interaction.command.name
    logger.info(f"L'utilisateur {user} a exécuté la commande {name}")
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
    user = interaction.user
    name = interaction.command.name
    logger.info(f"L'utilisateur {user} a exécuté la commande {name}")
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
    cmd_user = interaction.user
    cmd_name = interaction.command.name
    logger.info(f"L'utilisateur {cmd_user} a exécuté la commande {cmd_name}")

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
    user = interaction.user
    name = interaction.command.name
    logger.info(f"L'utilisateur {user} a exécuté la commande {name}")
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
    user = interaction.user
    name = interaction.command.name
    logger.info(f"L'utilisateur {user} a exécuté la commande {name}")
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
    user = interaction.user
    name = interaction.command.name
    logger.info(f"L'utilisateur {user} a exécuté la commande {name}")
    await interaction.response.send_message(
        "🚧 Fonctionnalité en construction.",
        ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
    )

# /logs
@bot.tree.command(name="logs", description="Affiche les derniers logs du bot")
async def logs_command(interaction: discord.Interaction):
    user = interaction.user
    name = interaction.command.name
    logger.info(f"L'utilisateur {user} a exécuté la commande {name}")
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
    (os.execv(sys.executable, [sys.executable] + sys.argv))

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
    user = interaction.user
    name = interaction.command.name
    logger.info(f"L'utilisateur {user} a exécuté la commande {name}")
    await interaction.response.send_message("✅ Test réussi!", ephemeral=CONFIG["EPHEMERAL_GLOBAL"]
)



if __name__ == "__main__":
    bot.run(CONFIG["TOKEN"])
