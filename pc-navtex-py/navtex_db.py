# -*- coding: utf-8 -*-

"""
Copyright (c) 2026 Tomasz Łuczak

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sqlite3
from pathlib import Path


class NavtexDatabase:
    """Class for database connection and use"""

    def __init__(self, path="navtex.db"):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self._init_schema()

    def _init_schema(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT,
                info TEXT,
                body TEXT,
                checkcode TEXT,
                sum TEXT UNIQUE,
                receivedate TEXT
            )
        """)
        self.conn.commit()

    def store_message(self, msg):
        """Store in database"""
        cur = self.conn.cursor()
        md5 = msg.md5sum()

        # sprawdź, czy istnieje
        cur.execute("SELECT id FROM messages WHERE sum = ?", (md5,))
        if cur.fetchone():
            return  # duplikat → nie zapisujemy

        cur.execute(
            """
            INSERT INTO messages (code, info, body, checkcode, sum, receivedate)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (msg.code, msg.info, msg.body, msg.checkcode, md5, msg.receivedate),
        )

        self.conn.commit()

    def list_messages(self):
        """Get all from database"""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, code, info, receivedate FROM messages ORDER BY receivedate DESC"
        )
        return cur.fetchall()
