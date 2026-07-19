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

from datetime import datetime
import hashlib

class NavtexMessage:
    def __init__(self, lines):
        self.lines = lines
        self.code = ""
        self.info = ""
        self.body = ""
        self.checkcode = ""
        self.receivedate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.valid = self._parse()

    def _parse(self):
        if not self.lines:
            return False

        # bardzo uproszczone – odpowiednik PCNMessage
        header = self.lines[0]  # linia z '>'
        footer = self.lines[-1] # linia z '<'

        self.code = header[1:].strip() if header.startswith(">") else ""
        self.checkcode = footer[1:].strip() if footer.startswith("<") else ""

        # środek wiadomości
        middle = self.lines[1:-1]
        self.body = "\n".join(middle)

        # info można wyciągnąć z pierwszej linii środka, jak w oryginale
        self.info = middle[0] if middle else ""

        return bool(self.code)

    def is_valid(self):
        return self.valid

    def md5sum(self):
        return hashlib.md5(self.body.encode("utf-8")).hexdigest()
