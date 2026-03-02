# hornet-bot/main.py
from common.imports import *
from common.init import *
from common.langManager import lang_manager
from common.utils import *

### config
bot, CONFIG, logger = create_bot("core")
guild_obj = discord.Object(id=CONFIG["GUILD_ID"])
START_TIME = date_now()

voice_client: discord.VoiceClient | None = None

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

    # démarrage task cpu
    if not cpu_temp_task.is_running():
        cpu_temp_task.start()
        logger.info("🧠 Task CPU démarrée")
    else:
        logger.warning("⚠️ Task CPU déjà en cours")

    # démarrage task hornet
    if not hornet_status_task.is_running():
        hornet_status_task.start()
        logger.info("🐝 Task Hornet démarrée")
    else:
        logger.warning("⚠️ Task Hornet déjà en cours")

# config translation
t = lang_manager.translation_key

load_playlists()

# ----------------- EMOJIS -----------------
EMOJIS = {
    "hornet": "<:hornet:1478096482425901058>",
    "hollowknight": "<:hollowknight:1426114181396041799>"
}

# ----------------- HORNET CONFIG -----------------
MIN_MESSAGES = 15
MAX_MESSAGES = 40

HORNET_QUOTES = [
    "SHAW !",
    "ADINO !",
    "HEGALE !",
    "Git gud!",
    "You wear the face of your father...",
    "I will not be bound by your laws.",
    "That crucial emptiness, I do not share."
]

HORNET_TRIGGERS = [
    "shaw",
    "adino",
    "hegale",
    "hega",
    "git gud",
    "gitgut",
    "hornet"
]

message_count = 0
next_trigger = random.randint(MIN_MESSAGES, MAX_MESSAGES)
last_hornet_message = None  # Stocker le dernier message de Hornet pour les replies

# ----------------- EVENT -----------------
@bot.event
async def on_message(message: discord.Message):
    global message_count, next_trigger, last_hornet_message

    if message.author.bot:
        # Si on reply à Hornet, renvoyer un message avec emoji
        if message.reference and message.reference.resolved == last_hornet_message:
            await message.reply(f"{random.choice(HORNET_QUOTES)} {EMOJIS['hollowknight']}")
        return

    content = message.content.lower()

    # ----------------- TRIGGERS -----------------
    # 1️⃣ Mot-clé dans le texte
    if any(trigger in content for trigger in HORNET_TRIGGERS):
        sent = await message.channel.send(f"{random.choice(HORNET_QUOTES)} {EMOJIS['hornet']}")
        last_hornet_message = sent
        return

    # 2️⃣ Mention de Hornet
    if bot.user in message.mentions:
        sent = await message.channel.send(f"{random.choice(HORNET_QUOTES)} {EMOJIS['hornet']}")
        last_hornet_message = sent
        return

    # ----------------- RANDOM INTERVAL -----------------
    message_count += 1
    if message_count >= next_trigger:
        # Déterminer le comportement aléatoire
        rand = random.random()
        reply_text = random.choice(HORNET_QUOTES)

        if rand < 0.5:
            # Message normal
            sent = await message.channel.send(f"{reply_text} {EMOJIS['hornet']}")
            last_hornet_message = sent

        elif rand < 0.8:
            # Reply au dernier message Hornet si existant
            if last_hornet_message:
                sent = await last_hornet_message.reply(f"{reply_text} {EMOJIS['hollowknight']}")
                last_hornet_message = sent
            else:
                # Sinon message normal
                sent = await message.channel.send(f"{reply_text} {EMOJIS['hornet']}")
                last_hornet_message = sent

        else:
            # Ajouter une reaction au dernier message Hornet si existant
            if last_hornet_message:
                await last_hornet_message.add_reaction(EMOJIS["hornet"])
            else:
                sent = await message.channel.send(f"{reply_text} {EMOJIS['hornet']}")
                last_hornet_message = sent

        # Reset compteur
        message_count = 0
        next_trigger = random.randint(MIN_MESSAGES, MAX_MESSAGES)

    await bot.process_commands(message)

# ----------------- REACTION EVENT -----------------
@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    global last_hornet_message

    if user.bot:
        return

    # last_hornet_message existe
    if last_hornet_message is None:
        return

    # reaction message Hornet, Hornet répond en reply ou emoji
    rand = random.random()
    reply_text = random.choice(HORNET_QUOTES)

    try:
        if rand < 0.5:
            # Message normal
            sent = await last_hornet_message.channel.send(f"{reply_text} {EMOJIS['hornet']}")
            last_hornet_message = sent
        elif rand < 0.8:
            # Reply
            sent = await last_hornet_message.reply(f"{reply_text} {EMOJIS['hollowknight']}")
            last_hornet_message = sent
        else:
            # Ajout emoji
            await last_hornet_message.add_reaction(EMOJIS["hornet"])
    except discord.Forbidden:
        pass  # erreur de permissions, ignoré

# -------------- TÂCHES PÉRIODIQUES --------------
@tasks.loop(minutes=30)
async def hornet_status_task():
    if is_panic_mode():
        await bot.change_presence(activity=discord.Game(name="⚠️ Mode panic ⚠️"))
    else:
        status_message = random.choice(HORNET_QUOTES)
        await bot.change_presence(activity=discord.Game(name=status_message))

@tasks.loop(minutes=60)
async def cpu_temp_task():
    temp_raw = get_cpu_temperature()
    try:
        temp_cpu = float(temp_raw.replace("'C", "").strip())
    except (ValueError, TypeError):
        temp_cpu = None

    status = cpu_temp_verification(temp_cpu) if temp_cpu is not None else "⚪ Inconnu"

    pwm_fan_str = get_fan_pwm()
    try:
        value_pwm = f"`{pwm_fan_str} %`"
    except (ValueError, TypeError):
        value_pwm = "`N/A` — Inconnu"

    # Définition des titres, descriptions et couleurs selon température
    if temp_cpu is None:
        title = "❌ Température CPU inconnue"
        desc = f"Impossible de lire la température\nÉtat : `{status}`\nPWM Ventilateur : `{value_pwm}`"
        color = discord.Color.light_grey()
    elif temp_cpu < 50:
        title = "✅ Température CPU normale"
        desc = f"Température : `{temp_cpu}°C`\nÉtat : `{status}`\nPWM Ventilateur : `{value_pwm}`"
        color = discord.Color.green()
    elif temp_cpu < 65:
        title = "🌡 Température CPU élevée"
        desc = f"Température : `{temp_cpu}°C`\nÉtat : `{status}`\nPWM Ventilateur : `{value_pwm}`"
        color = discord.Color.yellow()
    elif temp_cpu < 75:
        title = "⚠️ Température CPU critique"
        desc = f"Température : `{temp_cpu}°C`\nÉtat : `{status}`\nPWM Ventilateur : `{value_pwm}`\nVérifiez le refroidissement."
        color = discord.Color.orange()
    else:
        title = "🚨 TEMPÉRATURE CRITIQUE"
        desc = f"Température : `{temp_cpu}°C`\nÉtat : `{status}`\nPWM Ventilateur : `{value_pwm}`\n**Arrêt recommandé !**"
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
    logger.info(f"✅ Embed CPU envoyé : {title} | Temp: {temp_raw} | PWM: {value_pwm}")

# --- AVANT LE LANCEMENT DU TASK ---
@cpu_temp_task.before_loop
async def before_cpu_task():
    await bot.wait_until_ready()

@cpu_temp_task.before_loop
async def before_hornet_task():
    await bot.wait_until_ready()

# ---------------- COMMANDES SLASH ----------------

@bot.tree.command(name="fanconfig", description="Génère une configuration de ventilateur personnalisée")
@commands.has_permissions(administrator=True)
async def fanconfig(interaction: discord.Interaction, temp_min: float, temp_max: float, pwm_min: int, pwm_max: int):
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    try:
        if temp_min >= temp_max:
            await interaction.followup.send("❌ temp_min doit être inférieur à temp_max")
            return
        if pwm_min >= pwm_max:
            await interaction.followup.send("❌ pwm_min doit être inférieur à pwm_max")
            return
        if not (0 <= pwm_min <= 100 and 0 <= pwm_max <= 100):
            await interaction.followup.send("❌ PWM doit être entre 0 et 100")
            return

        config_content = generate_fanconfig(temp_min, temp_max, pwm_min, pwm_max)

        # Embed preview
        embed = discord.Embed(
            title="⚙️ Prévisualisation configuration ventilateur",
            description=f"```{config_content}```",
            color=discord.Color.blue()
        )
        view = FanConfirmView(config_content, backup=True)
        await interaction.followup.send(embed=embed, view=view)

    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {e}")


@bot.tree.command(name="fanpanic", description="Applique une configuration de ventilateur en mode PANIC (100% dès 1°C)")
@commands.has_permissions(administrator=True)
async def fanpanic(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    try:
        content = (
            "debug=true\n\n"
            "main:\n"
            "    1=100\n\n"
            "debug:\n"
            "    1=100\n"
        )

        # Embed preview
        embed = discord.Embed(
            title="🚨 Mode PANIC ventilateur",
            description=f"```{content}```",
            color=discord.Color.red()
        )
        view = FanConfirmView(content, backup=False)
        await interaction.followup.send(embed=embed, view=view)

    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {e}")

@bot.tree.command(name="fanrestore", description="Restaure l'ancienne configuration ventilateur")
@commands.has_permissions(administrator=True)
async def fanrestore(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)

    try:
        if restore_config():
            await interaction.followup.send("✅ Ancienne configuration restaurée avec succès !")
        else:
            await interaction.followup.send("❌ Aucune sauvegarde trouvée.")
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {e}")

# ---------------- Lecture suivante interne ----------------
async def _play_next(interaction: discord.Interaction):
    global voice_client
    next_audio = audio_queue.next()
    if not next_audio:
        return

    source = discord.FFmpegPCMAudio(next_audio["url"], **FFMPEG_OPTIONS)

    def after_playing(error):
        if error:
            logger.debug(error)
        # relancer la lecture
        bot.loop.create_task(_play_next(interaction))

    voice_client.play(source, after=after_playing)

# ---------------- PLAY ----------------
player = MusicPlayer()  # instance globale

@bot.tree.command(name="play", description="Lit une musique depuis YouTube")
@app_commands.describe(query="Titre ou lien YouTube")
async def play_command(interaction: discord.Interaction, query: str):
    global player

    await interaction.response.defer()

    # Vérification salon vocal
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.followup.send(
            "❌ Tu dois être connecté à un salon vocal.",
            ephemeral=True
        )
        return

    channel = interaction.user.voice.channel

    # Connexion si nécessaire
    if not player.voice_client or not player.voice_client.is_connected():
        player.voice_client = await channel.connect()

    # Récupération musique
    try:
        audio = get_audio_source(query)
    except ValueError as e:
        await interaction.followup.send(str(e), ephemeral=True)
        return

    # Ajout à la queue
    player.queue.add(audio)

    # Si rien ne joue → démarrer
    if not player.voice_client.is_playing():
        await player.play_next()

    # Embed initial
    embed = discord.Embed(
        title="🎵 Ajouté à la queue",
        description=f"**[{audio['title']}]({audio.get('webpage_url')})**",
        color=discord.Color.blue()
    )

    if audio.get("thumbnail"):
        embed.set_thumbnail(url=audio["thumbnail"])

    embed.add_field(
        name="⏱ Durée",
        value=format_duration(audio.get("duration")),
        inline=True
    )

    if audio.get("uploader"):
        embed.add_field(
            name="👤 Auteur",
            value=audio["uploader"],
            inline=True
        )

    embed.timestamp = date_now()

    # Envoi du message player
    message = await interaction.followup.send(
        embeds=[embed],
        view=MusicControls(player)
    )

    # Stocker le message pour updates live
    player.message = message

# a revoir
"""
# ---------------- VOLUME ----------------
@bot.tree.command(name="volume", description="Change le volume de la musique")
@app_commands.describe(level="Niveau de volume (0 à 100)")
async def volume_command(interaction: discord.Interaction, level: int):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    embed = discord.Embed(title=t("core.volume.title"), color=discord.Color.green())
    if not voice_client or not voice_client.is_playing():
        embed.color = discord.Color.red()
        embed.description = t("core.volume.nothing")
    elif level < 0 or level > 100:
        embed.color = discord.Color.red()
        embed.description = t("core.volume.invalid")
    else:
        audio_queue.set_volume(level / 100)
        embed.description = t("core.volume.set", level=level)
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])


# ---------------- ADDLIST ----------------
@bot.tree.command(name="addlist", description="Ajoute un lien à une playlist existante")
@app_commands.describe(number="Numéro de la playlist", url="Lien de la musique à ajouter")
async def addlist_command(interaction: discord.Interaction, number: int, url: str):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    playlist = playlists.get(number, [])
    playlist.append(url)
    playlists[number] = playlist
    save_playlists()

    embed = discord.Embed(
        title=t("core.addlist.title"),
        description=t("core.addlist.added", number=number, url=url),
        color=discord.Color.green()
    )
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

# ---------------- PLAYLIST ----------------
@bot.tree.command(name="playlist", description="Joue une playlist")
@app_commands.describe(number="Numéro de la playlist à jouer")
async def playlist_command(interaction: discord.Interaction, number: int):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    playlist = playlists.get(number)
    embed = discord.Embed(title=t("core.playlist.title"), color=discord.Color.green())
    if not playlist:
        embed.color = discord.Color.red()
        embed.description = t("core.playlist.not_found", number=number)
    else:
        for url in playlist:
            audio = get_audio_source(url)
            audio_queue.add(audio)
        embed.description = t("core.playlist.started", number=number, count=len(playlist))
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

# ---------------- LIST ----------------
@bot.tree.command(name="list", description="Liste les playlists ou leur contenu")
@app_commands.describe(number="Numéro de la playlist (optionnel)")
async def list_command(interaction: discord.Interaction, number: int = None):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    embed = discord.Embed(title=t("core.list.title"), color=discord.Color.green())
    if number is None:
        if not playlists:
            embed.color = discord.Color.red()
            embed.description = t("core.list.none")
        else:
            embed.description = "\n".join([f"{num}: {len(pl)} liens" for num, pl in playlists.items()])
    else:
        pl = playlists.get(number)
        if not pl:
            embed.color = discord.Color.red()
            embed.description = t("core.list.not_found", number=number)
        else:
            embed.description = "\n".join([f"{i+1}. {url}" for i, url in enumerate(pl)])
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

# ---------------- DELETELIST ----------------
@bot.tree.command(name="deletelist", description="Supprime une playlist ou un élément")
@app_commands.describe(number="Numéro de la playlist", index="Numéro du morceau à supprimer (optionnel)")
async def deletelist_command(interaction: discord.Interaction, number: int, index: int = None):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    pl = playlists.get(number)
    embed = discord.Embed(title=t("core.deletelist.title"), color=discord.Color.green())
    if not pl:
        embed.color = discord.Color.red()
        embed.description = t("core.deletelist.not_found", number=number)
    elif index is None:
        del playlists[number]
        save_playlists()
        embed.description = t("core.deletelist.deleted", number=number)
    else:
        if index < 1 or index > len(pl):
            embed.color = discord.Color.red()
            embed.description = t("core.deletelist.invalid_index", number=number, index=index)
        else:
            removed = pl.pop(index - 1)
            playlists[number] = pl
            save_playlists()
            embed.description = t("core.deletelist.deleted_item", number=number, index=index, url=removed)
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

"""

# secours pour stats
"""
# /hornetstats
@bot.tree.command(name="hornetstats", description="Affiche les stats du système de random Hornet")
async def hornet_stats(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    global message_count, next_trigger

    embed = discord.Embed(
        title="Hornet Random System",
        color=discord.Color.purple()
    )

    embed.add_field(name="Messages comptés", value=f"`{str(message_count)}`/`{str(next_trigger)}`", inline=False)

    embed.add_field(
        name="Répliques",
        value="\n".join(f"• {quote}" for quote in HORNET_QUOTES),
        inline=False
    )

    embed.add_field(
        name="Déclencheurs",
        value=", ".join(HORNET_TRIGGERS),
        inline=False
    )

    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

# /stat
@bot.tree.command(name="stat", description="Stat sur le bot")
async def botstat(interaction: discord.Interaction):
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

    pwm_fan_str = get_fan_pwm()
    try:
        value = f"`{pwm_fan_str} %`"
    except (ValueError, TypeError):
        value = "`N/A` — Inconnu"

    embed.add_field(
        name=t("core.stat.fan_pwm"),
        value=value,
        inline=True
    )

    embed.timestamp = date_now()

    await send_with_warning(interaction, embeds=[embed])
"""

@bot.tree.command(name="stat", description="Statistiques du bot ou du système Hornet")
@app_commands.describe(module="Choisir le module à afficher")
@app_commands.choices(module=[
    app_commands.Choice(name="bot", value="bot"),
    app_commands.Choice(name="hornet", value="hornet")
])
async def stat(interaction: discord.Interaction, module: app_commands.Choice[str]):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    global message_count, next_trigger

    # =========================
    # SECTION HORNET
    # =========================
    if module.value == "hornet":

        embed = discord.Embed(
            title="Hornet Random System",
            color=discord.Color.purple()
        )

        embed.add_field(
            name="Messages comptés",
            value=f"`{message_count}`/`{next_trigger}`",
            inline=False
        )

        embed.add_field(
            name="Répliques",
            value="\n".join(f"• {quote}" for quote in HORNET_QUOTES),
            inline=False
        )

        embed.add_field(
            name="Déclencheurs",
            value=", ".join(HORNET_TRIGGERS),
            inline=False
        )

        embed.timestamp = date_now()
        print("avant send_with_warning")
        await send_with_warning(interaction, embeds=[embed])
        print("après send_with_warning")
        return

    # =========================
    # SECTION BOT
    # =========================
    if module.value == "bot":

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

        embed = discord.Embed(
            title=t("core.stat.title"),
            color=discord.Color.pink()
        )

        for chunk in users_list_chunks:
            embed.add_field(
                name=t("core.stat.members", member_count=interaction.guild.member_count),
                value=chunk,
                inline=False
            )

        embed.add_field(
            name=t("core.stat.servers", servers_count=servers_count),
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

        pwm_fan_str = get_fan_pwm()
        embed.add_field(
            name=t("core.stat.fan_pwm"),
            value=f"`{pwm_fan_str} %`",
            inline=True
        )

        embed.timestamp = date_now()
        print("avant send_with_warning")
        await send_with_warning(interaction, embeds=[embed])
        print("après send_with_warning")

# /biere
@bot.tree.command(name="biere", description="Teste l'alcoolémie du bot")
async def biere(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    a = randint(1, 7)
    if a == 1:
        embed = discord.Embed(title=t("core.biere.response1"), color=discord.Color.pink())
    elif a == 2:
        embed = discord.Embed(title=t("core.biere.response2"), color=discord.Color.pink())
    elif a == 3:
        embed = discord.Embed(title=t("core.biere.response3"), color=discord.Color.pink())
    elif a == 4:
        embed = discord.Embed(title=t("core.biere.response4"), color=discord.Color.pink())
    elif a == 5:
        embed = discord.Embed(title=t("core.biere.response5"), color=discord.Color.pink())
    elif a == 6:
        embed = discord.Embed(title=t("core.biere.response6"), color=discord.Color.pink())
    elif a == 7:
        embed = discord.Embed(title=t("core.biere.response7"), color=discord.Color.pink())

    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

# /ping
@bot.tree.command(name="ping", description="Teste l'alcoolémie du bot")
async def ping(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    embed = discord.Embed(title=t("core.ping.response"), color=discord.Color.pink())
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

@bot.tree.command(name="addkeyword", description="Ajoute un mot-clé à un sujet de réaction")
@commands.has_permissions(administrator=True)
async def addkeyword(interaction: discord.Interaction, topic: str, *, keyword: str):
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    topic = topic.lower()

    if topic not in REACTION_TOPICS:
        await interaction.followup.send(f"❌ Sujet `{topic}` introuvable.")
        return

    REACTION_TOPICS[topic]["keywords"].append(keyword.lower())

    await interaction.followup.send(f"✅ Mot-clé `{keyword}` ajouté au sujet `{topic}`.")

@bot.tree.command(name="addresponse", description="Ajoute une réponse à un sujet de réaction")
@commands.has_permissions(administrator=True)
async def addresponse(interaction: discord.Interaction, topic: str, rtype: str, *, content: str):
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    topic = topic.lower()
    rtype = rtype.lower()

    if topic not in REACTION_TOPICS:
        await interaction.followup.send("❌ Sujet introuvable.")
        return

    if rtype not in ["text", "gif"]:
        await interaction.followup.send("❌ Type invalide (text/gif).")
        return

    REACTION_TOPICS[topic]["responses"].append({
        "type": rtype,
        "content": content
    })

    await interaction.followup.send(f"✅ Réponse ajoutée au sujet `{topic}`.")

if __name__ == "__main__":
    bot.run(CONFIG["TOKEN"])
