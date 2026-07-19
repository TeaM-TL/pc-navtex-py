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

import tkinter as tk
from tkinter import ttk

from navtex_serial import NavtexSerial
from navtex_message import NavtexMessage
from navtex_db import NavtexDatabase

class NavtexApp(tk.Tk):
    def __init__(self, port):
        super().__init__()
        self.title("PC-Navtex Python/Tk")
        self.geometry("900x600")

        self.db = NavtexDatabase()
        self.receiver = NavtexSerial(port)
        self.receiver.on_received_message = self.on_received_message
        self.receiver.db = self.db

        # self.tree = ttk.Treeview(self, columns=("code", "info", "date"), show="headings")
        # self.tree.heading("code", text="Code")
        # self.tree.heading("info", text="Info")
        # self.tree.heading("date", text="Received")
        # self.tree.pack(fill=tk.BOTH, expand=True)
        # Frame for tree + scrollbar
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        self.tree = ttk.Treeview(
            frame,
            columns=("code", "info", "date"),
            show="headings",
            yscrollcommand=scrollbar.set
        )

        self.tree.heading("code", text="Code")
        self.tree.heading("info", text="Info")
        self.tree.heading("date", text="Received")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)


        # Connect scrollbar
        scrollbar.config(command=self.tree.yview)


        self.after(200, self.poll_serial)

        # --- Details panel ---
        details_frame = ttk.Frame(self)
        details_frame.pack(fill=tk.BOTH, expand=True)

        details_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.details_text = tk.Text(
            details_frame,
            wrap="word",
            yscrollcommand=details_scroll.set,
            height=12
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)

        details_scroll.config(command=self.details_text.yview)


    def poll_serial(self):
        self.receiver.read_data()
        self.after(200, self.poll_serial)

    def on_received_message(self, msg):
        # tu trzeba mieć dostęp do lst_line_buffer – możesz to rozbudować
        # na razie tylko odświeżamy listę z bazy
        #self.db.store_message(msg)
        self.tree.insert("", tk.END, values=(msg.code, msg.info, "now"))
        #self.refresh_messages()

    def refresh_messages(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in self.db.list_messages():
            _id, code, info, date = row
            self.tree.insert("", tk.END, values=(code, info, date))

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        code = item["values"][0]  # msg.code

        # Pobierz pełną treść wiadomości z bazy
        cur = self.db.conn.cursor()
        cur.execute("SELECT body FROM messages WHERE code = ?", (code,))
        row = cur.fetchone()

        self.details_text.delete("1.0", tk.END)

        if row:
            body = row[0]
            self.details_text.insert(tk.END, body)
        else:
            self.details_text.insert(tk.END, "Brak treści wiadomości.")


if __name__ == "__main__":
    app = NavtexApp(port="/dev/ttyUSB0")  # dostosuj do swojego systemu
    app.mainloop()

