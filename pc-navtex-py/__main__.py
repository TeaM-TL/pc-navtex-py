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

        # --- Główny układ: lewa kolumna + prawa kolumna ---
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Status NAVTEX ---
        self.status_label = ttk.Label(left_frame, text="NAVTEX nie podłączony", foreground="red")
        self.status_label.pack(anchor="w", pady=5, padx=5)


        # --- Filter bar ---
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(anchor="w", pady=5, padx=5)

        filter_frame.pack(fill=tk.X)

        ttk.Label(filter_frame, text="Channel:").pack(side=tk.LEFT, padx=5)

        for ch in ("ALL", "A", "B", "C", "D", "E", "F", "G", "K", "L"):
            btn = ttk.Button(filter_frame, text=ch, width=4,
                     command=lambda c=ch: self.apply_filter(c))
            btn.pack(side=tk.TOP, anchor="w", pady=2)

        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Treeview
        self.tree = ttk.Treeview(right_frame, 
            columns=("code", "info", "date"),
            show="headings"
        )
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            frame,
            columns=("code", "info", "date"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
                # Connect scrollbar
        scrollbar.config(command=self.tree.yview)

        style = ttk.Style()
        style.configure("A.Treeview", background="#d0e4ff")   # jasnoniebieski
        style.configure("B.Treeview", background="#d8ffd0")   # jasnozielony
        style.configure("C.Treeview", background="#ffe4b3")   # jasnopomarańczowy
        style.configure("D.Treeview", background="#ffd0d0")   # jasnoczerwony

        # Kolorowanie kanałów NAVTEX
        self.tree.tag_configure("A", foreground="blue")
        self.tree.tag_configure("B", foreground="green")
        self.tree.tag_configure("C", foreground="orange")
        self.tree.tag_configure("D", foreground="red")
        self.tree.tag_configure("E", foreground="purple")
        self.tree.tag_configure("F", foreground="brown")
        self.tree.tag_configure("G", foreground="darkgreen")
        self.tree.tag_configure("K", foreground="darkblue")
        self.tree.tag_configure("L", foreground="gray")


        self.tree.heading("code", text="Code")
        self.tree.heading("info", text="Info")
        self.tree.heading("date", text="Received")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)


        self.after(200, self.poll_serial)

        # --- Details panel ---
        details_frame = ttk.Frame(right_frame)
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

        self.apply_filter("ALL")


    def poll_serial(self):
        try:
        # jeśli port jest None → nie próbujemy czytać
            if self.receiver.ser:
                self.receiver.read_data()
                self.set_navtex_status(True)
            else:
                self.set_navtex_status(False)
        except Exception as e:
            print("Błąd NAVTEX:", e)
            self.set_navtex_status(False)

        self.after(200, self.poll_serial)


    def on_received_message(self, msg):
        # kanał to druga litera kodu
        channel = msg.code[1].upper() if len(msg.code) > 1 else "?"

        style = f"{channel}.Treeview"

        self.tree.insert(
            "",
            tk.END,
            values=(msg.code, msg.info, "now"),
            tags=(style,)
        )


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


    def apply_filter(self, channel):
        # wyczyść tabelę
        for row in self.tree.get_children():
            self.tree.delete(row)

        cur = self.db.conn.cursor()

        if channel == "ALL":
            cur.execute("SELECT code, info, receivedate FROM messages ORDER BY receivedate DESC")
        else:
            # kanał to DRUGA litera kodu
            cur.execute("""
                SELECT code, info, receivedate
                FROM messages
                WHERE substr(code, 2, 1) = ?
                ORDER BY receivedate DESC
            """, (channel,))

        for code, info, date in cur.fetchall():
            ch = code[1].upper() if len(code) > 1 else ""
            self.tree.insert("", tk.END, values=(code, info, date), tags=(ch,))

    def set_navtex_status(self, connected: bool):
        if connected:
            self.status_label.config(text="NAVTEX podłączony", foreground="green")
        else:
            self.status_label.config(text="NAVTEX nie podłączony", foreground="red")



if __name__ == "__main__":
    app = NavtexApp(port="/dev/ttyUSB0")  # dostosuj do swojego systemu
    app.mainloop()

