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
import time
from collections import defaultdict

PORT = 8000

ALLOWED_IPS = ("127.", "192.168.", "10.")
RATE_LIMIT = 60        # requêtes
RATE_WINDOW = 60       # secondes

rate_limit_store = defaultdict(list)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ERRORS_DIR = os.path.join(BASE_DIR, "errors")
STATE_FILE = os.path.join(BASE_DIR, "server_state.json")

LOGS_DIR = "/home/trotroni/nude-discord-bot/logs"
os.makedirs(LOGS_DIR, exist_ok=True)

load_dotenv("/home/trotroni/nude-discord-bot/var.env")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")

# ──────────────────────────
# État serveur (maintenance)
# ──────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"enabled": False, "code": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

SERVER_MODE = load_state()

# ──────────────────────────
# Logging
# ──────────────────────────
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

# ──────────────────────────
# HTTP Handler
# ──────────────────────────
class Handler(http.server.SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        logger.info("%s - %s" % (self.client_address[0], format % args))

    # ──────────── ADMIN ────────────
    def admin_allowed(self):
        if not self.ip_allowed():
            return False
        token = self.get_bearer_token()
        return token == ADMIN_TOKEN
    def get_bearer_token(self):
        auth = self.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return None
        return auth.split(" ", 1)[1]
    def ip_allowed(self):
        return self.client_address[0].startswith(ALLOWED_IPS)
    def rate_limited(self):
        ip = self.client_address[0]
        now = time.time()
    
        rate_limit_store[ip] = [
            t for t in rate_limit_store[ip]
            if now - t < RATE_WINDOW
        ]
    
        if len(rate_limit_store[ip]) >= RATE_LIMIT:
            return True
        
        rate_limit_store[ip].append(now)
        return False
    # ──────────── GET ────────────
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        logger.info(f"GET {path} depuis {self.client_address[0]}")
        if self.rate_limited():
            self.send_error(429, "Too Many Requests")
            return
        # MODE MAINTENANCE / TEST ERREUR
        if SERVER_MODE["enabled"]:
            self.send_error(SERVER_MODE["code"] or 503)
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

            elif path == "/api/logs":
                self.send_json(self.get_logs())

            elif path.startswith("/api/delete"):
                self.handle_delete(parsed)

            elif path.startswith("/api/restart"):
                self.handle_restart(parsed)

            elif path == "/api/admin/set":
                if not self.admin_allowed():
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

    # ──────────── JSON ────────────
    def send_json(self, data):
        raw = json.dumps(data, indent=2).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    # ──────────── ERROR HANDLER ────────────
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

        with open(file, "rb") as f:
            content = f.read()

        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    # ──────────── MONITORING ────────────
    def get_cpu_temp(self):
        try:
            res = subprocess.run(
                ["vcgencmd", "measure_temp"],
                capture_output=True,
                text=True
            )
            return float(res.stdout.split("=")[1].replace("'C", ""))
        except Exception:
            return None

    def is_process_running(self, name):
        try:
            return any(
                name in p.name() or name in " ".join(p.cmdline())
                for p in psutil.process_iter()
            )
        except Exception:
            return False

    def get_logs(self):
        logs = {}
        for item in sorted(os.listdir(LOGS_DIR), reverse=True):
            path = os.path.join(LOGS_DIR, item)
            if os.path.isdir(path):
                logs[item] = os.listdir(path)
        return logs

    # ──────────── ACTIONS ────────────
    def handle_delete(self, parsed):
        target = parse_qs(parsed.query).get("target", [None])[0]
        if not target:
            self.send_json({"success": False})
            return
        safe = os.path.abspath(os.path.join(LOGS_DIR, target))
        if safe.startswith(os.path.abspath(LOGS_DIR)) and os.path.exists(safe):
            shutil.rmtree(safe) if os.path.isdir(safe) else os.remove(safe)
            self.send_json({"success": True})
        else:
            self.send_json({"success": False})

    def handle_restart(self, parsed):
        target = parse_qs(parsed.query).get("target", [None])[0]
        if target == "raspberry":
            subprocess.Popen(["sudo", "reboot"])
        elif target:
            subprocess.Popen(["pkill", "-f", target])
        self.send_json({"success": True})

# MIME
Handler.extensions_map.update({
    ".js": "application/javascript",
    ".css": "text/css",
})

# ──────────── START ────────────
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    logger.info(f"Serveur HTTP actif sur le port {PORT}")
    httpd.serve_forever()