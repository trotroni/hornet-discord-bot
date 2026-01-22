#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys
import json
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import psutil
import subprocess
import logging
from logging.handlers import TimedRotatingFileHandler
import shutil

PORT = 8000
LOG_DIR = "/home/trotroni/nude-discord-bot/logs"

SERVER_MODE = {
    "enabled": False,
    "code": None   # ex: 503, 404, 500
}

# --- Créer le dossier log du jour ---
os.makedirs(LOG_DIR, exist_ok=True)

# --- Setup logging ---
logger = logging.getLogger("ServerLogger")
logger.setLevel(logging.INFO)

# Rotation quotidienne, 7 jours de backup
log_file_path = os.path.join(LOG_DIR, "server.log")
handler = TimedRotatingFileHandler(log_file_path, when="midnight", backupCount=7, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# StreamHandler pour stdout
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
logger.addHandler(sh)

logger.info(f"--- Server démarré le {datetime.now()} ---")

class Handler(http.server.SimpleHTTPRequestHandler):

    # Override pour notre logger
    def log_message(self, format, *args):
        logger.info("%s - %s" % (self.client_address[0], format % args))

    def do_GET(self):
        # --- Mode forcé (maintenance / test erreurs) ---
        if SERVER_MODE["enabled"]:
            code = SERVER_MODE["code"] or 503
            self.send_error(code)
            return
        parsed = urlparse(self.path)
        path = parsed.path
        logger.info(f"Requête GET reçue : {path} depuis {self.client_address[0]}")

        try:
            if path == "/dashboard":
                self.path = "/web/dashboard.html"
                logger.info("Serve page dashboard.html")
                return http.server.SimpleHTTPRequestHandler.do_GET(self)

            elif path == "/api/status":
                status = {
                    "cpu_temp": self.get_cpu_temp(),
                    "cpu_perc": psutil.cpu_percent(percpu=True),
                    "ram_perc": psutil.virtual_memory().percent,
                    "bots": {
                        "core": self.is_process_running("nude-core-bot"),
                        "compta": self.is_process_running("nude-compta-bot"),
                        "server": True
                    },
                    "uptime": datetime.now().timestamp() - psutil.boot_time()
                }
                logger.info("API /status appelée")
                self.send_json(status)

            elif path == "/api/logs":
                logs_data = self.get_logs()
                logger.info("API /logs appelée")
                self.send_json(logs_data)

            elif path.startswith("/api/delete"):
                query = parse_qs(parsed.query)
                target = query.get("target", [None])[0]
                logger.info(f"API /delete appelée pour target={target}")
                if target:
                    safe_path = os.path.abspath(os.path.join(LOG_DIR, target))
                    if safe_path.startswith(os.path.abspath(LOG_DIR)) and os.path.exists(safe_path):
                        if os.path.isfile(safe_path):
                            os.remove(safe_path)
                            logger.info(f"Fichier supprimé : {safe_path}")
                        else:
                            shutil.rmtree(safe_path)
                            logger.info(f"Dossier supprimé : {safe_path}")
                        self.send_json({"success": True})
                        return
                logger.warning(f"Échec suppression : {target}")
                self.send_json({"success": False})

            elif path.startswith("/api/restart"):
                query = parse_qs(parsed.query)
                target = query.get("target", [None])[0]
                logger.info(f"API /restart appelée pour target={target}")
                if target == "raspberry":
                    subprocess.Popen(["sudo", "reboot"])
                    logger.info("Redémarrage Raspberry déclenché")
                elif target in ["nude-core-bot", "nude-compta-bot"]:
                    subprocess.Popen(["pkill", "-f", target])
                    logger.info(f"Redémarrage du bot {target} déclenché")
                self.send_json({"success": True})

            else:
                logger.info(f"Serve file standard : {self.path}")
                return http.server.SimpleHTTPRequestHandler.do_GET(self)

        except Exception as e:
            logger.exception(f"Erreur lors du traitement de {path}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Erreur serveur : {e}".encode())

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def get_cpu_temp(self):
        try:
            res = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
            t = res.stdout.strip().split('=')[1].replace("'C", "")
            return float(t)
        except Exception as e:
            logger.warning(f"Impossible de lire la température CPU : {e}")
            return None

    def is_process_running(self, name):
        try:
            return any(name in p.name() or name in " ".join(p.cmdline()) for p in psutil.process_iter())
        except Exception as e:
            logger.warning(f"Impossible de vérifier si {name} tourne : {e}")
            return False

    def get_logs(self):
        logs = {}
        if not os.path.exists(LOG_DIR):
            return logs
        for date in sorted(os.listdir(LOG_DIR), reverse=True):
            date_path = os.path.join(LOG_DIR, date)
            if os.path.isdir(date_path):
                logs[date] = {}
                for file in sorted(os.listdir(date_path)):
                    parts = file.split("_")
                    if len(parts) < 3:
                        continue
                    typ = parts[0]
                    hhmm = parts[2][:5]
                    if hhmm not in logs[date]:
                        logs[date][hhmm] = {}
                    if typ not in logs[date][hhmm]:
                        logs[date][hhmm][typ] = []
                    logs[date][hhmm][typ].append(file)
        return logs
    
    def send_error(self, code, message=None, explain=None):
        logger.warning(f"HTTP {code} sur {self.path}")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        error_dir = os.path.join(base_dir, "errors")

        specific = os.path.join(error_dir, f"{code}.html")
        generic = os.path.join(error_dir, "error.html")

        # API → JSON
        if self.path.startswith("/api"):
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": code,
                "message": message or "Erreur serveur"
            }).encode())
            return

        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        try:
            if os.path.exists(specific):
                with open(specific, "r", encoding="utf-8") as f:
                    html = f.read()
            elif os.path.exists(generic):
                with open(generic, "r", encoding="utf-8") as f:
                    html = f.read()
            else:
                raise FileNotFoundError

            html = html.replace("{{code}}", str(code))
            html = html.replace("{{message}}", message or "Erreur")

            self.wfile.write(html.encode("utf-8"))

        except Exception as e:
            logger.error(f"Erreur chargement page erreur : {e}")
            super().send_error(code, message, explain)


# --- Extensions MIME ---
Handler.extensions_map.update({
    ".js": "application/javascript",
    ".css": "text/css",
})

# --- Lancement du serveur ---
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    logger.info(f"Dashboard & server HTTP sur le port {PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Arrêt manuel du serveur")
