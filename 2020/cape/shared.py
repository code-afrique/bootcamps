import time
import queue
import tokenize
import ast
import io
import keyword
import tkinter as tk
import pmod
import block

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
        self.program = None
        self.stack = []
        self.trap = False

    def startKeeping(self):
        assert not self.keeping
        self.keeping = True
        self.linebuf = []

    def keep(self, b):
        if self.keeping:
            index = len(self.linebuf)
            self.linebuf.append(b)
            return index
        else:
            return 0

    def stopKeeping(self):
        assert self.keeping
        self.keeping = False

    def slowPrint(self, s):
        print("at {}".format(s))
        time.sleep(2)

    def extract(self, code, mode="exec"):
        keywords = queue.Queue()
        if mode == "exec":
            keywords.put(("module", 0, 0))
        comments = {}
        fd = io.StringIO(code)
        for (toktype, tokval, begin, end, line) in tokenize.generate_tokens(fd.readline):
            if (toktype == tokenize.COMMENT):
                (row, col) = begin
                comments[row] = tokenize.untokenize([(toktype, tokval)])
            elif (toktype == tokenize.NAME):
                (row, col) = begin
                if keyword.iskeyword(tokval):
                    keywords.put((tokval, row, col))
        return (keywords, comments)

    def getComment(self, text):
        assert (text[0] == "#")
        if len(text) > 1 and text[1] == " ":
            return text[2:]
        return text[1:]

    def parse(self, code, show_offsets=True, mode='exec'):
        # tree = pparse.pparse(code, mode="eval")
        mod = ast.parse(code, mode=mode)
        tree = ast.dump(mod, include_attributes=True)
        n = pmod.nodeEval(tree)

        # extract keywords and comments
        keywords, comments = self.extract(code, mode=mode)

        # find the line numbers corresponding to keywords
        n.merge(keywords)

        # now we can merge comments back into the AST, sort of
        for (lineno, text) in comments.items():
            comment = self.getComment(text)
            (type, b, i) = n.findLine(lineno)
            if type == "row":
                # print("ROW", lineno, i)
                row = b.rows[i]
                lin = row.lineno
            else:
                # print("CLAUSE", lineno, i)
                assert type == "clause"
                row = b
                lin = i
            if (lineno < lin):
                row.commentU += comment + '\n'
            else:
                row.commentR = comment
        return n

    # save for undo later
    def save(self):
        if self.program != None:
            print("save for later")
            self.cvtError = True
            n = self.program.toNode()
            self.stack.append(n)

    def undo(self):
        if len(self.stack) == 0:
            print("nothing to undo")
            return
        print("undo")
        self.program.grid_forget()
        n = self.stack.pop()
        self.program = block.ModuleBlock(self.scrollable.stuff, self, n)
        self.program.grid(sticky=tk.W)
        self.scrollable.scrollUpdate()
        self.saved = False
