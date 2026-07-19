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

