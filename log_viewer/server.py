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
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == "/logs":
            # ... code existant pour lister les fichiers
            ...
        
        elif parsed.path.startswith("/read_log"):
            # lecture d'un fichier spécifique
            query = urllib.parse.parse_qs(parsed.query)
            file_path = query.get("file", [None])[0]
            if not file_path:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing file parameter")
                return

            # sécuriser pour éviter de lire en dehors de logs
            safe_path = os.path.abspath(os.path.join(LOG_DIR, file_path))
            if not safe_path.startswith(os.path.abspath(LOG_DIR)) or not os.path.isfile(safe_path):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Access denied")
                return

            with open(safe_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode())
        
        else:
            super().do_GET()

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Serving at http://0.0.0.0:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Serveur arrêté par Ctrl+C")