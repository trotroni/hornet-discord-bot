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
from dotenv import load_dotenv

PORT = 8000
LOGS_DIR = "/home/trotroni/nude-discord-bot/logs"
os.makedirs(LOGS_DIR, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ERRORS_DIR = os.path.join(BASE_DIR, "errors")
STATE_FILE = os.path.join(BASE_DIR, "server_state.json")

load_dotenv("/home/trotroni/nude-discord-bot/var.env")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"enabled": False, "code": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

SERVER_MODE = load_state()

# --- Logging ---
logger = logging.getLogger("ServerLogger")
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler(
    os.path.join(LOGS_DIR, "server.log"),
    when="midnight",
    backupCount=7,
    encoding="utf-8"
)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))

logger.info(f"--- Server démarré le {datetime.now()} ---")

class Handler(http.server.SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        logger.info("%s - %s" % (self.client_address[0], format % args))

    def admin_allowed(self, parsed):
        ip = self.client_address[0]
        token = parse_qs(parsed.query).get("token", [None])[0]
        return (
            ip.startswith("127.") or
            ip.startswith("192.168.") or
            token == ADMIN_TOKEN
        )

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        logger.info(f"Requête GET reçue : {path} depuis {self.client_address[0]}")

        # --- Mode forcé (maintenance / test erreurs) ---
        if SERVER_MODE["enabled"]:
            self.send_error(SERVER_MODE["code"] or 503)
            logger.info(
                f"Requête rejetée ({SERVER_MODE['code']}) depuis {self.client_address[0]}"
            )
            return

        try:
            if path == "/dashboard":
                self.path = "/web/dashboard.html"
                return super().do_GET()

            elif path == "/admin":
                self.path = "/admin/admin.html"
                return super().do_GET()

            elif path == "/api/status":
                self.send_json({
                    "cpu_temp": self.get_cpu_temp(),
                    "cpu_perc": psutil.cpu_percent(percpu=True),
                    "ram_perc": psutil.virtual_memory().percent,
                    "bots": {
                        "core": self.is_process_running("nude-core-bot"),
                        "compta": self.is_process_running("nude-compta-bot"),
                        "server": True
                    },
                    "uptime": datetime.now().timestamp() - psutil.boot_time()
                })

            elif path == "/api/admin/set":
                if not self.admin_allowed(parsed):
                    self.send_error(403)
                    return

                code = int(parse_qs(parsed.query).get("code", [503])[0])
                SERVER_MODE["enabled"] = True
                SERVER_MODE["code"] = code
                save_state(SERVER_MODE)

                self.send_json({"enabled": True, "code": code})

            elif path == "/api/admin/disable":
                if not self.admin_allowed(parsed):
                    self.send_error(403)
                    return

                SERVER_MODE["enabled"] = False
                SERVER_MODE["code"] = None
                save_state(SERVER_MODE)

                self.send_json({"enabled": False})

            else:
                return super().do_GET()

        except Exception as e:
            logger.exception("Erreur serveur")
            self.send_error(500, str(e))

    def send_json(self, data):
        raw = json.dumps(data, indent=2).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def send_error(self, code, message=None, explain=None):
        logger.warning(f"HTTP {code} sur {self.path}")

        if self.path.startswith("/api"):
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": code,
                "message": message or "Erreur serveur"
            }).encode())
            return

        if code == 503:
            file = os.path.join(ERRORS_DIR, "maintenance.html")
        else:
            file = os.path.join(ERRORS_DIR, f"{code}.html")

        if not os.path.exists(file):
            file = os.path.join(ERRORS_DIR, "error.html")

        try:
            with open(file, "rb") as f:
                content = f.read()
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception:
            super().send_error(code, message, explain)

Handler.extensions_map.update({
    ".js": "application/javascript",
    ".css": "text/css",
})

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    logger.info(f"Serveur HTTP actif sur le port {PORT}")
    httpd.serve_forever()

# --- Lancement du serveur ---
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    logger.info(f"Dashboard & server HTTP sur le port {PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Arrêt manuel du serveur")
