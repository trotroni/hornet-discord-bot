# log_viewer/server.py

#!/usr/bin/env python3
import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs

PORT = 8000
LOG_DIR = "./logs"

class Handler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/logs":
            # option date ou type si nécessaire
            query = parse_qs(parsed.query)
            date_filter = query.get("date", [None])[0]
            type_filter = query.get("type", [None])[0]

            # liste tous les logs
            logs = {}
            for date_folder in sorted(os.listdir(LOG_DIR), reverse=True):
                if date_filter and date_folder != date_filter:
                    continue
                date_path = os.path.join(LOG_DIR, date_folder)
                if not os.path.isdir(date_path):
                    continue
                logs[date_folder] = {}
                for log_file in sorted(os.listdir(date_path)):
                    # type = avant le _
                    log_type = log_file.split("_")[0]
                    if type_filter and log_type != type_filter:
                        continue
                    # extraire hh:mm
                    try:
                        time_part = log_file.split("_")[2]  # nude-core-bot_2026-01-19_17:40:16.log
                        hh_mm = ":".join(time_part.split(":")[:2])
                    except IndexError:
                        hh_mm = "unknown"
                    if hh_mm not in logs[date_folder]:
                        logs[date_folder][hh_mm] = {}
                    if log_type not in logs[date_folder][hh_mm]:
                        logs[date_folder][hh_mm][log_type] = []
                    logs[date_folder][hh_mm][log_type].append(log_file)
            
            # réponse JSON
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(logs, indent=2).encode())
        else:
            # servir fichiers statiques (index.html, script.js, style.css)
            super().do_GET()


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()