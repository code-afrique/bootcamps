class Shared():
    def __init__(self):
        self.curForm = None
        self.curBlock = None
        self.stmtBuffer = None
        self.exprBuffer = None
        self.saved = True
        self.cvtError = False
        self.confarea = None
