# common/storage.py

import json
import os

DATA_DIR = "../compta-bot/data"

def _path(filename):
    return os.path.join(DATA_DIR, filename)

def load_json(filename):
    path = _path(filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filename, data):
    path = _path(filename)
    tmp_path = path + ".tmp"

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    os.replace(tmp_path, path)

def log_event(event):
    path = _path("events.log")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
