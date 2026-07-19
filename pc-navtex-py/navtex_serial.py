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

import serial
import time

from navtex_message import NavtexMessage

BUFFER_SIZE = 1024

class NavtexSerial:
    def __init__(self, port):
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=38400,          # zostawiasz swoje ustawienia
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1,
            )
            time.sleep(1.0)   # <<< KLUCZOWE
            self.ser.write(b"$S\r\n")   # NASA NAVTEX wymaga CRLF
            self.line_buffer = ""
            self.lst_line_buffer = []
            self.is_message = False
            self.is_stored_messages = False
            self.is_version = False
            self.on_message = None

            # callbacki zamiast sygnałów Qt
            self.on_start_message = None
            self.on_end_of_message = None
            self.on_received_message = None
            self.on_end_of_stored_messages = None
            self.on_received_version = None
        except Exception as e:
            print("Błąd: nie można otworzyć portu NAVTEX:", e)
            self.ser = None
        self.db = None


    def debug(self, msg):
        #print(f"[DEBUG] {msg}")
        x = 1

    def read_data(self):
        if not self.ser:
            return  # port nie został otwarty

        try:
            bytes_available = self.ser.in_waiting
        except Exception as e:
            print("Błąd odczytu z portu NAVTEX:", e)
            self.ser = None
            return

        bytes_available = self.ser.in_waiting
        self.debug(f"BytesAvailable = {bytes_available}")
        if bytes_available < 1:
            return

        sum_bytes_read = 0
        while sum_bytes_read < bytes_available:
            bytes_to_read = min(bytes_available - sum_bytes_read, BUFFER_SIZE)
            data = self.ser.read(bytes_to_read)
            if not data:
                break
            sum_bytes_read += len(data)

            for c in data.decode("latin1"):
                if c == "\n":
                    # line = self.line_buffer
                    line = self.line_buffer.replace("\r", "")
                    self.line_buffer = ""
                    line = line.strip()  # usuwa \r, \n, spacje

                    if not line:
                        continue

                    if line.startswith("a") and line[1:].isdigit():
                        continue

                    self.debug(f"isMessage = {int(self.is_message)}   Line = {line}")

                    if line.startswith(">"):
                        self.is_message = True
                        self.lst_line_buffer = [line]
                        if not self.is_stored_messages and self.on_start_message:
                            self.on_start_message()
                        continue

                    if line.startswith("<"):
                        if self.on_end_of_message:
                            self.on_end_of_message()
                        if self.is_message:
                            self.lst_line_buffer.append(line)
                            self.handle_message(self.lst_line_buffer)
                        self.is_message = False
                        self.lst_line_buffer = []
                        continue

                    if line.startswith("end"):
                        self.is_message = False
                        self.is_stored_messages = False
                        self.lst_line_buffer = []
                        if self.on_end_of_stored_messages:
                            self.on_end_of_stored_messages()
                        continue

                    if line.startswith("Version"):
                        self.is_version = False
                        if self.on_received_version:
                            self.on_received_version(line)
                        continue

                    if self.is_message:
                        self.lst_line_buffer.append(line)
                else:
                    self.line_buffer += c

    def handle_message(self, lines):
        from navtex_message import NavtexMessage
        msg = NavtexMessage(lines)

        if msg.is_valid():
            if self.on_received_message:
                self.on_received_message(msg)
            if self.db:
                self.db.store_message(msg)

