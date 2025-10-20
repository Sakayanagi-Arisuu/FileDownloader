import sqlite3
import os
from datetime import datetime
import json

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

def _load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    # default
    return {"download_folder": "downloads", "db_path": "downloads.db"}

_cfg = _load_config()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, _cfg.get("download_folder", "downloads"))
DB_PATH = os.path.join(BASE_DIR, _cfg.get("db_path", "downloads.db"))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        size INTEGER DEFAULT 0,
        downloads INTEGER DEFAULT 0,
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS download_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            filename TEXT,
            info TEXT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_file_record(filename: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO files (filename, added_at) VALUES (?, ?)", (filename, datetime.utcnow()))
    conn.commit()
    conn.close()

def list_files():
    # returns list of filenames (strings) ordered by newest
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    files = sorted(os.listdir(DOWNLOAD_FOLDER), key=lambda x: os.path.getmtime(os.path.join(DOWNLOAD_FOLDER, x)), reverse=True)
    return files

def log(action: str, filename: str, info: str = ''):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO download_logs (action, filename, info, ts) VALUES (?, ?, ?, ?)", (action, filename, info, datetime.utcnow()))
    conn.commit()
    conn.close()
def get_file_info(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(path):
        return None
    size = os.path.getsize(path)
    return {"filename": filename, "size": size, "added_at": datetime.fromtimestamp(os.path.getmtime(path))}

def increase_download_count(filename):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE files SET downloads = downloads + 1 WHERE filename = ?", (filename,))
    conn.commit()
    conn.close()

