import time
import queue
import tokenize
import ast
import io
import keyword
import tkinter as tk
import pmod
import block
import pp

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
        self.search_string = None

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
                    print("tokval: " + str(tokval))
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
        print("START")
        pp.pprint(tree)
        print("FINISH")
        n = pmod.nodeEval(tree)

        # extract keywords and comments
        keywords, comments = self.extract(code, mode=mode)
        print("START KW")
        print(keywords)
        print("FINISH KW")

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

    def scrollUpdate(self):
        self.scrollable.scrollUpdate()

    def setForm(self, f):
        if (self.curForm != None):
            self.curForm.grid_forget()
            self.curForm.destroy()
        self.curForm = f
        if f:
            f.grid(row=0, column=0, sticky=tk.E)
            f.update()
            f.catchKeys()

    def setBlock(self, b):
        if self.curBlock:
            self.curBlock.configure(bd=self.bd, highlightbackground=self.hlb, highlightcolor=self.hlc, highlightthickness=self.hlt)
        self.curBlock = b
        if b:
            # save the properties of b that we're about the change
            # so we can restore them later
            self.bd = b.cget('bd')
            self.hlb = b.cget('highlightbackground')
            self.hlc = b.cget('highlightcolor')
            self.hlt = b.cget('highlightthickness')
            # change the properties
            b.configure(bd=2, highlightbackground='red', highlightcolor='red', highlightthickness=2)
            b.update()
            # Generate a form for the new box
            b.genForm()
            # See if we need to move the scrollbars to make sure the box
            # is visible within the canvas.  self.canvas points to
            # to the entire image, while self.canvas.parent is
            # the visible region of the image.
            # 
            # Considering only the y-axis: let Th be the total height, and
            # Vh be the visible height.  The relative size of the scroller
            # in the scrollbar is therefore Vh / Th.
            # 
            # If we set the bottom of scroller within the vertical scroll
            # bar to 0, we see the range [ 0, Vh ].  If we set the top of
            # the scroller to 1, we see the range [ Th - Vh, Th ].  This
            # latter position corresponds to the bottom of the scroller
            # being at position (Th - Vh) / Th.
            # 
            # So to get point Vh / 2 in the middle, we set the scroll bar
            # to 0, and to get point (2Th - Vh)/2 in the middle we set the
            # scroll bar to (Th - Vh) / Th.
            # 
            # Let (x1, y1) = (Vh / 2, 0), and let (x2, y2) =
            # ((2Th - Vh) / 2, (Th - Vh) / Th).  The line that passes through
            # both points is y = (y2 - y1) / (x2 - x1) * (x - x1) + y1.
            # y2 - y1 = (Th - Vh) / Th.  x2 - x1 = Th - Vh.   So the slope
            # is 1 / Th.  So the final equation is:
            #   y = (x - Vh / 2) / Th
            # this is the visible canvas.  self.canvas is the entire image.
            c = self.canvas.parent
            # these are the coordinates of the box within the visible area
            bv = self.getBoxWithin(c, b)
            # this is the size of the visible image
            cv = self.getBoxWithin(c, c)
            if (not self.intersects(bv, cv)):
                # these are the coordinates of the box within the entire image
                bt = self.getBoxWithin(self.canvas, b)
                # this is the size of the entire image
                ct = self.getBoxWithin(self.canvas, self.canvas)
                # the halfway point of the box
                px = ((bt[0] + bt[2]) / 2.0)
                py = ((bt[1] + bt[3]) / 2.0)
                # the desired setting of the scrollers
                qx = ((px - (cv[2] / 2.0)) / (ct[2] - ct[0]))
                qy = ((py - (cv[3] / 2.0)) / (ct[3] - ct[1]))
                # don't overscroll
                if (qx < 0):
                    qx = 0
                if (qx > 1):
                    qx = 1
                if (qy < 0):
                    qy = 0
                if (qy > 1):
                    qy = 1
                c.xview(tk.MOVETO, qx)
                c.yview(tk.MOVETO, qy)
        self.scrollUpdate()

    # see if box b1 intersects with box b2
    def intersects(self, b1, b2):
        return (not ((b1[2] < b2[0]) or (b1[0] > b2[2]) or (b1[3] < b2[1]) or (b1[1] > b2[3])))

    # widget inner is a widget within widget outer.  Return the box inner with
    # coordinates relative to outer
    def getBoxWithin(self, outer, inner):
        (x, y) = self.getCoord(outer, inner)
        return (x, y, (x + inner.winfo_width()), (y + inner.winfo_height()))

    # widget inner is a widget within widget outer.  Return the coordinates
    # of inner relative to outer
    def getCoord(self, outer, inner):
        if (outer is inner):
            return (0, 0)
        else:
            (x, y) = self.getCoord(outer, inner.parent)
            return ((x + inner.winfo_x()), (y + inner.winfo_y()))

    # save for undo later
    def save(self):
        if self.program != None:
            print("save for later")
            self.cvtError = True
            n = self.program.toNode()
            self.stack.append((n, self.curBlock, self.curForm))
            if self.search_string != None:
                self.program.contains(self.search_string)

    def undo(self):
        if len(self.stack) <= 1:
            print("nothing to undo")
            return
        self.stack.pop()
        self.program.grid_forget()
        (n, curBlock, curForm) = self.stack[-1]
        # print("undo", curBlock)
        self.program = block.ModuleBlock(self.scrollable.stuff, self, n)
        self.program.grid(sticky=tk.W)
        # self.setBlock(curBlock)
        self.saved = False
