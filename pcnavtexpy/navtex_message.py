class NavtexMessage:
    def __init__(self, lines):
        self.lines = lines
        self.code = ""
        self.info = ""
        self.body = ""
        self.checkcode = ""

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

