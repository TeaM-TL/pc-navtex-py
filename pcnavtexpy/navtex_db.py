import sqlite3
from pathlib import Path

class NavtexDatabase:
    def __init__(self, path="navtex.db"):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self._init_schema()

    def _init_schema(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                code TEXT,
                info TEXT,
                body TEXT,
                checkcode TEXT,
                receivedate TEXT
            )
        """)
        self.conn.commit()

    def store_message(self, msg):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO messages (code, info, body, checkcode, receivedate)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (msg.code, msg.info, msg.body, msg.checkcode))
        self.conn.commit()

    def list_messages(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, code, info, receivedate FROM messages ORDER BY receivedate DESC")
        return cur.fetchall()

