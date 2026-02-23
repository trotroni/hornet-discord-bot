"""
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
"""