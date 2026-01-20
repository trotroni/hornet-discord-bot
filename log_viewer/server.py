#!/usr/bin/env python3
import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import psutil
import subprocess

PORT = 8000
LOG_DIR = "/home/trotroni/nude-discord-bot/logs"

# --- Créer le dossier log du jour ---
today = datetime.now().strftime("%Y-%m-%d")
server_log_dir = os.path.join(LOG_DIR, today)
os.makedirs(server_log_dir, exist_ok=True)

time_str = datetime.now().strftime("%H:%M:%S")
server_log_file = os.path.join(server_log_dir, f"server_{today}_{time_str}.log")

# rediriger stdout et stderr du serveur dans ce fichier
sys.stdout = open(server_log_file, "a", buffering=1)
sys.stderr = sys.stdout

print(f"--- Server démarré le {datetime.now()} ---")

class Handler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/dashboard":
            # sert la page dashboard
            self.path = "/web/dashboard.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        elif path == "/api/status":
            # infos status général
            status = {
                "cpu_temp": self.get_cpu_temp(),
                "cpu_perc": psutil.cpu_percent(percpu=True),
                "ram_perc": psutil.virtual_memory().percent,
                "bots": {
                    "core": self.is_process_running("nude-core-bot"),
                    "compta": self.is_process_running("nude-compta-bot"),
                    "server": True  # ce serveur est actif
                },
                "uptime": psutil.boot_time()
            }
            self.send_json(status)

        elif path == "/api/logs":
            # retourne les logs triés par date → hh:mm → type → fichier
            logs_data = self.get_logs()
            self.send_json(logs_data)

        elif path.startswith("/api/delete"):
            # delete fichier ou dossier
            query = parse_qs(parsed.query)
            target = query.get("target", [None])[0]
            if target:
                safe_path = os.path.abspath(os.path.join(LOG_DIR, target))
                if safe_path.startswith(os.path.abspath(LOG_DIR)) and os.path.exists(safe_path):
                    if os.path.isfile(safe_path):
                        os.remove(safe_path)
                    else:
                        import shutil
                        shutil.rmtree(safe_path)
                    self.send_json({"success": True})
                    return
            self.send_json({"success": False})

        elif path.startswith("/api/restart"):
            # restart bot ou serveur ou raspberry
            query = parse_qs(parsed.query)
            target = query.get("target", [None])[0]
            if target == "raspberry":
                subprocess.Popen(["sudo", "reboot"])
            elif target in ["nude-core-bot", "nude-compta-bot"]:
                subprocess.Popen(["pkill", "-f", target])
                # à ce stade start_bot.bash redémarrera automatiquement ou on peut le relancer ici
            self.send_json({"success": True})

        else:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def get_cpu_temp(self):
        try:
            res = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
            t = res.stdout.strip().split('=')[1].replace("'C", "")
            return float(t)
        except:
            return None

    def is_process_running(self, name):
        return any(name in p.name() or name in " ".join(p.cmdline()) for p in psutil.process_iter())

    def get_logs(self):
        logs = {}
        if not os.path.exists(LOG_DIR):
            return logs
        for date in sorted(os.listdir(LOG_DIR), reverse=True):
            date_path = os.path.join(LOG_DIR, date)
            if os.path.isdir(date_path):
                logs[date] = {}
                for file in sorted(os.listdir(date_path)):
                    # fichier nom : type_date_time.log
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


Handler.extensions_map.update({
    ".js": "application/javascript",
    ".css": "text/css",
})

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Dashboard & server HTTP sur le port {PORT}")
    httpd.serve_forever()