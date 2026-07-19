import serial
import time

from navtex_message import NavtexMessage

BUFFER_SIZE = 1024

class NavtexSerial:
    def __init__(self, port):
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

    def debug(self, msg):
        print(f"[DEBUG] {msg}")

    def read_data(self):
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
                    line = self.line_buffer
                    self.line_buffer = ""
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
            if self.on_message:
                self.on_message(msg)

            if self.on_received_message:
                self.on_received_message(msg)

