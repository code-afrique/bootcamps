import tkinter as tk
import tkinter.messagebox
import io
from form import *
from node import *
import pparse
import pmod

class Block(tk.Frame):

    def __init__(self, parent, shared, borderwidth=0):
        super().__init__(parent, borderwidth=borderwidth, relief=tk.SUNKEN)
        self.parent = parent
        self.shared = shared
        self.isTop = False
        self.isWithinDef = (False if (parent == None) else parent.isWithinDef)
        self.isWithinLoop = (False if (parent == None) else parent.isWithinLoop)
        self.isWithinStore = (False if (parent == None) else parent.isWithinStore)    # lvalue

    # All blocks consist of a number of rows.  Some rows are blocks themselves
    # Each row currently translates in one line of output.  We use this fact
    # to find the offending block in error messages by line number.
    # findLine(n) returns (True, RowBlock) if the RowBlock is at row n
    # of a SeqBlock, or (False, m) with the number of rows in this block.
    def findLine(lineno):
        return (True, self)

    def scrollUpdate(self):
        self.shared.scrollable.scrollUpdate()

    def setForm(self, f):
        if (self.shared.curForm != None):
            self.shared.curForm.grid_forget()
        self.shared.curForm = f
        if f:
            f.grid(row=0, column=0, sticky=tk.E)
            f.update()
            f.catchKeys()

    def genForm(self):
        print("no genForm {}".format(self))

    def setBlock(self, b):
        if self.shared.curBlock:
            self.shared.curBlock.configure(bd=self.shared.bd, highlightbackground=self.shared.hlb, highlightcolor=self.shared.hlc, highlightthickness=self.shared.hlt)
        self.shared.curBlock = b
        if b:
            # save the properties of b that we're about the change
            # so we can restore them later
            b.shared.bd = b.cget("bd")
            b.shared.hlb = b.cget("highlightbackground")
            b.shared.hlc = b.cget("highlightcolor")
            b.shared.hlt = b.cget("highlightthickness")

            # change the properties
            b.configure(bd=2, highlightbackground="red", highlightcolor="red", highlightthickness=2)
            b.update()

            # Generate a form for the new box
            b.genForm()

            # See if we need to move the scrollbars to make sure the box
            # is visible within the canvas.  self.shared.canvas points to
            # to the entire image, while self.shared.canvas.parent is
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

            # this is the visible canvas.  self.shared.canvas is the entire
            # image.
            c = self.shared.canvas.parent

            # these are the coordinates of the box within the visible area
            bv = self.getBoxWithin(c, b)

            # this is the size of the visible image
            cv = self.getBoxWithin(c, c)

            if (not self.intersects(bv, cv)):
                # these are the coordinates of the box within the entire image
                bt = self.getBoxWithin(self.shared.canvas, b)

                # this is the size of the entire image
                ct = self.getBoxWithin(self.shared.canvas, self.shared.canvas)

                # the halfway point of the box
                px = (bt[0] + bt[2]) / 2.0
                py = (bt[1] + bt[3]) / 2.0

                # the desired setting of the scrollers
                qx = (px - cv[2] / 2.0) / (ct[2] - ct[0])
                qy = (py - cv[3] / 2.0) / (ct[3] - ct[1])

                # don't overscroll
                if qx < 0:
                    qx = 0
                if qx > 1:
                    qx = 1
                if qy < 0:
                    qy = 0
                if qy > 1:
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

    def needsSaving(self):
        self.shared.saved = False

    def cut(self, doCopy):
        if doCopy:
            self.copy()
        if isinstance(self, RowBlock):
            self.delStmt()
        elif isinstance(self.parent, RowBlock):
            self.parent.delStmt()
        elif isinstance(self, ExpressionBlock):
            self.delExpr()
        elif isinstance(self.parent, ExpressionBlock):
            self.parent.delExpr()
        else:
            print("Can't cut {0} {1}".format(self.parent, self))

    def copy(self):
        self.shared.cvtError = True
        self.shared.exprBuffer = self.toNode()
        self.clipboard_clear()
        f = io.StringIO("")
        self.shared.exprBuffer.print(f, 0)
        code = f.getvalue()
        self.clipboard_append(code)

    def paste(self):
        tk.messagebox.showinfo("Paste Error", "paste only allowed into uninitialized expression or rows")

    def delExpr(self):
        self.copyExpr()
        self.parent.delExpr()
        print("expression deleted")

    def goLeft(self):
        if (self.isTop or (self.parent == None) or self.parent.isTop):
            return
        p = self.parent
        if isinstance(p, ExpressionBlock):
            p = p.parent
        if isinstance(p, HeaderBlock):
            p = p.parent
        return p

    def goRight(self):
        return self

    def goUp(self):
        return self

    def goDown(self):
        return self

    def newContainerBlock(self, parent, node):
        return ContainerBlock(parent, self.shared, node)

    def newModuleBlock(self, parent, node):
        return ModuleBlock(parent, self.shared, node)

    def newPassBlock(self, parent, node):
        return PassBlock(parent, self.shared, node)

    def newEmptyBlock(self, parent, node):
        return EmptyBlock(parent, self.shared, node)

    def newDefClauseBlock(self, parent, node):
        return DefClauseBlock(parent, self.shared, node)

    def newLambdaBlock(self, parent, node):
        return LambdaBlock(parent, self.shared, node)

    def newClassClauseBlock(self, parent, node):
        return ClassClauseBlock(parent, self.shared, node)

    def newBasicClauseBlock(self, parent, node):
        return BasicClauseBlock(parent, self.shared, node)

    def newIfClauseBlock(self, parent, node):
        return IfClauseBlock(parent, self.shared, node)

    def newIfBlock(self, parent, node):
        return IfBlock(parent, self.shared, node)

    def newTryBlock(self, parent, node):
        return TryBlock(parent, self.shared, node)

    def newWithClauseBlock(self, parent, node):
        return WithClauseBlock(parent, self.shared, node)

    def newWhileBlock(self, parent, node):
        return WhileBlock(parent, self.shared, node)

    def newForBlock(self, parent, node):
        return ForBlock(parent, self.shared, node)

    def newReturnBlock(self, parent, node):
        return ReturnBlock(parent, self.shared, node)

    def newDelBlock(self, parent, node):
        return DelBlock(parent, self.shared, node)

    def newAssertBlock(self, parent, node):
        return AssertBlock(parent, self.shared, node)

    def newBreakBlock(self, parent, node):
        return BreakBlock(parent, self.shared, node)

    def newContinueBlock(self, parent, node):
        return ContinueBlock(parent, self.shared, node)

    def newImportBlock(self, parent, node):
        return ImportBlock(parent, self.shared, node)

    def newImportfromBlock(self, parent, node):
        return ImportfromBlock(parent, self.shared, node)

    def newGlobalBlock(self, parent, node):
        return GlobalBlock(parent, self.shared, node)

    def newAssignBlock(self, parent, node):
        return AssignBlock(parent, self.shared, node)

    def newAugassignBlock(self, parent, node):
        return AugassignBlock(parent, self.shared, node)

    def newBinaryopBlock(self, parent, node):
        return BinaryopBlock(parent, self.shared, node)

    def newListopBlock(self, parent, node):
        return ListopBlock(parent, self.shared, node)

    def newUnaryopBlock(self, parent, node):
        return UnaryopBlock(parent, self.shared, node)

    def newSubscriptBlock(self, parent, node):
        return SubscriptBlock(parent, self.shared, node)

    def newCallBlock(self, parent, node):
        return CallBlock(parent, self.shared, node)

    def newIfelseBlock(self, parent, node):
        return IfelseBlock(parent, self.shared, node)

    def newListBlock(self, parent, node):
        return ListBlock(parent, self.shared, node)

    def newListcompBlock(self, parent, node):
        return ListcompBlock(parent, self.shared, node)

    def newDictBlock(self, parent, node):
        return DictBlock(parent, self.shared, node)

    def newTupleBlock(self, parent, node):
        return TupleBlock(parent, self.shared, node)

    def newAttrBlock(self, parent, node):
        return AttrBlock(parent, self.shared, node)

    def newEvalBlock(self, parent, node):
        return EvalBlock(parent, self.shared, node)

    def newNumberBlock(self, parent, what):
        return NumberBlock(parent, self.shared, what)

    def newConstantBlock(self, parent, what):
        return ConstantBlock(parent, self.shared, what)

    def newNameBlock(self, parent, what):
        return NameBlock(parent, self.shared, what)

    def newStringBlock(self, parent, what):
        return StringBlock(parent, self.shared, what)

    def newBytesBlock(self, parent, what):
        return BytesBlock(parent, self.shared, what)

    def newRowBlock(self, parent, what):
        return RowBlock(parent, self.shared, what)

    def newExpressionBlock(self, parent, what):
        return ExpressionBlock(parent, self.shared, what)

    def newSeqBlock(self, parent, rows):
        return SeqBlock(parent, self.shared, rows)

class HeaderBlock(Block):

    def __init__(self, parent, shared):
        super().__init__(parent, shared)

class NameBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.vname = tk.StringVar()
        self.btn = tk.Button(self, textvariable=self.vname, fg="blue", width=0, command=self.cb)
        self.vname.set(node.what)
        self.btn.grid(row=0, column=0)

    def genForm(self):
        f = NameForm(self.shared.confarea, self)
        self.setForm(f)
    # f.entry.focus()

    def cb(self):
        self.setBlock(self)

    def setName(self, v):
        self.vname.set(v)
        self.btn.config(width=0)
        self.needsSaving()
        self.setBlock(self.goLeft())

    def toNode(self):
        v = self.vname.get()
        if (not v.isidentifier()):
            if (not self.shared.cvtError):
                self.setBlock(self)
                tk.messagebox.showinfo("Convert Error", "Fix bad variable name")
                self.shared.cvtError = True
        return NameNode(v)

class NumberBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.value = tk.StringVar()
        self.value.set(node.what)
        self.btn = tk.Button(self, textvariable=self.value, fg="blue", width=0, command=self.cb)
        self.btn.grid(row=0, column=0)

    def genForm(self):
        f = NumberForm(self.shared.confarea, self)
        self.setForm(f)
    # f.entry.focus()

    def cb(self):
        self.setBlock(self)

    def setValue(self, v):
        self.value.set(v)
        self.btn.config(width=0)
        self.needsSaving()
        self.setBlock(self.goLeft())

    def toNode(self):
        v = self.value.get()
        try:
            float(v)
        except ValueError:
            if (not self.shared.cvtError):
                self.setBlock(self)
                tk.messagebox.showinfo("Convert Error", "Fix bad number")
                self.shared.cvtError = True
        return NumberNode(v)

class ConstantBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.value = tk.StringVar()
        self.value.set(node.what)
        self.btn = tk.Button(self, textvariable=self.value, fg="purple", width=0, command=self.cb)
        self.btn.grid(row=0, column=0)

    def genForm(self):
        self.setForm(ConstantForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return ConstantNode(self.value.get())

class StringBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.string = tk.StringVar()
        tk.Button(self, text="\"", command=self.cb).grid(row=0, column=0)
        self.btn = tk.Button(self, textvariable=self.string, fg="green", width=0, command=self.cb)
        self.string.set(node.what)
        self.btn.grid(row=0, column=1)
        tk.Button(self, text="\"", command=self.cb).grid(row=0, column=2)

    def genForm(self):
        f = StringForm(self.shared.confarea, self)
        self.setForm(f)
    # f.entry.focus()

    def cb(self):
        self.setBlock(self)

    def setContents(self, s):
        self.string.set(s)
        self.btn.config(width=0)
        self.scrollUpdate()
        self.needsSaving()
        self.setBlock(self.goLeft())

    def toNode(self):
        return StringNode(self.string.get())

class BytesBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.bytes = tk.StringVar()
        tk.Button(self, text="b'", command=self.cb).grid(row=0, column=0)
        self.btn = tk.Button(self, textvariable=self.bytes, fg="green", width=0, command=self.cb)
        self.bytes.set(node.what.decode())
        self.btn.grid(row=0, column=1)
        tk.Button(self, text="'", command=self.cb).grid(row=0, column=2)

    def genForm(self):
        f = BytesForm(self.shared.confarea, self)
        self.setForm(f)
    # f.entry.focus()

    def cb(self):
        self.setBlock(self)

    def setContents(self, s):
        self.bytes.set(s)
        self.btn.config(width=0)
        self.scrollUpdate()
        self.needsSaving()

    def toNode(self):
        return BytesNode(self.bytes.get().encode())

class SubscriptBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.isWithinStore = False
        self.array = ExpressionBlock(self, shared, node.array)
        self.array.grid(row=0, column=0)
        tk.Button(self, text="[", command=self.cb).grid(row=0, column=1)
        self.colon1 = tk.Button(self, text=":", command=self.cb)
        self.colon2 = tk.Button(self, text=":", command=self.cb)
        self.eol = tk.Button(self, text="]", command=self.cb)
        (self.isSlice, lower, upper, step) = node.slice
        if (lower == None):
            self.lower = None
        else:
            self.lower = lower.toBlock(self, self)
        if self.isSlice:
            if (upper == None):
                self.upper = None
            else:
                self.upper = upper.toBlock(self, self)
            if (step == None):
                self.step = None
            else:
                self.step = step.toBlock(self, self)
        else:
            self.upper = self.step = None
        self.updateGrid()

    def cb(self):
        self.setBlock(self)

    def genForm(self):
        self.setForm(SubscriptForm(self.shared.confarea, self))

    def updateGrid(self):
        column = 2
        if (self.lower != None):
            self.lower.grid(row=0, column=column)
            column += 1
        if self.isSlice:
            self.colon1.grid(row=0, column=column)
            column += 1
            if (self.upper != None):
                self.upper.grid(row=0, column=column)
                column += 1
            if (self.step != None):
                self.colon2.grid(row=0, column=column)
                column += 1
                self.step.grid(row=0, column=column)
                column += 1
        self.eol.grid(row=0, column=column)

    def addLower(self):
        self.lower = ExpressionBlock(self, self.shared, None)
        self.updateGrid()
        self.setBlock(self.lower)

    def addUpper(self):
        self.upper = ExpressionBlock(self, self.shared, None)
        self.updateGrid()
        self.setBlock(self.upper)

    def addStep(self):
        self.step = ExpressionBlock(self, self.shared, None)
        self.updateGrid()
        self.setBlock(self.step)

    def toNode(self):
        return SubscriptNode(self.array.toNode(), (self.isSlice, (None if (self.lower == None) else self.lower.toNode()), (None if (self.upper == None) else self.upper.toNode()), (None if (self.step == None) else self.step.toNode())))

class AttrBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.isWithinStore = False
        if (node == None):
            self.array = ExpressionBlock(self, shared, None)
        else:
            self.array = node.array.toBlock(self, self)
        self.array.grid(row=0, column=0)
        tk.Button(self, text=".", command=self.cb).grid(row=0, column=1)
        if (node == None):
            self.ref = NameBlock(self, shared, NameNode(""))
        else:
            self.ref = node.ref.toBlock(self, self)
        self.ref.grid(row=0, column=2)

    def cb(self):
        self.setBlock(self)

    def genForm(self):
        self.setForm(AttrForm(self.shared.confarea, self))

    def toNode(self):
        return AttrNode(self.array.toNode(), self.ref.toNode())

class UnaryopBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        left = tk.Button(self, text=node.op, fg="purple", width=0, command=self.cb)
        left.grid(row=0, column=0)
        self.right = ExpressionBlock(self, shared, node.right)
        self.op = node.op
        self.right.grid(row=0, column=1)

    def genForm(self):
        self.setForm(UnaryopForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return UnaryopNode(self.right.toNode(), self.op)

class BinaryopBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.left = ExpressionBlock(self, shared, node.left)
        self.middle = tk.Button(self, text=node.op, fg="purple", width=0, command=self.cb)
        self.right = ExpressionBlock(self, shared, node.right)
        self.op = node.op
        self.left.grid(row=0, column=0)
        self.middle.grid(row=0, column=1)
        self.right.grid(row=0, column=2)

    def genForm(self):
        self.setForm(BinaryopForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return BinaryopNode(self.left.toNode(), self.right.toNode(), self.op)

class ListopBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.values = [ExpressionBlock(self, shared, v) for v in node.values]
        self.ops = node.ops
        n = len(node.ops)
        for i in range(n):
            self.values[i].grid(row=0, column=(2 * i))
            op = tk.Button(self, text=node.ops[i], fg="purple", width=0, command=self.cb)
            op.grid(row=0, column=((2 * i) + 1))
        self.values[n].grid(row=0, column=(2 * n))

    def genForm(self):
        self.setForm(ListopForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return ListopNode([v.toNode() for v in self.values], self.ops)

# A clause block consists of a header and a body
class ClauseBlock(Block):
    def __init__(self, parent, shared, node, minimized, title):
        super().__init__(parent, shared)

        self.node = SeqNode([RowNode(PassNode())]) if node == None else node
        self.title = title
        self.hdr = HeaderBlock(self, shared)
        self.colon = tk.Button(self.hdr, highlightbackground="yellow", text="+", command=self.minmax)
        self.body = None
        self.hdr.grid(row=0, column=0, sticky=tk.W)
        self.colon.grid(row=0, column=1000, sticky=tk.W)
        self.minimized = True
        self.row = None

        # TODO.  May need to get rid of this
        if not minimized:
            self.minmax()

    def genForm(self):
        self.setForm(ClauseForm(self.shared.confarea, self))

    def goRight(self):
        return self if self.body == None else self.body

    def goUp(self):
        if ((self.row != None) and (self.row > 0)):
            return self.parent.clauses[(self.row - 1)]
        else:
            return self

    def goDown(self):
        if ((self.row != None) and (self.row < (len(self.parent.clauses) - 1))):
            return self.parent.clauses[(self.row + 1)]
        else:
            return self

    def minmax(self):
        if self.minimized:
            if self.body == None:
                self.body = self.node.toBlock(self, self)
            self.body.grid(row=1, column=0, columnspan=2, sticky=tk.W)
            self.update()
            self.minimized = False
            self.colon.configure(highlightbackground="white", text=":")
        else:
            self.body.grid_forget()
            self.minimized = True
            self.colon.configure(highlightbackground="yellow", text="+")
        self.scrollUpdate()

    def toNode(self):
        if self.minimized:
            return self.node
        else:
            return self.body.toNode()

# A 'basic' clause consists of a header and a body.  It's used for 'module', 'else', and
# 'finally' clauses.
class BasicClauseBlock(ClauseBlock):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared, node.body, False, "basic clause")
        self.type = node.type
        tk.Button(self.hdr, text=node.type, fg="red", width=0, command=self.cb).grid(row=0, column=0)
        self.hdr.grid(row=0, sticky=tk.W)

    def genForm(self):
        self.setForm(ClauseForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return BasicClauseNode(self.type, self.body.toNode())

# An 'if' clause consists of a condition and a body.  It's used for 'if', 'elif', and 'while'
# clauses.
class IfClauseBlock(ClauseBlock):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared, node.body, False, "if clause")
        if node.cond == None:
            self.cond = ExpressionBlock(self.hdr, shared, None)
        else:
            self.cond = node.cond.toBlock(self.hdr, self)
        self.type = node.type
        self.cond.grid(row=0, column=1)
        tk.Button(self.hdr, text=self.type, fg="red", width=0, command=self.cb).grid(row=0, column=0)
        self.cond.grid(row=0, column=1)
        self.hdr.grid(row=0, sticky=tk.W)

    def genForm(self):
        self.setForm(ClauseForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def goRight(self):
        return self.cond

    def toNode(self):
        return IfClauseNode(self.type, self.cond.toNode(), self.body.toNode())

# A compound block consists of a list of clause blocks.
class CompoundBlock(Block):

    def __init__(self, parent, shared):
        super().__init__(parent, shared)
        self.clauses = []

    def gridUpdate(self):
        for row in range(len(self.clauses)):
            self.clauses[row].row = row

    def goRight(self):
        return self.clauses[0]

class ModuleBlock(CompoundBlock):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)

        if (node == None):
            self.clauses = [BasicClauseBlock(self, self.shared, BasicClauseNode("module", None))]
        else:
            self.clauses = [BasicClauseBlock(self, self.shared, BasicClauseNode("module", node.body))]

        self.clauses[0].grid()

    def goRight(self):
        return self.clauses[0]

    def genForm(self):
        self.setForm(ModuleForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return ModuleNode(self.clauses[0].body.toNode())

# A container block is a compound block with a single clause.  Examples are class, def,
# and with statements
class ContainerBlock(CompoundBlock):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)

        self.clauses = [node.body.toBlock(self, self)]
        self.clauses[0].grid()

    def goRight(self):
        return self.clauses[0]

    def genForm(self):
        self.setForm(ContainerForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return ContainerNode(self.clauses[0].toNode())

class ClassClauseBlock(ClauseBlock):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared, node.body, node.body != None, "def clause")
        self.cname = tk.StringVar()
        self.cname.set(node.name)
        btn = tk.Button(self.hdr, text="class", fg="red", width=0, command=self.cb)
        btn.grid(row=0, column=0)
        self.name = tk.Button(self.hdr, textvariable=self.cname, fg="blue", command=self.cb)
        self.name.grid(row=0, column=1)
        tk.Button(self.hdr, text="(", command=self.cb).grid(row=0, column=2)
        self.eol = tk.Button(self.hdr, text=")", command=self.cb)
        self.bases = []
        if (node != None):
            for base in node.bases:
                self.addBaseClass(base)

        self.setHeader()
        self.hdr.grid()

    def goRight(self):
        return self.clause

    def genForm(self):
        self.setForm(ClassForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def classUpdate(self, mname):
        self.cname.set(mname)
        self.needsSaving()

    def addBaseClass(self, node):
        if (node == None):
            base = ExpressionBlock(self.hdr, self.shared, None)
        else:
            base = ExpressionBlock(self.hdr, self.shared, node)
        self.bases.append(base)
        self.setHeader()
        self.needsSaving()

    def setHeader(self):
        column = 3
        for i in range(len(self.bases)):
            if (i != 0):
                tk.Button(self.hdr, text=",", command=self.cb).grid(row=0, column=column)
                column += 1
            self.bases[i].grid(row=0, column=column)
            column += 1
        self.eol.grid(row=0, column=column)

    def toNode(self):
        v = self.cname.get()
        if (not v.isidentifier()):
            if (not self.shared.cvtError):
                self.setBlock(self)
                tk.messagebox.showinfo("Convert Error", "Fix bad class name")
                self.shared.cvtError = True
        return ClassNode(v, [b.toNode() for b in self.bases], self.body.toNode())

class CallBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        if (node == None):
            self.func = ExpressionBlock(self, shared, None)
        else:
            self.func = ExpressionBlock(self, shared, node.func)
        self.func.grid(row=0, column=0)
        tk.Button(self, text="(", width=0, command=self.cb).grid(row=0, column=1)
        self.eol = tk.Button(self, text=")", width=0, command=self.cb)
        self.args = []
        self.keywords = []
        if (node != None):
            for arg in node.args:
                self.addArg(arg)
            for kw in node.keywords:
                self.addKeyword(kw)
        self.gridUpdate()

    def genForm(self):
        self.setForm(CallForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def addArg(self, node):
        if (node == None):
            arg = ExpressionBlock(self, self.shared, None)
        else:
            arg = ExpressionBlock(self, self.shared, node)
        self.args.append(arg)

    def newArg(self, node):
        self.addArg(node)
        self.gridUpdate()
        self.needsSaving()

    def addNamedArg(self, name):
        self.addKeyword((name, None))

    def addKeyword(self, kw):
        (key, val) = kw
        if (val == None):
            arg = ExpressionBlock(self, self.shared, None)
        else:
            arg = ExpressionBlock(self, self.shared, val)
        self.keywords.append((key, arg))

    def gridUpdate(self):
        first = True
        column = 2
        for arg in self.args:
            if first:
                first = False
            else:
                tk.Button(self, text=",", width=0, command=self.cb).grid(row=0, column=column)
                column += 1
            arg.grid(row=0, column=column)
            column += 1
        for (k, v) in self.keywords:
            if first:
                first = False
            else:
                tk.Button(self, text=",", width=0, command=self.cb).grid(row=0, column=column)
                column += 1
            tk.Button(self, text=k, width=0, command=self.cb).grid(row=0, column=column)
            column += 1
            tk.Button(self, text="=", width=0, command=self.cb).grid(row=0, column=column)
            column += 1
            v.grid(row=0, column=column)
            column += 1
        self.eol.grid(row=0, column=column)

    def toNode(self):
        return CallNode(self.func.toNode(), [arg.toNode() for arg in self.args], [(k, v.toNode()) for (k, v) in self.keywords])

class ListBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        tk.Button(self, text="[", width=0, command=self.cb).grid(row=0, column=0)
        self.eol = tk.Button(self, text="]", width=0, command=self.cb)
        self.entries = []
        if (node != None):
            for e in node.entries:
                self.addEntry(e)
        self.gridUpdate()

    def genForm(self):
        self.setForm(ListForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def addEntry(self, node):
        if (node == None):
            e = ExpressionBlock(self, self.shared, None)
        else:
            e = ExpressionBlock(self, self.shared, node)
        self.entries.append(e)
        self.gridUpdate()
        self.needsSaving()

    def gridUpdate(self):
        for i in range(len(self.entries)):
            if (i != 0):
                tk.Button(self, text=",", width=0, command=self.cb).grid(row=0, column=((2 * i) + 1))
            self.entries[i].grid(row=0, column=((2 * i) + 2))
        self.eol.grid(row=0, column=((2 * len(self.entries)) + 2))

    def toNode(self):
        return ListNode([entry.toNode() for entry in self.entries])

class ListcompBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.node = node
        tk.Button(self, text="[", width=0, command=self.cb).grid(row=0, column=0)
        self.elt = node.elt.toBlock(self, self)
        self.elt.grid(row=0, column=1)
        column = 2
        self.generators = []
        for (target, iter, ifs, is_async) in node.generators:
            tk.Button(self, text=" for ", width=0, command=self.cb).grid(row=0, column=column)
            column += 1
            target.toBlock(self, self).grid(row=0, column=column)
            column += 1
            tk.Button(self, text=" in ", width=0, command=self.cb).grid(row=0, column=column)
            column += 1
            iter.toBlock(self, self).grid(row=0, column=column)
            column += 1
            for i in ifs:
                tk.Button(self, text=" if ", width=0, command=self.cb).grid(row=0, column=column)
                column += 1
                i.toBlock(self, self).grid(row=0, column=column)
                column += 1
        tk.Button(self, text="]", width=0, command=self.cb).grid(row=0, column=column)

    def genForm(self):
        self.setForm(ListcompForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        # TODO fake.  Should probably extract from blocks
        return self.node

class DictBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.keys = []
        self.values = []
        tk.Button(self, text="{", width=0, command=self.cb).grid(row=0, column=0)
        self.eol = tk.Button(self, text="}", width=0, command=self.cb)
        if (node != None):
            for i in range(len(node.keys)):
                self.addEntry(node.keys[i], node.values[i])
        self.gridUpdate()

    def genForm(self):
        self.setForm(DictForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def addEntry(self, key, value):
        if (key == None):
            k = ExpressionBlock(self, self.shared, None)
        else:
            k = ExpressionBlock(self, self.shared, key)
        self.keys.append(k)
        if (value == None):
            v = ExpressionBlock(self, self.shared, None)
        else:
            v = ExpressionBlock(self, self.shared, value)
        self.values.append(v)
        self.gridUpdate()
        self.needsSaving()

    def gridUpdate(self):
        column = 1
        for i in range(len(self.keys)):
            if (i != 0):
                tk.Button(self, text=",", width=0, command=self.cb).grid(row=0, column=column)
                column += 1
            self.keys[i].grid(row=0, column=column)
            column += 1
            tk.Button(self, text=":", width=0, command=self.cb).grid(row=0, column=column)
            column += 1
            self.values[i].grid(row=0, column=column)
            column += 1
        self.eol.grid(row=0, column=column)

    def toNode(self):
        return DictNode([k.toNode() for k in self.keys], [v.toNode() for v in self.values])

class TupleBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        tk.Button(self, text="(", width=0, command=self.cb).grid(row=0, column=0)
        self.eol = tk.Button(self, text=")", width=0, command=self.cb)
        self.entries = []
        if (node != None):
            for e in node.entries:
                self.addEntry(e)
        self.gridUpdate()

    def genForm(self):
        self.setForm(TupleForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def addEntry(self, node):
        if (node == None):
            e = ExpressionBlock(self, self.shared, None)
        else:
            e = ExpressionBlock(self, self.shared, node)
        self.entries.append(e)
        self.gridUpdate()
        self.needsSaving()

    def gridUpdate(self):
        column = 1
        n = len(self.entries)
        for i in range(n):
            if (i != 0):
                tk.Button(self, text=",", width=0, command=self.cb).grid(row=0, column=column)
                column += 1
            self.entries[i].grid(row=0, column=column)
            column += 1
        if (n == 1):
            tk.Button(self, text=",", width=0, command=self.cb).grid(row=0, column=column)
            column += 1
        self.eol.grid(row=0, column=column)

    def toNode(self):
        return TupleNode([entry.toNode() for entry in self.entries])

class ExpressionBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared, borderwidth=1)
        self.button = tk.Button(self, text="?", width=0, command=self.cb)
        if ((node == None) or (node.what == None)):
            self.what = None
            self.button.grid()
        else:
            assert isinstance(node, ExpressionNode)
            self.what = node.what.toBlock(self, self)
            self.what.grid()

    def goRight(self):
        return (self if (self.what == None) else self.what)

    def goLeft(self):
        return super().goLeft()

    def delExpr(self):
        self.setValue(None)

    def genForm(self):
        f = ExpressionForm(self.shared.confarea, self)
        self.setForm(f)

    def cb(self):
        self.setBlock(self)

    def setValue(self, v):
        if (v == None):
            if (self.what != None):
                self.what.grid_forget()
                self.what = None
                self.button.grid()
            self.setBlock(self)
        else:
            if (self.what == None):
                self.button.grid_forget()
            else:
                self.what.grid_forget()
            self.what = v.toBlock(self, self)
            self.what.grid()
            self.setBlock(self.what)
            self.needsSaving()

    def exprNumber(self, v):
        self.setValue(NumberNode(v))
        self.shared.curForm.entry.focus()

    def exprConstant(self, value):
        self.setValue(ConstantNode(value))
        self.setBlock(self.goLeft())

    def exprString(self):
        self.setValue(StringNode(""))
        self.shared.curForm.entry.focus()

    def exprName(self, v):
        self.setValue(NameNode(v))
        self.shared.curForm.entry.focus()

    def exprSubscript(self, isSlice):
        self.setValue(SubscriptNode(None, (isSlice, (None if isSlice else ExpressionNode(None)), None, None)))
        self.setBlock(self.what.array)

    def exprAttr(self):
        self.setValue(AttrNode(ExpressionNode(None), NameNode("")))
        self.setBlock(self.what.array)

    def exprList(self):
        self.setValue(ListNode([]))

    def exprTuple(self):
        self.setValue(TupleNode([]))

    def exprDict(self):
        self.setValue(DictNode([], []))

    def exprUnaryop(self, op):
        self.setValue(UnaryopNode(None, op))
        self.setBlock(self.what.right)

    def exprBinaryop(self, op):
        self.setValue(BinaryopNode(None, None, op))
        self.setBlock(self.what.left)

    def exprCall(self):
        self.setValue(CallNode(ExpressionNode(None), [], []))
        self.setBlock(self.what.func)

    def exprIfelse(self):
        self.setValue(IfelseNode(ExpressionNode(None), ExpressionNode(None), ExpressionNode(None)))

    def paste(self):
        try:
            code = self.clipboard_get()
            tree = pparse.pparse(code, mode="eval")
            n = pmod.nodeEval(tree)
            assert isinstance(n, ExpressionNode)
            self.setValue(n.what)
        except SyntaxError:
            tk.messagebox.showinfo("Paste Error", "not a Python expression")
            print("invalid Python expression: '{}'".format(code))

    def toNode(self):
        if (self.what == None):
            if (not self.shared.cvtError):
                self.setBlock(self)
                tk.messagebox.showinfo("Convert Error", "Fix uninitialized expression")
                self.shared.cvtError = True
            return ExpressionNode(NameNode("__CAPE_UNINITIALIZED__"))
        return ExpressionNode(self.what.toNode())

class AssignBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        if (node == None):
            self.isWithinStore = True
            self.targets = [ExpressionBlock(self, shared, None)]
            self.isWithinStore = False
            self.value = ExpressionBlock(self, shared, None)
        else:
            self.isWithinStore = True
            self.targets = [t.toBlock(self, self) for t in node.targets]
            self.isWithinStore = False
            self.value = node.value.toBlock(self, self)
        column = 0
        for t in self.targets:
            t.grid(row=0, column=column)
            column += 1
            tk.Button(self, text="=", fg="purple", command=self.cb).grid(row=0, column=column)
            column += 1
        self.value.grid(row=0, column=column)

    def goRight(self):
        return self.targets[0]

    def genForm(self):
        self.setForm(AssignForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return AssignNode([t.toNode() for t in self.targets], self.value.toNode())

class IfelseBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        if (node == None):
            self.cond = ExpressionBlock(self, shared, None)
            self.ifTrue = ExpressionBlock(self, shared, None)
            self.ifFalse = ExpressionBlock(self, shared, None)
        else:
            self.cond = ExpressionBlock(self, shared, node.cond)
            self.ifTrue = ExpressionBlock(self, shared, node.ifTrue)
            self.ifFalse = ExpressionBlock(self, shared, node.ifFalse)
        self.ifTrue.grid(row=0, column=0)
        tk.Button(self, text="if", fg="purple", command=self.cb).grid(row=0, column=1)
        self.cond.grid(row=0, column=2)
        tk.Button(self, text="else", fg="purple", command=self.cb).grid(row=0, column=3)
        self.ifFalse.grid(row=0, column=4)

    def genForm(self):
        self.setForm(IfelseForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return IfelseNode(self.cond.toNode(), self.ifTrue.toNode(), self.ifFalse.toNode())

class AugassignBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.isWithinStore = True
        self.left = ExpressionBlock(self, shared, node.left)
        middle = tk.Button(self, text=node.op, fg="purple", command=self.cb)
        self.isWithinStore = False
        self.right = ExpressionBlock(self, shared, node.right)
        self.op = node.op
        self.left.grid(row=0, column=0)
        middle.grid(row=0, column=1)
        self.right.grid(row=0, column=2)

    def genForm(self):
        self.setForm(AugassignForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return AugassignNode(self.left.toNode(), self.right.toNode(), self.op)

class PassBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.rowblk = parent
        btn = tk.Button(self, text="pass", fg="red", width=0, command=self.cb)
        btn.grid(row=0, column=0)

    def genForm(self):
        f = PassForm(self.shared.confarea, self)
        self.setForm(f)

    def cb(self):
        self.setBlock(self)

    def paste(self):
        self.parent.paste()

    def stmtEmpty(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = EmptyBlock(self.rowblk, self.shared, None)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk)
        self.needsSaving()

    def stmtAugassign(self, op):
        self.rowblk.what.grid_forget()
        if (op == "="):
            self.rowblk.what = AssignBlock(self.rowblk, self.shared, None)
            self.setBlock(self.rowblk.what.targets[0])
        else:
            self.rowblk.what = AugassignBlock(self.rowblk, self.shared, AugassignNode(None, None, op))
            self.setBlock(self.rowblk.what.left)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.needsSaving()

    def stmtEval(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = EvalBlock(self.rowblk, self.shared, None)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.expr)
        self.needsSaving()

    def stmtIf(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = IfBlock(self.rowblk, self.shared, None)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.clauses[0])
        self.needsSaving()

    def stmtWhile(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = WhileBlock(self.rowblk, self.shared, None)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.cond)
        self.needsSaving()

    def stmtDef(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ContainerBlock(self.rowblk, self.shared, ContainerNode(DefClauseNode("", [], [], None)))
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.clauses[0])
        self.needsSaving()
        self.shared.curForm.entry.focus()

    def stmtClass(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ContainerBlock(self.rowblk, self.shared, ContainerNode(ClassClauseNode("", [], None)))
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.clauses[0])
        self.needsSaving()
        self.shared.curForm.entry.focus()

    def stmtWith(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ContainerBlock(self.rowblk, self.shared, ContainerNode(WithClauseNode([], None)))
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.clauses[0])
        self.needsSaving()

    def stmtFor(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ForBlock(self.rowblk, self.shared, None)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.target)
        self.needsSaving()

    def stmtReturn(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ReturnBlock(self.rowblk, self.shared, None)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.expr)
        self.needsSaving()

    def stmtDel(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = DelBlock(self.rowblk, self.shared, None)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.targets[0])
        self.needsSaving()

    def stmtCall(self):
        self.rowblk.what.grid_forget()
        n = EvalNode(ExpressionNode(CallNode(ExpressionNode(None), [], [])))
        self.rowblk.what = n.toBlock(self.rowblk, self)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.expr.what.func)
        self.needsSaving()
        self.shared.curForm.entry.focus()

    def stmtPrint(self):
        self.rowblk.what.grid_forget()
        n = EvalNode(ExpressionNode(CallNode(ExpressionNode(NameNode("print")), [ExpressionNode(None)], [])))
        self.rowblk.what = n.toBlock(self.rowblk, self)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.expr.what.args[0])
        self.needsSaving()

    def stmtAssert(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = AssertBlock(self.rowblk, self.shared, None)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.test)
        self.needsSaving()

    def stmtBreak(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = BreakBlock(self.rowblk, self.shared, None)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what)
        self.needsSaving()

    def stmtContinue(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ContinueBlock(self.rowblk, self.shared, None)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what)
        self.needsSaving()

    def stmtGlobal(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = GlobalBlock(self.rowblk, self.shared, None)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.vars[0])
        self.shared.curForm.entry.focus()
        self.needsSaving()

    def stmtImport(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ImportBlock(self.rowblk, self.shared, None)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.module)
        self.shared.curForm.entry.focus()
        self.needsSaving()

    def stmtPasteOld(self):
        if (self.shared.stmtBuffer != None):
            self.rowblk.what.grid_forget()
            self.rowblk.what = self.shared.stmtBuffer.toBlock(self.rowblk, self.rowblk)
            self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
            self.setBlock(self.rowblk.what)
        self.needsSaving()

    def toNode(self):
        return PassNode()

class EmptyBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
    # btn = tk.Button(self, text="", fg="red", width=0, command=self.cb)
    # btn.grid(row=0, column=0)

    def genForm(self):
        self.setForm(EmptyForm(self.shared.confarea, self))

    def paste(self):
        self.parent.paste()

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return EmptyNode()

class EvalBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        if (node == None):
            self.expr = ExpressionBlock(self, shared, None)
        else:
            self.expr = ExpressionBlock(self, shared, node.what)
        self.expr.grid()

    def genForm(self):
        self.setForm(EvalForm(self.shared.confarea, self))

    def goRight(self):
        return self.expr

    def toNode(self):
        return EvalNode(self.expr.toNode())

class ReturnBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        tk.Button(self, text="return", fg="red", command=self.cb).grid(row=0, column=0)
        if ((node == None) or (node.what == None)):
            self.expr = None
        else:
            self.expr = ExpressionBlock(self, shared, node.what)
            self.expr.grid(row=0, column=1)

    def genForm(self):
        self.setForm(ReturnForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def returnValue(self):
        self.expr = ExpressionBlock(self, self.shared, None)
        self.expr.grid(row=0, column=1)

    def toNode(self):
        return ReturnNode((None if (self.expr == None) else self.expr.toNode()))

class LambdaBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        # fake...
        self.node = node
        tk.Button(self, text="lambda", fg="red", command=self.cb).grid(row=0, column=0)
        column = 1
        d = len(node.defaults)
        for i in range(len(node.args)):
            if (i > 0):
                tk.Button(self, text=",", fg="red", command=self.cb).grid(row=0, column=column)
                column += 1
            tk.Button(self, text=node.args[i], fg="red", command=self.cb).grid(row=0, column=column)
            column += 1
            if (i >= d):
                tk.Button(self, text="=", fg="red", command=self.cb).grid(row=0, column=column)
                column += 1
                node.defaults[(i - d)].toBlock(self, self).grid(row=0, column=column)
                column += 1
        tk.Button(self, text=":", fg="red", command=self.cb).grid(row=0, column=column)
        column += 1
        node.body.toBlock(self, self).grid(row=0, column=column)

    def genForm(self):
        self.setForm(LambdaForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return self.node

class DelBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        tk.Button(self, text="del", fg="red", command=self.cb).grid(row=0, column=0)
        self.isWithinStore = True
        if (node == None):
            self.targets = [ExpressionBlock(self, shared, None)]
        else:
            self.targets = [ExpressionBlock(self, shared, t) for t in node.targets]
        first = True
        column = 1
        for t in self.targets:
            if first:
                first = False
            else:
                tk.Button(self, text=",", fg="red", command=self.cb).grid(row=0, column=column)
                column += 1
            t.grid(row=0, column=column)
            column += 1

    def genForm(self):
        self.setForm(ReturnForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return DelNode([t.toNode() for t in self.targets])

class AssertBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        tk.Button(self, text="assert", fg="red", command=self.cb).grid(row=0, column=0)
        if (node == None):
            self.test = ExpressionBlock(self, shared, None)
            self.msg = None
        else:
            self.test = ExpressionBlock(self, shared, node.test)
            self.msg = (None if (node.msg == None) else ExpressionBlock(self, shared, node.msg))
        self.test.grid(row=0, column=1)
        if (self.msg != None):
            tk.Button(self, text=",", fg="red", command=self.cb).grid(row=0, column=2)
            self.msg.grid(row=0, column=3)

    def genForm(self):
        self.setForm(AssertForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return AssertNode(self.test.toNode(), (None if (self.msg == None) else self.msg.toNode()))

class BreakBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        tk.Button(self, text="break", fg="red", command=self.cb).grid(row=0, column=0)

    def genForm(self):
        self.setForm(BreakForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return BreakNode()

class ContinueBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        tk.Button(self, text="continue", fg="red", command=self.cb).grid(row=0, column=0)

    def genForm(self):
        self.setForm(ContinueForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return ContinueNode()

class GlobalBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        tk.Button(self, text="global", fg="red", command=self.cb).grid(row=0, column=0)
        if (node == None):
            self.vars = [NameBlock(self, shared, NameNode(""))]
        else:
            self.vars = [n.toBlock(self, self) for n in node.names]
        column = 1
        for i in range(len(self.vars)):
            if (i > 0):
                tk.Button(self, text=",", command=self.cb).grid(row=0, column=column)
                column += 1
            self.vars[i].grid(row=0, column=column)
            column += 1

    def genForm(self):
        self.setForm(GlobalForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return GlobalNode([v.toNode() for v in self.vars])

class ImportBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        tk.Button(self, text="import", fg="red", command=self.cb).grid(row=0, column=0)
        if (node == None):
            self.module = NameBlock(self, shared, NameNode(""))
            self.alias = None
        else:
            self.module = node.name.toBlock(self, self)
            self.alias = (None if (node.asname == None) else node.asname.toBlock(self, self))
        self.module.grid(row=0, column=1)
        if (self.alias != None):
            tk.Button(self, text=" as ", fg="red", command=self.cb).grid(row=0, column=2)
            self.alias.grid(row=0, column=3)

    def genForm(self):
        self.setForm(ImportForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return ImportNode(self.module.toNode(), (None if (self.alias == None) else self.alias.toNode()))

class ImportfromBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.node = node
        tk.Button(self, text="from", fg="red", command=self.cb).grid(row=0, column=0)
        self.module = node.module.toBlock(self, self)
        self.module.grid(row=0, column=1)
        tk.Button(self, text="import", fg="red", command=self.cb).grid(row=0, column=2)
        first = True
        column = 3
        for (name, alias) in node.names:
            if first:
                first = False
            else:
                tk.Button(self, text=",", fg="red", command=self.cb).grid(row=0, column=column)
                column += 1
            name.toBlock(self, self).grid(row=0, column=column)
            column += 1
            if (alias != None):
                tk.Button(self, text=" as ", fg="red", command=self.cb).grid(row=0, column=column)
                column += 1
                alias.grid(row=0, column=column)
                column += 1

    def genForm(self):
        self.setForm(ImportForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return self.node

class RowBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared, borderwidth=1)
        self.row = None
        self.comment = tk.StringVar()
        menu = tk.Button(self, text="-", width=3, command=self.listcmd)
        menu.grid(row=0, column=0, sticky=tk.W)
        if (node == None):
            self.what = PassBlock(self, self.shared, None)
        else:
            self.what = node.what.toBlock(self, self)
        self.what.grid(row=0, column=1, sticky=tk.W)
        if ((node != None) and (node.comment != None)):
            self.comment.set(("#" + node.comment))
        tk.Button(self, textvariable=self.comment, fg="brown", command=self.listcmd).grid(row=0, column=2, sticky=(tk.N + tk.W))

    def goRight(self):
        return (self if (self.what == None) else self.what)

    def goUp(self):
        if ((self.row != None) and (self.row > 0)):
            return self.parent.rows[(self.row - 1)]
        else:
            return self

    def goDown(self):
        if ((self.row != None) and (self.row < (len(self.parent.rows) - 1))):
            return self.parent.rows[(self.row + 1)]
        else:
            return self

    def setComment(self, comment):
        if (comment == ""):
            self.comment.set("")
        else:
            self.comment.set(("#" + comment))

    def genForm(self):
        self.setForm(RowForm(self.shared.confarea, self))

    def addStmt(self):
        self.parent.insert((self.row + 1))
        self.needsSaving()

    def insrtStmt(self):
        self.parent.insert(self.row)
        self.needsSaving()

    def upStmt(self):
        self.parent.moveUp(self.row)
        self.needsSaving()

    def downStmt(self):
        self.parent.moveDown(self.row)
        self.needsSaving()

    def delStmt(self):
        self.parent.delRow(self.row)
        print("statement deleted")
        self.needsSaving()

    def paste(self):
        try:
            code = self.clipboard_get()
            try:
                tree = pparse.pparse(code, mode="single")
                n = pmod.nodeEval(tree)
                assert isinstance(n, RowNode)
                if (not (isinstance(self.what, EmptyBlock) or isinstance(self.what, PassBlock))):
                    tk.messagebox.showinfo("Paste Error", "can only overwrite empty or pass statements")
                else:
                    self.what.grid_forget()
                    self.what = n.what.toBlock(self, self)
                    self.what.grid(row=0, column=1, sticky=tk.W)
                    self.setBlock(self.what)
                    self.needsSaving()
            except SyntaxError:
                tk.messagebox.showinfo("Paste Error", "not a Python statement")
                print("invalid Python statement: '{}'".format(code))
        except e:
            tk.messagebox.showinfo("Paste Error", e)

    def listcmd(self):
        self.setBlock(self)

    def toNode(self):
        r = RowNode(self.what.toNode(), 0)
        c = self.comment.get()
        if (c != ""):
            assert (c[0] == "#")
            r.comment = c[1:]
        return r

# The parent of a SeqBlock is always a ClauseBlock, which helps with navigating
# There's something to be said to merge the concepts of SeqBlock and ClauseBlock, but
# that might require creating ClauseNodes for all types of clauses.
class SeqBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.rows = []
        if (node == None):
            self.insert(0)
        else:
            for i in range(len(node.rows)):
                self.rows.append(RowBlock(self, shared, node.rows[i]))
            self.gridUpdate()

    def findLine(n):
        lineno = 0
        for i in range(len(node.rows)):
            (status, x) = self.rows[i].findLine(n)
            if status:
                return (True, x)
            lineno += x
        return (False, lineno)

    def goRight(self):
        return self.rows[0]

    def genForm(self):
        self.setForm(SeqForm(self.shared.confarea, self))

    def insert(self, row):
        rb = RowBlock(self, self.shared, None)
        self.rows.insert(row, rb)
        self.gridUpdate()
        self.setBlock(rb.what)

    def delRow(self, row):
        for i in range(len(self.rows)):
            self.rows[i].grid_forget()
        if (row < len(self.rows)):
            del self.rows[row]
        if (len(self.rows) == 0):
            self.insert(0)
        else:
            if (row >= len(self.rows)):
                row = (len(self.rows) - 1)
            self.setBlock(self.rows[row])
        self.gridUpdate()

    def moveUp(self, row):
        if (row == 0):
            return
        tmp = self.rows[(row - 1)]
        self.rows[(row - 1)] = self.rows[row]
        self.rows[row] = tmp
        self.gridUpdate()

    def moveDown(self, row):
        if (row == (len(self.rows) - 1)):
            return
        tmp = self.rows[(row + 1)]
        self.rows[(row + 1)] = self.rows[row]
        self.rows[row] = tmp
        self.gridUpdate()

    def gridUpdate(self):
        for row in range(len(self.rows)):
            self.rows[row].grid(row=row, column=0, sticky=tk.W)
            self.rows[row].row = row

    def toNode(self):
        return SeqNode([r.toNode() for r in self.rows])

class DefClauseBlock(ClauseBlock):

    def __init__(self, parent, shared, node):
        parent.isWithinDef = True
        super().__init__(parent, shared, node.body, node.body != None, "def clause")
        self.mname = tk.StringVar()
        self.mname.set(node.name)
        self.args = node.args
        self.defaults = [d.toBlock(self.clause.hdr, self) for d in node.defaults]

        self.setHeader()
        self.hdr.grid()

    def setHeader(self):
        hdr = self.hdr
        btn = tk.Button(hdr, text="def", fg="red", width=0, command=self.cb)
        btn.grid(row=0, column=0)
        self.name = tk.Button(hdr, textvariable=self.mname, fg="blue", command=self.cb)
        self.name.grid(row=0, column=1)
        tk.Button(hdr, text="(", command=self.cb).grid(row=0, column=2)
        column = 3
        d = (len(self.args) - len(self.defaults))
        for i in range(len(self.args)):
            if (i != 0):
                tk.Button(hdr, text=",", command=self.cb).grid(row=0, column=column)
                column += 1
            tk.Button(hdr, text=self.args[i], fg="blue", command=self.cb).grid(row=0, column=column)
            column += 1
            if (i >= d):
                tk.Button(hdr, text="=", command=self.cb).grid(row=0, column=column)
                column += 1
                self.defaults[(i - d)].grid(row=0, column=column)
                column += 1
        tk.Button(hdr, text=")", command=self.cb).grid(row=0, column=column)

    def genForm(self):
        f = DefClauseForm(self.shared.confarea, self)
        self.setForm(f)
    # f.entry.focus()

    def cb(self):
        self.setBlock(self)

    def defUpdate(self, mname, args):
        self.mname.set(mname)
        self.args = args
        self.setHeader()
        self.needsSaving()

    def toNode(self):
        v = self.mname.get()
        if (not v.isidentifier()):
            if (not self.shared.cvtError):
                self.setBlock(self)
                tk.messagebox.showinfo("Convert Error", "Fix bad function name")
                self.shared.cvtError = True
        return DefClauseNode(v, self.args, [d.toNode() for d in self.defaults], self.body.toNode())

class IfBlock(CompoundBlock):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        if (node == None):
            self.clauses = [IfClauseBlock(self, shared, IfClauseNode("if", None, None))]
            self.hasElse = False
        else:
            self.clauses = [n.toBlock(self, self) for n in node.clauses]
            self.hasElse = node.hasElse
        self.gridUpdate()

    def genForm(self):
        self.setForm(IfForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def addElse(self):
        if not self.hasElse:
            clause = BasicClauseBlock(self, self.shared, BasicClauseNode("else", None))
            self.clauses.append(clause)
            self.gridUpdate()
            self.setBlock(clause.body.rows[0].what)
            self.hasElse = True
            self.needsSaving()

    def removeElse(self):
        if self.hasElse:
            self.clauses[-1].grid_forget()
            del self.clauses[-1]
            self.setBlock(self)
            self.hasElse = False
            self.needsSaving()

    def insertElif(self):
        clause = IfClauseBlock(self, self.shared, IfClauseNode("elif", None, None))
        n = len(self.clauses)
        self.clauses.insert(n - 1 if self.hasElse else n, clause)
        self.gridUpdate()
        self.setBlock(clause.body.rows[0].what)
        self.needsSaving()

    def gridUpdate(self):
        super().gridUpdate()
        for i in range(len(self.clauses)):
            self.clauses[i].grid(row=i, sticky=tk.W)
        self.scrollUpdate()

    def toNode(self):
        return IfNode([c.toNode() for c in self.clauses], self.hasElse)

class WhileBlock(CompoundBlock):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.isWithinLoop = True
        if (node == None):
            self.clauses = [IfClauseBlock(self, shared, IfClauseNode("while", None, None))]
            self.isWithinLoop = False
            self.hasElse = False
        else:
            self.clauses = [node.clauses[0].toBlock(self, self)]
            self.isWithinLoop = False
            if node.hasElse:
                self.clauses.append([node.clauses[1].toBlock(self, self)])
            self.hasElse = node.hasElse
        self.gridUpdate()

    def genForm(self):
        self.setForm(WhileForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def addElse(self):
        if not self.hasElse:
            clause = BasicClauseBlock(self, self.shared, BasicClauseNode("else", None))
            self.clauses.append(clause)
            self.gridUpdate()
            self.setBlock(clause.body.rows[0].what)
            self.hasElse = True
            self.needsSaving()

    def removeElse(self):
        if self.hasElse:
            self.clauses[-1].grid_forget()
            del self.clauses[-1]
            self.setBlock(self)
            self.hasElse = False
            self.needsSaving()

    def gridUpdate(self):
        super().gridUpdate()
        for i in range(len(self.clauses)):
            self.clauses[i].grid(row=i, sticky=tk.W)
        self.scrollUpdate()

    def toNode(self):
        return WhileNode([c.toNode() for c in self.clauses], self.hasElse)

class TryBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared, borderwidth=1)

        if node == None:
            self.clause = ClauseBlock(self, self.shared, SeqNode([RowNode(PassNode())]), False, "'try' clause in a 'try' statement")
            self.orelse = None
            self.finalbody = None
        else:
            self.clause = ClauseBlock(self, shared, node.body, False, "'try' clause in a 'try' statement")
        hdr = self.clause.hdr
        tk.Button(hdr, text="try", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        self.clause.grid(row=0, sticky=tk.W)

        self.handlers = []
        if node != None:
            for (type, name, body) in node.handlers:
                clause = ClauseBlock(self, shared, body, False, "'except' clause in a 'try' statement")
                hdr = clause.hdr
                self.handlers.append((clause, (None if (type == None) else type.toBlock(hdr, self)), (None if (name == None) else NameBlock(hdr, shared, NameNode(name)))))
            row = 2
            for (clause, type, name) in self.handlers:
                hdr = clause.hdr
                tk.Button(hdr, text="except", fg="red", width=0, command=self.cb).grid(row=0, column=0)
                column = 1
                if type != None:
                    type.grid(row=0, column=column)
                    column += 1
                    if (name != None):
                        tk.Button(hdr, text="as", fg="red", width=0, command=self.cb).grid(row=0, column=column)
                        column += 1
                        name.grid(row=0, column=column)
                        column += 1
                clause.grid(row=row, column=0, sticky=tk.W)
                row += 1
            if (node.orelse == None):
                self.orelse = None
            else:
                self.orelse = ClauseBlock(self, shared, node.orelse, False, "'else' clause in a 'try' statement")
                hdr = self.orelse.hdr
                tk.Button(hdr, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
                self.orelse.grid(row=row, sticky=tk.W)
                row += 1
            if (node.finalbody == None):
                self.finalbody = None
            else:
                self.finalbody = ClauseBlock(self, shared, node.finalbody, False, "'finally' clause in a 'try' statement")
                hdr = self.finalbody.hdr
                tk.Button(hdr, text="finally", fg="red", width=0, command=self.cb).grid(row=0, column=0)
                self.finalbody.grid(row=row, column=0, sticky=tk.W)

    def genForm(self):
        self.setForm(TryForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return TryNode(self.clause.toNode(), [((None if (type == None) else type.toNode()), (None if (name == None) else name.toNode()), clause.toNode()) for (clause, type, name) in self.handlers], (None if (self.orelse == None) else self.orelse.toNode()), (None if (self.finalbody == None) else self.finalbody.toNode()))

class WithClauseBlock(ClauseBlock):

    def __init__(self, parent, shared, node):
        if node == None:
            super().__init__(parent, shared, None, False, "with clause")
        else:
            super().__init__(parent, shared, node.body, False, "with clause")

        self.items = []
        tk.Button(self.hdr, text="with", fg="red", width=0, command=self.cb).grid(row=0, column=0)

        column = 1
        if node != None:
            for (expr, var) in node.items:
                b = expr.toBlock(self.hdr, self)
                b.grid(row=0, column=column)
                column += 1
                if var == None:
                    v = None
                else:
                    tk.Button(self.hdr, text="as", fg="red", width=0, command=self.cb).grid(row=0, column=column)
                    column += 1
                    v = var.toBlock(self.hdr, self)
                    v.grid(row=0, column=column)
                    column += 1
                self.items.append((b, v))

        self.hdr.grid()

    def genForm(self):
        self.setForm(WithClauseForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return WithClauseNode([(e.toNode(), None if v == None else v.toNode()) for (e, v) in self.items], self.body.toNode())

class ForBlock(CompoundBlock):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)

        self.isWithinLoop = True
        if (node == None):
            self.clause = ClauseBlock(self, shared, SeqNode([RowNode(PassNode())]), False, "'for' clause of a 'for' statement")
            hdr = self.clause.hdr
            hdr.isWithinStore = True
            self.target = ExpressionBlock(hdr, shared, None)
            hdr.isWithinStore = False
            self.expr = ExpressionBlock(hdr, shared, None)
            self.orelse = None
        else:
            self.clause = ClauseBlock(self, shared, node.body, False, "'for' clause of a 'for' statement")
            hdr = self.clause.hdr
            hdr.isWithinStore = True
            self.target = node.target.toBlock(hdr, self)
            hdr.isWithinStore = False
            self.expr = ExpressionBlock(hdr, shared, node.expr)
            self.orelse = None if (node.orelse == None) else Subblock(self, shared, node.orelse, "'else' clause of aa 'for' statement")
        tk.Button(hdr, text="for", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        self.target.grid(row=0, column=1)
        tk.Button(hdr, text="in", fg="red", command=self.cb).grid(row=0, column=2)
        self.expr.grid(row=0, column=3)
        self.clause.grid(row=0, sticky=tk.W)
        self.isWithinLoop = False
        if self.orelse != None:
            hdr2 = HeaderBlock(self, shared)
            tk.Button(hdr2, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
            self.orelse.grid(row=1, sticky=tk.W)

    def genForm(self):
        self.setForm(ForForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def addElse(self):
        self.orelse = ClauseBlock(self, self.shared, SeqNode([RowNode(PassNode())]), False, "'else' clause of a 'for' statement")
        hdr2 = self.orelse.hdr
        tk.Button(hdr2, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        self.orelse.grid(row=1, sticky=tk.W)
        self.setBlock(self.orelse.body.rows[0].what)
        self.needsSaving()

    def removeElse(self):
        self.orelse.grid_forget()
        self.orelse = None
        self.setBlock(self)
        self.needsSaving()

    def toNode(self):
        return ForNode(self.target.toNode(), self.expr.toNode(), self.clause.toNode(), (None if (self.orelse == None) else self.orelse.toNode()))
