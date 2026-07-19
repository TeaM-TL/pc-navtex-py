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

        self.tree = ttk.Treeview(self, columns=("code", "info", "date"), show="headings")
        self.tree.heading("code", text="Code")
        self.tree.heading("info", text="Info")
        self.tree.heading("date", text="Received")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.after(200, self.poll_serial)

    def poll_serial(self):
        self.receiver.read_data()
        self.after(200, self.poll_serial)

    def on_received_message(self):
        # tu trzeba mieć dostęp do lst_line_buffer – możesz to rozbudować
        # na razie tylko odświeżamy listę z bazy
        self.refresh_messages()

    def refresh_messages(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in self.db.list_messages():
            _id, code, info, date = row
            self.tree.insert("", tk.END, values=(code, info, date))

if __name__ == "__main__":
    app = NavtexApp(port="/dev/ttyUSB0")  # dostosuj do swojego systemu
    app.mainloop()

