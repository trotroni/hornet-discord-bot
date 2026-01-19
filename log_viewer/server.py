#!/usr/bin/env python3
import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import sys

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
        if parsed.path == "/logs":
            query = parse_qs(parsed.query)
            date_filter = query.get("date", [None])[0]
            type_filter = query.get("type", [None])[0]

            logs = {}
            for date_folder in sorted(os.listdir(LOG_DIR), reverse=True):
                if date_filter and date_folder != date_filter:
                    continue
                date_path = os.path.join(LOG_DIR, date_folder)
                if not os.path.isdir(date_path):
                    continue
                logs[date_folder] = {}
                for log_file in sorted(os.listdir(date_path)):
                    log_type = log_file.split("_")[0]
                    if type_filter and log_type != type_filter:
                        continue
                    try:
                        time_part = log_file.split("_")[2]
                        hh_mm = ":".join(time_part.split(":")[:2])
                    except IndexError:
                        hh_mm = "unknown"
                    if hh_mm not in logs[date_folder]:
                        logs[date_folder][hh_mm] = {}
                    if log_type not in logs[date_folder][hh_mm]:
                        logs[date_folder][hh_mm][log_type] = []
                    logs[date_folder][hh_mm][log_type].append(log_file)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(logs, indent=2).encode())
        else:
            super().do_GET()


with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Serving at http://0.0.0.0:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Serveur arrêté par Ctrl+C")