# 🌍 Guide du système de traductions

## 📁 Structure des fichiers

```

votre_projet/
├── main.py                  # Script principal du bot
├── var.env                  # Variables d'environnement
├── token.env                # Variables d'environnement (private)
├── data/
│   ├── commands.csv         # Commandes personnalisées
│   ├── warns.csv            # Données de modération (warns)
│   └── logs/                # 📂 Logs du bot
├── languages/               # 📂 Dossier des traductions
│   ├── fr.json              # Français (par défaut)
│   └── en.json              # Anglais (exemple)

```

---

## 🚀 Installation rapide

1. Créer le dossier `languages/` dans le même répertoire que `main.py`.  
2. Créer le dossier `data/` pour stocker les fichiers CSV et logs.  
3. Copier les fichiers JSON (`fr.json`, `en.json`, etc.) dans `languages/`.  
4. Configurer la langue par défaut dans `.env` :

```env
DEFAULT_LANGUAGE=fr
````

5. Installer les dépendances :

```bash
pip install discord.py python-dotenv
```

---

## ✏️ Ajouter une nouvelle langue

### Étape 1 : Créer le fichier JSON

Créez un nouveau fichier dans `languages/` avec le code de langue (ex: `de.json` pour l'allemand).

### Étape 2 : Structure du fichier

Copiez la structure d'un fichier existant et traduisez toutes les clés :

```json
{
  "language_name": "Deutsch",
  "ping_response": "Pong! 🏓",
  "help_title": "📚 Hilfe - Verfügbare Befehle"
}
```

### Étape 3 : Redémarrer le bot

Le bot détectera automatiquement la nouvelle langue au démarrage.

---

## 🔑 Liste des clés de traduction

### Informations générales

* `language_name` : Nom de la langue (affiché dans `/language`)
* `ping_response` : Réponse de la commande `/ping`
* `bot_online` : Message de démarrage du bot
* `no_permission` : Message d'erreur pour permissions insuffisantes

### Commande `/help`

* `help_title`, `help_system`, `help_csv`, `help_lang`, `help_footer`
* `help_ping`, `help_reboot`, `help_upgrade`
* `help_create`, `help_modif`, `help_reload`, `help_list`
* `help_language`

### Commande `/list`

* `list_title`, `list_empty`, `list_footer`

### Commande `/create`

* `create_exists`, `create_success`, `create_error`

### Commande `/modif`

* `modif_not_found`, `modif_success`, `modif_error`, `modif_name_exists`, `modif_success_rename`

### Commande `/reload_commands`

* `reload_success`, `reload_error`

### Commande `/upgrade`

* `upgrade_updating`, `upgrade_success`, `upgrade_restarting`, `upgrade_timeout`, `upgrade_error`

### Commande `/reboot`

* `reboot_message`

### Commande `/bot_update`

* `bot_update_sent`, `bot_update_not_configured`, `bot_update_channel_not_found`, `bot_update_notification`, `bot_update_error`

### Commande `/language`

* `language_changed`, `language_current`, `language_available`, `language_invalid`, `language_usage`, `language_title`

### Messages généraux

* `no_permission`, `bot_online`

---

## 💡 Variables dynamiques

Certaines traductions contiennent des variables entre accolades :

* `{count}` : Nombre de commandes
* `{name}` : Nom d'une commande
* `{error}` : Message d'erreur
* `{output}` : Sortie de commande
* `{language}` : Nom de la langue

Exemple :

```json
"reload_success": "✅ Commandes rechargées ! {count} commande(s) disponible(s)."
```

---

## 🎯 Utilisation par les utilisateurs

### Changer de langue

```
/language fr    → Passer en français
/language en    → Passer en anglais
/language       → Voir les langues disponibles
```

### Préférences

* Chaque utilisateur peut avoir sa propre langue
* La préférence est stockée en mémoire (réinitialisée au redémarrage)
* La langue par défaut est définie dans `.env` avec `DEFAULT_LANGUAGE`

---

## ⚙️ Configuration avancée

### Langue par défaut

Dans `.env` :

```env
DEFAULT_LANGUAGE=fr
```

### Langue de secours

Si une langue n'est pas trouvée, le bot utilise :

1. La langue de l'utilisateur (si définie)
2. `DEFAULT_LANGUAGE`
3. La première langue disponible dans `/languages/`

### Fichiers manquants

Si aucun fichier de traduction n'existe au démarrage, le bot affiche un avertissement dans les logs mais continue de fonctionner.

---

## 🔧 Dépannage

### Le bot ne trouve pas les traductions

✅ Vérifiez que le dossier `languages/` existe
✅ Vérifiez que les fichiers JSON sont bien encodés en UTF-8
✅ Vérifiez les logs dans `data/logs/` pour voir les erreurs

### Une clé de traduction manque

Le bot affichera la clé elle-même si une traduction est manquante :

```
help_title  (au lieu du texte traduit)
```

### Ajouter des traductions personnalisées

Vous pouvez ajouter vos propres clés dans les fichiers JSON et les utiliser dans le code avec :

```python
t("ma_cle_personnalisee", interaction)
```

---

## 📝 Exemple complet

### Créer une nouvelle langue (italien)

Fichier : `languages/it.json`

```json
{
  "language_name": "Italiano",
  "ping_response": "Pong! 🏓",
  "help_title": "📚 Aiuto - Comandi disponibili",
  "no_permission": "⚠️ Non hai il permesso di usare questo comando."
}
```

Redémarrez le bot, puis :

```
/language it
```

✅ Le bot parlera maintenant italien pour cet utilisateur !

---

## 🌟 Langues suggérées

| Code | Langue    | Fichier | Disponible |
| ---- | --------- | ------- | ---------- |
| fr   | Français  | fr.json | Oui        |
| en   | Anglais   | en.json | Non        |

---

💬 Besoin d'aide ? Consultez le responsable pour tout probleme
