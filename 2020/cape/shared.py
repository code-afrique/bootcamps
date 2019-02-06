import time

class Shared():
    def __init__(self):
        self.curForm = None
        self.curBlock = None
        self.stmtBuffer = None
        self.exprBuffer = None
        self.saved = True
        self.cvtError = False
        self.confarea = None
        self.canvas = None
        self.keeping = False

    def startKeeping(self):
        assert not self.keeping
        self.keeping = True
        self.linebuf = []

    def keep(self, b):
        if self.keeping:
            self.linebuf.append(b)

    def stopKeeping(self):
        assert self.keeping
        self.keeping = False

    def slowPrint(self, s):
        print("at {}".format(s))
        time.sleep(2)
