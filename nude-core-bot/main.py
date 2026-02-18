# nude-core-bot/main.py
from common.imports import *
from common.init import *
from common.langManager import lang_manager
from common.utils import *

### config
bot, CONFIG, logger = create_bot("core")
guild_obj = discord.Object(id=CONFIG["GUILD_ID"])
START_TIME = date_now()
load_custom_commands()

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

    # message envoyé au demarrage
    """
    channel = bot.get_channel(1417564003760082978)

    if channel is None:
        logger.debug("❌ Channel général introuvable")
        return

    embed = discord.Embed(
        title="C'est bon !",
        description="J'en ai marre !",
        color=discord.Color.green()
    )
    embed.timestamp = discord.utils.utcnow()

    await channel.send(embed=embed)
    """
    # démarrage task cpu
    if not cpu_temp_task.is_running():
        cpu_temp_task.start()
        logger.info("🧠 Task CPU démarrée")
    else:
        logger.warning("⚠️ Task CPU déjà en cours")

# config translation
t = lang_manager.translation_key

load_playlists()

# -------- CONFIG --------
MIN_MESSAGES = 15   # x
MAX_MESSAGES = 40   # y

HORNET_QUOTES = [
    "SHAW!",
    "ADINO!",
    "HEGALE!",
    "Git gud!",
    "You wear the face of your father...",
    "I will not be bound by your laws.",
    "That crucial emptiness, I do not share."
]

HORNET_TRIGGERS = [
    "shaw",
    "adino",
    "hega",
    "git gud",
    "hornet"
]
# ------------------------


message_count = 0
next_trigger = randint(MIN_MESSAGES, MAX_MESSAGES)

@bot.event
async def on_message(message: discord.Message):
    global message_count, next_trigger

    if message.author.bot:
        return

    content = message.content.lower()

    # Trigger direct Hornet
    if any(trigger in content for trigger in HORNET_TRIGGERS):
        reply = random.choice(HORNET_QUOTES)
        await message.channel.send(reply)
        return

    # Compteur
    message_count += 1
    logger.debug(f"[DEBUG] {message_count} / {next_trigger}")

    if message_count >= next_trigger:
        reply = random.choice(HORNET_QUOTES)
        await message.channel.send(reply)

        logger.debug(f"[DEBUG] TRIGGERED at {message_count}")

        message_count = 0
        next_trigger = random.randint(MIN_MESSAGES, MAX_MESSAGES)
        logger.debug(f"[DEBUG] New target: {next_trigger}")

    await bot.process_commands(message)

# -------------- TÂCHES PÉRIODIQUES --------------
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

# ---------------- COMMANDES SLASH ----------------

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
    play.message = await send_with_warning(
        interaction,
        embeds=[embed],
        view=MusicControls(player)
    )

    # Stocker le message pour updates live
    player.message = play.message
# ---------------- STOP ----------------
@bot.tree.command(name="stop", description="Arrête la lecture et déconnecte le bot")
async def stop_command(interaction: discord.Interaction):
    global voice_client
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    if voice_client:
        audio_queue.clear()
        await voice_client.disconnect()
        voice_client = None

    embed = discord.Embed(
        title=t("core.stop.title"),
        description=t("core.stop.stopped"),
        color=discord.Color.green()
    )
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

# ---------------- SKIP ----------------
@bot.tree.command(name="skip", description="Passe la musique en cours")
async def skip_command(interaction: discord.Interaction):
    global voice_client
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    embed = discord.Embed(title=t("core.skip.title"), color=discord.Color.green())
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        embed.description = t("core.skip.skipped")
    else:
        embed.color = discord.Color.red()
        embed.description = t("core.skip.nothing_playing")
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

# ---------------- PAUSE ----------------
@bot.tree.command(name="pause", description="Met en pause la musique en cours")
async def pause_command(interaction: discord.Interaction):
    global voice_client
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    embed = discord.Embed(title=t("core.pause.title"), color=discord.Color.green())
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        embed.description = t("core.pause.paused")
    else:
        embed.color = discord.Color.red()
        embed.description = t("core.pause.nothing_playing")
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

# ---------------- RESUME ----------------
@bot.tree.command(name="resume", description="Reprend la musique mise en pause")
async def resume_command(interaction: discord.Interaction):
    global voice_client
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    embed = discord.Embed(title=t("core.resume.title"), color=discord.Color.green())
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        embed.description = t("core.resume.resumed")
    else:
        embed.color = discord.Color.red()
        embed.description = t("core.resume.nothing_paused")
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

# ---------------- QUEUE ----------------
@bot.tree.command(name="queue", description="Affiche la file d'attente des musiques")
async def queue_command(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    embed = discord.Embed(title=t("core.queue.title"), color=discord.Color.green())
    if audio_queue.empty():
        embed.color = discord.Color.red()
        embed.description = t("core.queue.empty")
    else:
        embed.description = "\n".join([f"{i+1}. {item['title']}" for i, item in enumerate(audio_queue.queue)])
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

# ---------------- NOW PLAYING ----------------
@bot.tree.command(name="nowplaying", description="Affiche la musique en cours")
async def nowplaying_command(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    embed = discord.Embed(title=t("core.nowplaying.title"), color=discord.Color.green())
    if not voice_client or not voice_client.is_playing():
        embed.color = discord.Color.red()
        embed.description = t("core.nowplaying.nothing")
    else:
        current = audio_queue.current()
        embed.description = t("core.nowplaying.current", title=current["title"])
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

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

# ---------------- REPEAT ----------------
@bot.tree.command(name="repeat", description="Active ou désactive la répétition de la musique")
async def repeat_command(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    audio_queue.toggle_repeat()
    state = "on" if audio_queue.repeat else "off"
    embed = discord.Embed(
        title=t("core.repeat.title"),
        description=t("core.repeat.status", state=state),
        color=discord.Color.green()
    )
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

# ---------------- SHUFFLE ----------------
@bot.tree.command(name="shuffle", description="Mélange la file d'attente")
async def shuffle_command(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    embed = discord.Embed(title=t("core.shuffle.title"), color=discord.Color.green())
    if audio_queue.empty():
        embed.color = discord.Color.red()
        embed.description = t("core.shuffle.empty")
    else:
        audio_queue.shuffle()
        embed.description = t("core.shuffle.done")
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

# ---------------- CLEAR ----------------
@bot.tree.command(name="clear", description="Vide la file d'attente")
async def clear_command(interaction: discord.Interaction):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    audio_queue.clear()
    embed = discord.Embed(
        title=t("core.clear.title"),
        description=t("core.clear.done"),
        color=discord.Color.green()
    )
    embed.timestamp = date_now()
    await send_with_warning(interaction, embeds=[embed])

# ---------------- PLAYADD ----------------
@bot.tree.command(name="playadd", description="Ajoute un lien à la liste provisoire")
@app_commands.describe(url="Lien de la musique à ajouter")
async def playadd_command(interaction: discord.Interaction, url: str):
    command_log(interaction.command.name, interaction.user.id, interaction.user.name)
    await interaction.response.defer(ephemeral=CONFIG["EPHEMERAL_GLOBAL"])

    if not hasattr(audio_queue, "temp_list"):
        audio_queue.temp_list = []
    audio_queue.temp_list.append(url)

    embed = discord.Embed(
        title=t("core.playadd.title"),
        description=t("core.playadd.added", url=url),
        color=discord.Color.green()
    )
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


if __name__ == "__main__":
    bot.run(CONFIG["TOKEN"])
