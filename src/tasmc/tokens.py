

class Token:
    lineno: int
    def __init__(self, lineno: int) -> None:
        self.lineno = lineno

class LabelToken(Token):
    def __init__(self, lineno: int, name: str) -> None:
        super().__init__(lineno)
        self.name = name

class JMPToken(Token):
    def __init__(self, lineno: int, label: str, inst_code: int) -> None:
        super().__init__(lineno)
        self.label = label
        self.inst = inst_code