import tkinter as tk
import tkinter.messagebox

from form import *
from node import *

class Block(tk.Frame):
    def __init__(self, parent, shared):
        super().__init__(parent, borderwidth=1, relief=tk.SUNKEN)
        self.shared = shared
        self.isExpression = False
        self.isStatement = False
        self.isWithinDef = False if parent == None else parent.isWithinDef
        self.isWithinLoop = False if parent == None else parent.isWithinLoop

    def printIndent(self, fd):
        for i in range(self.level):
            print("    ", end="", file=fd)

    def scrollUpdate(self):
        self.shared.scrollable.scrollUpdate()

    def setForm(self, f):
        if self.shared.curForm != None:
            self.shared.curForm.grid_forget()
        self.shared.curForm = f
        if f:
            f.grid(row=0, column=0, sticky=tk.E)
            f.update()
            f.catchKeys()

    def genForm(self):
        print("genForm")

    def setBlock(self, b):
        if self.shared.curBlock:
            self.shared.curBlock.configure(bd=1, highlightbackground="white", highlightcolor="white", highlightthickness=1)
        self.shared.curBlock = b
        if b:
            b.configure(bd=2, highlightbackground="red", highlightcolor="red", highlightthickness=2)
            b.update()
            b.genForm()

        self.scrollUpdate()

    def needsSaving(self):
        self.shared.saved = False

    def copyExpr(self):
        self.shared.exprBuffer = self.toNode()
        print("expression copied")

    def delExpr(self):
        self.copyExpr()
        self.parent.delExpr()
        print("expression deleted")

    def newPassBlock(self, parent, node, level, rowblk):
        return PassBlock(parent, self.shared, node, level, rowblk)

    def newEmptyBlock(self, parent, node, level):
        return EmptyBlock(parent, self.shared, node, level)

    def newDefBlock(self, parent, node, level):
        return DefBlock(parent, self.shared, node, level)

    def newClassBlock(self, parent, node, level):
        return ClassBlock(parent, self.shared, node, level)

    def newIfBlock(self, parent, node, level):
        return IfBlock(parent, self.shared, node, level)
        
    def newWhileBlock(self, parent, node, level):
        return WhileBlock(parent, self.shared, node, level)

    def newForBlock(self, parent, node, level):
        return ForBlock(parent, self.shared, node, level)

    def newReturnBlock(self, parent, node, level):
        return ReturnBlock(parent, self.shared, node, level)

    def newBreakBlock(self, parent, node, level):
        return BreakBlock(parent, self.shared, node, level)

    def newContinueBlock(self, parent, node, level):
        return ContinueBlock(parent, self.shared, node, level)

    def newImportBlock(self, parent, node, level):
        return ImportBlock(parent, self.shared, node, level)

    def newGlobalBlock(self, parent, node, level):
        return GlobalBlock(parent, self.shared, node, level)

    def newAssignBlock(self, parent, node, level):
        return AssignBlock(parent, self.shared, node, level)

    def newAugassignBlock(self, parent, node, level, op):
        return AugassignBlock(parent, self.shared, node, level, op)

    def newBinaryopBlock(self, parent, node, op):
        return BinaryopBlock(parent, self.shared, node, op)

    def newUnaryopBlock(self, parent, node, op):
        return UnaryopBlock(parent, self.shared, node, op)

    def newSubscriptBlock(self, parent, node, isSlice):
        return SubscriptBlock(parent, self.shared, node, isSlice)

    def newFuncBlock(self, parent, node):
        return FuncBlock(parent, self.shared, node)

    def newListBlock(self, parent, node):
        return ListBlock(parent, self.shared, node)

    def newTupleBlock(self, parent, node):
        return TupleBlock(parent, self.shared, node)

    def newAttrBlock(self, parent, node):
        return AttrBlock(parent, self.shared, node)

    def newEvalBlock(self, parent, node, level):
        return EvalBlock(parent, self.shared, node, level)

    def newNumberBlock(self, parent, what):
        return NumberBlock(parent, self.shared, what)

    def newConstantBlock(self, parent, what):
        return ConstantBlock(parent, self.shared, what)

    def newNameBlock(self, parent, what):
        return NameBlock(parent, self.shared, what)

    def newStringBlock(self, parent, what):
        return StringBlock(parent, self.shared, what)

    def newExpressionBlock(self, parent, what, lvalue):
        return ExpressionBlock(parent, self.shared, what, lvalue)

    def newSeqBlock(self, parent, rows, level):
        return SeqBlock(parent, self.shared, rows, level)

class NameBlock(Block):
    def __init__(self, parent, shared, vname):
        super().__init__(parent, shared)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.vname = tk.StringVar()
        self.btn = tk.Button(self, textvariable=self.vname, fg="blue", width=0, command=self.cb)
        self.vname.set(vname)
        self.btn.grid(row=0, column=0)

    def genForm(self):
        f = NameForm(self.shared.confarea, self)
        self.setForm(f)
        f.entry.focus()

    def cb(self):
        self.setBlock(self)

    def setName(self, v):
        self.vname.set(v)
        self.btn.config(width=0)
        self.needsSaving()

    def print(self, fd):
        v = self.vname.get()
        print(v, end="", file=fd)
        if not v.isidentifier():
            if not self.shared.printError:
                self.setBlock(self)
                tk.messagebox.showinfo("Print Error", "Fix bad variable name")
                self.shared.printError = True

    def toNode(self):
        return NameNode(self.vname.get())

class NumberBlock(Block):
    def __init__(self, parent, shared, value):
        super().__init__(parent, shared)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.value = tk.StringVar()
        self.value.set(value)
        self.btn = tk.Button(self, textvariable=self.value, fg="blue", width=0, command=self.cb)
        self.btn.grid(row=0, column=0)

    def genForm(self):
        f = NumberForm(self.shared.confarea, self)
        self.setForm(f)
        f.entry.focus()

    def cb(self):
        self.setBlock(self)

    def setValue(self, v):
        self.value.set(v)
        self.btn.config(width=0)
        self.needsSaving()

    def print(self, fd):
        v = self.value.get()
        print(v, end="", file=fd)
        try:
            float(v)
        except ValueError:
            if not self.shared.printError:
                self.setBlock(self)
                tk.messagebox.showinfo("Print Error", "Fix bad number")
                self.shared.printError = True

    def toNode(self):
        return NumberNode(self.value.get())

class ConstantBlock(Block):
    def __init__(self, parent, shared, value):
        super().__init__(parent, shared)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.value = tk.StringVar()
        self.value.set(value)
        self.btn = tk.Button(self, textvariable=self.value, fg="purple", width=0, command=self.cb)
        self.btn.grid(row=0, column=0)

    def genForm(self):
        self.setForm(ConstantForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        print(self.value.get(), end="", file=fd)

    def toNode(self):
        return ConstantNode(self.value.get())

class StringBlock(Block):
    def __init__(self, parent, shared, value):
        super().__init__(parent, shared)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.string = tk.StringVar()
        tk.Label(self, text='"').grid(row=0, column=0)
        self.btn = tk.Button(self, textvariable=self.string, fg="green", width=0, command=self.cb)
        self.lq = tk.Label(self, text='"')
        self.string.set(value)
        self.btn.grid(row=0, column=1)
        tk.Label(self, text='"').grid(row=0, column=2)

    def genForm(self):
        f = StringForm(self.shared.confarea, self)
        self.setForm(f)
        f.entry.focus()

    def cb(self):
        self.setBlock(self)

    def setContents(self, s):
        self.string.set(s)
        self.btn.config(width=0)
        self.needsSaving()

    def print(self, fd):
        print('"', end="", file=fd)
        for c in self.string.get():
            if c == '"':
                print('\\"', end="", file=fd)
            elif c == '\n':
                print('\\n', end="", file=fd)
            else:
                print(c, end="", file=fd)
        print('"', end="", file=fd)

    def toNode(self):
        return StringNode(self.string.get())

class SubscriptBlock(Block):
    def __init__(self, parent, shared, node, isSlice):
        super().__init__(parent, shared)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.isSlice = isSlice
        if node == None:
            self.array = ExpressionBlock(self, shared, None, False)
        else:
            self.array = ExpressionBlock(self, shared, node.array, False)
        self.array.grid(row=0, column=0)
        tk.Button(self, text='[', command=self.cb).grid(row=0, column=1)
        self.colon1 = tk.Button(self, text=':', command=self.cb)
        self.colon2 = tk.Button(self, text=':', command=self.cb)
        self.eol = tk.Button(self, text=']', command=self.cb)

        if node == None:
            if isSlice:
                self.lower = None
            else:
                self.lower = ExpressionBlock(self, shared, None, False)
            self.upper = self.step = None
        else:
            isSlice, lower, upper, step = node.slice
            assert isSlice == self.isSlice
            if self.isSlice:
                if lower == None:
                    self.lower = None
                else:
                    self.lower = ExpressionBlock(self, shared, lower, False)
                if upper == None:
                    self.upper = None
                else:
                    self.upper = ExpressionBlock(self, shared, upper, False)
                if step == None:
                    self.step = None
                else:
                    self.step = ExpressionBlock(self, shared, step, False)
            else:
                self.lower = ExpressionBlock(self, shared, lower, False)
                self.upper = self.step = None
        self.updateGrid()

    def cb(self):
        self.setBlock(self)

    def genForm(self):
        self.setForm(SubscriptForm(self.shared.confarea, self))

    def updateGrid(self):
        column = 2
        if self.lower != None:
            self.lower.grid(row=0, column=column)
            column += 1
        if self.isSlice:
            self.colon1.grid(row=0, column=column)
            column += 1
            if self.upper != None:
                self.upper.grid(row=0, column=column)
                column += 1
            if self.step != None:
                self.colon2.grid(row=0, column=column)
                column += 1
                self.step.grid(row=0, column=column)
                column += 1
        self.eol.grid(row=0, column=column)

    def addLower(self):
        self.lower = ExpressionBlock(self, self.shared, None, False)
        self.updateGrid()
        self.setBlock(self.lower)

    def addUpper(self):
        self.upper = ExpressionBlock(self, self.shared, None, False)
        self.updateGrid()
        self.setBlock(self.upper)

    def addStep(self):
        self.step = ExpressionBlock(self, self.shared, None, False)
        self.updateGrid()
        self.setBlock(self.step)

    def print(self, fd):
        self.array.print(fd)
        print("[", end="", file=fd)
        if self.lower != None:
            self.lower.print(fd)
        if self.isSlice:
            print(":", end="", file=fd)
            if self.upper != None:
                self.upper.print(fd)
            if self.step != None:
                print(":", end="", file=fd)
                self.step.print(fd)
        print("]", end="", file=fd)

    def toNode(self):
        return SubscriptNode(self.array.toNode(), (self.isSlice,
            None if self.lower == None else self.lower.toNode(),
            None if self.upper == None else self.upper.toNode(),
            None if self.step == None else self.step.toNode()))

class AttrBlock(Block):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        if node == None:
            self.array = ExpressionBlock(self, shared, None, False)
        else:
            self.array = ExpressionBlock(self, shared, node.array, False)
        self.array.grid(row=0, column=0)
        tk.Button(self, text='.', command=self.cb).grid(row=0, column=1)
        if node == None:
            self.ref = NameBlock(self, shared, "")
        else:
            self.ref = node.ref.toBlock(self, 0, self)
        self.ref.grid(row=0, column=2)

    def cb(self):
        self.setBlock(self)

    def genForm(self):
        self.setForm(AttrForm(self.shared.confarea, self))

    def print(self, fd):
        self.array.print(fd)
        print(".", end="", file=fd)
        self.ref.print(fd)

    def toNode(self):
        return AttrNode(self.array.toNode(), self.ref.toNode())

class UnaryopBlock(Block):
    def __init__(self, parent, shared, node, op):
        super().__init__(parent, shared)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.op = op

        left = tk.Button(self, text=op, fg="purple", width=0, command=self.cb)
        left.grid(row=0, column=0)

        if node == None:
            self.right = ExpressionBlock(self, shared, None, False)
        else:
            self.right = ExpressionBlock(self, shared, node.right, False)
        self.right.grid(row=0, column=1)

    def genForm(self):
        self.setForm(UnaryopForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        print(self.op, end="", file=fd)
        print("(", end="", file=fd)
        self.right.print(fd)
        print(")", end="", file=fd)

    def toNode(self):
        return UnaryopNode(self.right.toNode(), self.op)

class BinaryopBlock(Block):
    def __init__(self, parent, shared, node, op):
        super().__init__(parent, shared)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.op = op

        if node == None:
            self.left = ExpressionBlock(self, shared, None, False)
            self.middle = tk.Button(self, text=op, fg="purple", width=0, command=self.cb)
            self.right = ExpressionBlock(self, shared, None, False)
        else:
            self.left = ExpressionBlock(self, shared, node.left, False)
            self.middle = tk.Button(self, text=node.op, fg="purple", width=0, command=self.cb)
            self.right = ExpressionBlock(self, shared, node.right, False)

        self.left.grid(row=0, column=0)
        self.middle.grid(row=0, column=1)
        self.right.grid(row=0, column=2)

    def genForm(self):
        self.setForm(BinaryopForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        print("(", end="", file=fd)
        self.left.print(fd)
        print(" {} ".format(self.op), end="", file=fd)
        self.right.print(fd)
        print(")", end="", file=fd)

    def toNode(self):
        return BinaryopNode(self.left.toNode(), self.right.toNode(), self.op)

class ClassBlock(Block):
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        self.cname = tk.StringVar()

        if node == None:
            self.minimized = False
        else:
            self.cname.set(node.name)
            self.minimized = node.minimized

        self.hdr = Block(self, shared)
        self.btn = tk.Button(self.hdr, text="def", fg="red", width=0, command=self.cb)
        self.btn.grid(row=0, column=0)
        self.name = tk.Button(self.hdr, textvariable=self.cname, fg="blue", command=self.cb)
        self.name.grid(row=0, column=1)
        tk.Button(self.hdr, text="(", command=self.cb).grid(row=0, column=2)
        self.eol = tk.Button(self.hdr, text=")", command=self.cb)
        self.colon = tk.Button(self.hdr, text=":", command=self.minmax)
        self.hdr.grid(row=0, column=0, sticky=tk.W)

        self.bases = [ ]
        if node != None:
            for base in node.bases:
                self.addBaseClass(base)
        self.setHeader()

        if node == None:
            self.body = SeqBlock(self, shared, None, level + 1)
        else:
            self.body = SeqBlock(self, shared, node.body, level + 1)
        if not self.minimized:
            self.body.grid(row=1, column=0, sticky=tk.W)

    def genForm(self):
        self.setForm(ClassForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def minmax(self):
        if self.minimized:
            self.body.grid(row=1, column=0, sticky=tk.W)
            self.update()
            self.minimized = False
        else:
            self.body.grid_forget()
            self.minimized = True
        self.scrollUpdate()

    def classUpdate(self, mname):
        self.cname.set(mname)
        self.needsSaving()

    def addBaseClass(self, node):
        if node == None:
            base = ExpressionBlock(self.hdr, self.shared, None, False)
        else:
            base = ExpressionBlock(self.hdr, self.shared, node, False)
        self.bases.append(base)
        self.setHeader()
        self.needsSaving()

    def setHeader(self):
        column = 3
        for i in range(len(self.bases)):
            if i != 0:
                tk.Button(self.hdr, text=",", command=self.cb).grid(row=0, column=column)
                column += 1
            self.bases[i].grid(row=0, column=column)
            column += 1
        self.eol.grid(row=0, column=column)
        self.colon.grid(row=0, column=column+1)

    def print(self, fd):
        self.printIndent(fd)
        v = self.cname.get()
        print("class {}(".format(v), end="", file=fd)
        if not v.isidentifier():
            if not self.shared.printError:
                self.setBlock(self)
                tk.messagebox.showinfo("Print Error", "Fix bad method name")
                self.shared.printError = True
        for i in range(len(self.bases)):
            if i != 0:
                print(", ", end="", file=fd)
            self.bases[i].print(fd)
        print("):", file=fd)
        self.body.print(fd)

    def toNode(self):
        return ClassNode(self.cname.get(), self.bases, self.body.toNode(), self.minimized)

class FuncBlock(Block):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent

        if node == None:
            self.func = ExpressionBlock(self, shared, None, False)
        else:
            self.func = ExpressionBlock(self, shared, node.func, False)
        self.func.grid(row=0, column=0)

        tk.Button(self, text="(", width=0, command=self.cb).grid(row=0, column=1)
        self.eol = tk.Button(self, text=")", width=0, command=self.cb)

        self.args = [ ]
        if node != None:
            for arg in node.args:
                self.addArg(arg)
        self.gridUpdate()

    def genForm(self):
        self.setForm(FuncForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def addArg(self, node):
        if node == None:
            arg = ExpressionBlock(self, self.shared, None, False)
        else:
            arg = ExpressionBlock(self, self.shared, node, False)
        self.args.append(arg)
        self.gridUpdate()
        self.needsSaving()

    def gridUpdate(self):
        for i in range(len(self.args)):
            if i != 0:
                tk.Button(self, text=",", width=0, command=self.cb).grid(row=0, column=2*i+2)
            self.args[i].grid(row=0, column=2*i+3)
        self.eol.grid(row=0, column=2*len(self.args)+3)

    def print(self, fd):
        self.func.print(fd)
        print("(", end="", file=fd)
        for i in range(len(self.args)):
            if i != 0:
                print(", ", end="", file=fd)
            self.args[i].print(fd)
        print(")", end="", file=fd)

    def toNode(self):
        return FuncNode(self.func.toNode(),
                        [ arg.toNode() for arg in self.args ])

class ListBlock(Block):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent

        tk.Button(self, text="[", width=0, command=self.cb).grid(row=0, column=0)
        self.eol = tk.Button(self, text="]", width=0, command=self.cb)

        self.entries = [ ]
        if node != None:
            for e in node.entries:
                self.addEntry(e)
        self.gridUpdate()

    def genForm(self):
        self.setForm(ListForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def addEntry(self, node):
        if node == None:
            e = ExpressionBlock(self, self.shared, None, False)
        else:
            e = ExpressionBlock(self, self.shared, node, False)
        self.entries.append(e)
        self.gridUpdate()
        self.needsSaving()

    def gridUpdate(self):
        for i in range(len(self.entries)):
            if i != 0:
                tk.Button(self, text=",", width=0, command=self.cb).grid(row=0, column=2*i+1)
            self.entries[i].grid(row=0, column=2*i+2)
        self.eol.grid(row=0, column=2*len(self.entries)+2)

    def print(self, fd):
        print("[", end="", file=fd)
        for i in range(len(self.entries)):
            if i != 0:
                print(", ", end="", file=fd)
            self.entries[i].print(fd)
        print("]", end="", file=fd)

    def toNode(self):
        return ListNode([ entry.toNode() for entry in self.entries ])

class TupleBlock(Block):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent

        tk.Button(self, text="(", width=0, command=self.cb).grid(row=0, column=0)
        self.eol = tk.Button(self, text=")", width=0, command=self.cb)

        self.entries = [ ]
        if node != None:
            for e in node.entries:
                self.addEntry(e)
        self.gridUpdate()

    def genForm(self):
        self.setForm(TupleForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def addEntry(self, node):
        if node == None:
            e = ExpressionBlock(self, self.shared, None, False)
        else:
            e = ExpressionBlock(self, self.shared, node, False)
        self.entries.append(e)
        self.gridUpdate()
        self.needsSaving()

    def gridUpdate(self):
        for i in range(len(self.entries)):
            if i != 0:
                tk.Button(self, text=",", width=0, command=self.cb).grid(row=0, column=2*i+1)
            self.entries[i].grid(row=0, column=2*i+2)
        self.eol.grid(row=0, column=2*len(self.entries)+2)

    def print(self, fd):
        print("(", end="", file=fd)
        for i in range(len(self.entries)):
            if i != 0:
                print(", ", end="", file=fd)
            self.entries[i].print(fd)
        print(")", end="", file=fd)

    def toNode(self):
        return TupleNode([ entry.toNode() for entry in self.entries ])

class ExpressionBlock(Block):
    def __init__(self, parent, shared, node, lvalue):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = False
        self.parent = parent
        self.lvalue = lvalue
        if node == None or node.what == None:
            self.what = tk.Button(self, text="?", width=0, command=self.cb)
            self.init = False
        else:
            self.what = node.what.toBlock(self, 0, self)
            self.init = True
        self.what.grid()

    def delExpr(self):
        self.what.grid_forget()
        self.what = tk.Button(self, text="?", width=0, command=self.cb)
        self.what.grid()
        self.init = False
        self.setBlock(self)
        self.needsSaving()

    def genForm(self):
        f = ExpressionForm(self.shared.confarea, self, self.lvalue)
        self.setForm(f)

    def cb(self):
        self.setBlock(self)

    def exprNumber(self, v):
        self.what.grid_forget()
        self.what = NumberBlock(self, self.shared, v)
        self.what.grid()
        self.init = True
        self.setBlock(self.what)
        self.needsSaving()

    def exprConstant(self, value):
        self.what.grid_forget()
        self.what = ConstantBlock(self, self.shared, value)
        self.what.grid()
        self.init = True
        self.setBlock(self.what)
        self.needsSaving()

    def exprString(self):
        self.what.grid_forget()
        self.what = StringBlock(self, self.shared, "")
        self.what.grid()
        self.init = True
        self.setBlock(self.what)
        self.needsSaving()

    def exprName(self, v):
        self.what.grid_forget()
        self.what = NameBlock(self, self.shared, v)
        self.what.grid()
        self.init = True
        self.setBlock(self.what)
        self.needsSaving()

    def exprSubscript(self, isSlice):
        self.what.grid_forget()
        self.what = SubscriptBlock(self, self.shared, None, isSlice)
        self.what.grid()
        self.init = True
        self.setBlock(self.what.array)
        self.needsSaving()

    def exprAttr(self):
        self.what.grid_forget()
        self.what = AttrBlock(self, self.shared, None)
        self.what.grid()
        self.init = True
        self.setBlock(self.what.array)
        self.needsSaving()

    def exprList(self):
        self.what.grid_forget()
        self.what = ListBlock(self, self.shared, None)
        self.what.grid()
        self.init = True
        self.setBlock(self.what)
        self.needsSaving()

    def exprTuple(self):
        self.what.grid_forget()
        self.what = TupleBlock(self, self.shared, None)
        self.what.grid()
        self.init = True
        self.setBlock(self.what)
        self.needsSaving()

    def exprUnaryop(self, op):
        self.what.grid_forget()
        self.what = UnaryopBlock(self, self.shared, None, op)
        self.what.grid()
        self.init = True
        self.setBlock(self.what.right)
        self.needsSaving()

    def exprBinaryop(self, op):
        self.what.grid_forget()
        self.what = BinaryopBlock(self, self.shared, None, op)
        self.what.grid()
        self.init = True
        self.setBlock(self.what.left)
        self.needsSaving()

    def exprFunc(self):
        self.what.grid_forget()
        self.what = FuncBlock(self, self.shared, None)
        self.what.grid()
        self.init = True
        self.setBlock(self.what.func)
        self.needsSaving()

    def exprPaste(self):
        if self.shared.exprBuffer != None:
            self.what.grid_forget()
            self.what = self.shared.exprBuffer.toBlock(self, 0, self)
            self.what.grid(row=0, column=1, sticky=tk.W)
            self.init = True
            self.setBlock(self.what)
            self.needsSaving()

    def print(self, fd):
        if self.init:
            self.what.print(fd)
        else:
            print("?", end="", file=fd)
            if not self.shared.printError:
                self.setBlock(self)
                tk.messagebox.showinfo("Print Error", "Fix uninitialized expression")
                self.shared.printError = True

    def toNode(self):
        return ExpressionNode(self.what.toNode() if self.init else None)

class AssignBlock(Block):
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level

        if node == None:
            self.targets = [ExpressionBlock(self, shared, None, True)]
            self.value = ExpressionBlock(self, shared, None, False)
        else:
            self.targets = [ExpressionBlock(self, shared, t, True) for t in node.targets]
            self.value = ExpressionBlock(self, shared, node.value, False)

        column = 0
        for t in self.targets:
            t.grid(row=0, column=column)
            column += 1
            tk.Button(self, text='=', fg="purple", command=self.cb).grid(row=0, column=column)
            column += 1
        self.value.grid(row=0, column=column)

    def genForm(self):
        self.setForm(AssignForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        self.printIndent(fd)
        for t in self.targets:
            t.print(fd)
            print(" = ", end="", file=fd)
        self.value.print(fd)
        print("", file=fd)

    def toNode(self):
        return AssignNode([ t.toNode() for t in self.targets ], self.value.toNode())

class AugassignBlock(Block):
    def __init__(self, parent, shared, node, level, op):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        self.op = op
        if node == None:
            self.left = ExpressionBlock(self, shared, None, True)
            middle = tk.Button(self, text=op, fg="purple", command=self.cb)
            self.right = ExpressionBlock(self, shared, None, False)
        else:
            self.left = ExpressionBlock(self, shared, node.left, True)
            middle = tk.Button(self, text=op, fg="purple", command=self.cb)
            self.right = ExpressionBlock(self, shared, node.right, False)
        self.left.grid(row=0, column=0)
        middle.grid(row=0, column=1)
        self.right.grid(row=0, column=2)

    def genForm(self):
        self.setForm(AugassignForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        self.printIndent(fd)
        self.left.print(fd)
        print(" {} ".format(self.op), end="", file=fd)
        self.right.print(fd)
        print("", file=fd)

    def toNode(self):
        return AugassignNode(self.left.toNode(), self.right.toNode(), self.op)

class PassBlock(Block):
    def __init__(self, parent, shared, node, level, rowblk):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        self.rowblk = rowblk
        btn = tk.Button(self, text="pass", fg="red", width=0, command=self.cb)
        btn.grid(row=0, column=0)

    def genForm(self):
        f = PassForm(self.shared.confarea, self)
        self.setForm(f)

    def cb(self):
        self.setBlock(self)

    def stmtEmpty(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = EmptyBlock(self.rowblk, self.shared, self.shared, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk)
        self.needsSaving()

    def stmtDef(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = DefBlock(self.rowblk, self.shared, self.shared, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what)
        self.needsSaving()

    def stmtAugassign(self, op):
        self.rowblk.what.grid_forget()
        self.rowblk.what = AssignBlock(self.rowblk, self.shared, None, self.level) if op == '=' else AugassignBlock(self.rowblk, None, self.level, op)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.targets[0])
        self.needsSaving()

    def stmtEval(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = EvalBlock(self.rowblk, self.shared, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.expr)
        self.needsSaving()

    def stmtIf(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = IfBlock(self.rowblk, self.shared, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.conds[0])
        self.needsSaving()

    def stmtWhile(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = WhileBlock(self.rowblk, self.shared, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.cond)
        self.needsSaving()

    def stmtFor(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ForBlock(self.rowblk, self.shared, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.var)
        self.needsSaving()

    def stmtReturn(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ReturnBlock(self.rowblk, self.shared, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.expr)
        self.needsSaving()

    def stmtBreak(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = BreakBlock(self.rowblk, self.shared, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what)
        self.needsSaving()

    def stmtContinue(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ContinueBlock(self.rowblk, self.shared, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what)
        self.needsSaving()

    def stmtGlobal(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = GlobalBlock(self.rowblk, self.shared, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.var)
        self.needsSaving()

    def stmtImport(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ImportBlock(self.rowblk, self.shared, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.module)
        self.needsSaving()

    def stmtPaste(self):
        if self.shared.stmtBuffer != None:
            self.rowblk.what.grid_forget()
            self.rowblk.what = self.shared.stmtBuffer.toBlock(self.rowblk, self.level, self.rowblk)
            self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
            self.setBlock(self.rowblk.what)
        self.needsSaving()

    def print(self, fd):
        self.printIndent(fd)
        print("pass", file=fd)

    def toNode(self):
        return PassNode()

class EmptyBlock(Block):
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        # btn = tk.Button(self, text="", fg="red", width=0, command=self.cb)
        # btn.grid(row=0, column=0)

    def genForm(self):
        # f = EmptyForm(self.shared.confarea, self)
        # self.setForm(f)
        pass

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        self.printIndent(fd)
        print("", file=fd)

    def toNode(self):
        return EmptyNode()

class EvalBlock(Block):
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        if node == None:
            self.expr = ExpressionBlock(self, shared, None, False)
        else:
            self.expr = ExpressionBlock(self, shared, node.what, False)
        self.expr.grid()

    def print(self, fd):
        self.printIndent(fd)
        self.expr.print(fd)
        print("", file=fd)

    def toNode(self):
        return EvalNode(self.expr.toNode())

class ReturnBlock(Block):
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        tk.Button(self, text="return", fg="red", command=self.cb).grid(row=0, column=0)
        if node == None:
            self.expr = ExpressionBlock(self, shared, None, False)
        else:
            self.expr = ExpressionBlock(self, shared, node.what, False)
        self.expr.grid(row=0, column=1)

    def genForm(self):
        self.setForm(ReturnForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        self.printIndent(fd)
        print("return ", end="", file=fd)
        self.expr.print(fd)
        print("", file=fd)

    def toNode(self):
        return ReturnNode(self.expr.toNode())

class BreakBlock(Block):
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        tk.Button(self, text="break", fg="red", command=self.cb).grid(row=0, column=0)

    def genForm(self):
        self.setForm(BreakForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        self.printIndent(fd)
        print("break", file=fd)

    def toNode(self):
        return BreakNode()

class ContinueBlock(Block):
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        tk.Button(self, text="continue", fg="red", command=self.cb).grid(row=0, column=0)

    def genForm(self):
        self.setForm(ContinueForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        self.printIndent(fd)
        print("continue", file=fd)

    def toNode(self):
        return ContinueNode()

class GlobalBlock(Block):
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        tk.Button(self, text="global", fg="red", command=self.cb).grid(row=0, column=0)
        if node == None:
            self.vars = [NameBlock(self, shared, "")]
        else:
            self.vars = [NameBlock(self, shared, n) for n in node.names]

        column = 1
        for i in range(len(self.vars)):
            if i > 0:
                tk.Button(self, text=",", command=self.cb).grid(row=0, column=column)
                column += 1
            self.vars[i].grid(row=0, column=column)
            column += 1

    def genForm(self):
        self.setForm(GlobalForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        self.printIndent(fd)
        print("global ", end="", file=fd)
        for i in range(len(self.vars)):
            if i > 0:
                print(", ", end="", file=fd)
            self.vars[i].print(fd)
        print("", file=fd)

    def toNode(self):
        return GlobalNode(self.var.toNode())

class ImportBlock(Block):
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        tk.Button(self, text="import", fg="red", command=self.cb).grid(row=0, column=0)
        if node == None:
            self.module = NameBlock(self, shared, "")
        else:
            self.module = NameBlock(self, shared, node.what)
        self.module.grid(row=0, column=1)

    def genForm(self):
        self.setForm(ImportForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        self.printIndent(fd)
        print("import ", end="", file=fd)
        self.module.print(fd)
        print("", file=fd)

    def toNode(self):
        return ImportNode(self.module.toNode())

class RowBlock(Block):
    def __init__(self, parent, shared, node, level, row):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = False
        self.parent = parent
        self.level = level
        self.row = row
        self.comment = tk.StringVar()

        menu = tk.Button(self, text="-", width=3, command=self.listcmd)
        menu.grid(row=0, column=0, sticky=tk.W)
        if node == None:
            self.what = PassBlock(self, self.shared, None, level, self)
        else:
            self.what = node.what.toBlock(self, level, self)
        self.what.grid(row=0, column=1, sticky=tk.W)
        if node != None and node.comment != None:
            self.comment.set("#" + node.comment)
        tk.Button(self, textvariable=self.comment, fg="brown", command=self.listcmd).grid(row=0, column=2, sticky=tk.N+tk.W)

    def setComment(self, comment):
        if comment == "":
            self.comment.set("")
        else:
            self.comment.set("#" + comment)

    def genForm(self):
        f = RowForm(self.shared.confarea, self)
        self.setForm(f)

    def addStmt(self):
        self.parent.insert(self.row + 1)
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

    def copyStmt(self):
        self.shared.stmtBuffer = self.what.toNode()
        print("statement copied")

    def delStmt(self):
        self.parent.delRow(self.row)
        print("statement deleted")
        self.needsSaving()

    def listcmd(self):
        self.setBlock(self)

    def print(self, fd):
        # first print into a string buffer
        f = io.StringIO("")
        self.what.print(f)
        s = f.getvalue()

        # insert the comment, if any, after the first line
        if '\n' in s and self.comment.get() != "":
            i = s.index('\n')
            s = s[:i] + ('' if isinstance(self.what, EmptyBlock) else '\t') + self.comment.get() + s[i:]

        print(s, file=fd, end="")

    def toNode(self):
        return RowNode(self.what.toNode(), 0)

class SeqBlock(Block):
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = False
        self.parent = parent
        self.level = level
        self.rows = []
        if node == None:
            self.insert(0)
        else:
            for i in range(len(node.rows)):
                self.rows.append(RowBlock(self, shared, node.rows[i], self.level, i))
            self.gridUpdate()

    def insert(self, row):
        rb = RowBlock(self, self.shared, None, self.level, row)
        self.rows.insert(row, rb)
        self.gridUpdate()
        self.setBlock(rb.what)

    def delRow(self, row):
        for i in range(len(self.rows)):
            self.rows[i].grid_forget()
        if row < len(self.rows):
            del self.rows[row]
        if len(self.rows) == 0:
            self.insert(0)
        else:
            if row >= len(self.rows):
                row = len(self.rows) - 1
            self.setBlock(self.rows[row])
        self.gridUpdate()

    def moveUp(self, row):
        if row == 0:
            return
        tmp = self.rows[row - 1]
        self.rows[row - 1] = self.rows[row]
        self.rows[row] = tmp
        self.gridUpdate()

    def moveDown(self, row):
        if row == len(self.rows) - 1:
            return
        tmp = self.rows[row + 1]
        self.rows[row + 1] = self.rows[row]
        self.rows[row] = tmp
        self.gridUpdate()

    def gridUpdate(self):
        for row in range(len(self.rows)):
            self.rows[row].grid(row=row, column=0, sticky=tk.W)
            self.rows[row].row = row

    def print(self, fd):
        for r in self.rows:
            r.print(fd)

    def toNode(self):
        return SeqNode([ r.toNode() for r in self.rows ])

class DefBlock(Block):
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        self.isWithinDef = True
        self.mname = tk.StringVar()

        if node == None:
            self.args = [ ]
            self.minimized = False
        else:
            self.mname.set(node.name)
            self.args = node.args
            self.minimized = node.minimized

        self.setHeader()

        if node == None:
            self.body = SeqBlock(self, shared, None, level + 1)
        else:
            self.body = SeqBlock(self, shared, node.body, level + 1)
        if not self.minimized:
            self.body.grid(row=1, column=0, sticky=tk.W)

    def setHeader(self):
        self.hdr = Block(self, self.shared)
        self.btn = tk.Button(self.hdr, text="def", fg="red", width=0, command=self.cb)
        self.btn.grid(row=0, column=0)
        self.name = tk.Button(self.hdr, textvariable=self.mname, fg="blue", command=self.cb)
        self.name.grid(row=0, column=1)
        tk.Button(self.hdr, text="(", command=self.cb).grid(row=0, column=2)

        column = 3
        for i in range(len(self.args)):
            if i != 0:
                tk.Button(self.hdr, text=",", command=self.cb).grid(row=0, column=column)
                column += 1
            tk.Button(self.hdr, text=self.args[i], fg="blue", command=self.cb).grid(row=0, column=column)
            column += 1

        tk.Button(self.hdr, text=")", command=self.cb).grid(row=0, column=column)
        tk.Button(self.hdr, text=":", command=self.minmax).grid(row=0, column=column+1)
        self.hdr.grid(row=0, column=0, sticky=tk.W)

    def genForm(self):
        f = DefForm(self.shared.confarea, self)
        self.setForm(f)
        f.entry.focus()

    def cb(self):
        self.setBlock(self)

    def minmax(self):
        if self.minimized:
            self.body.grid(row=1, column=0, sticky=tk.W)
            self.update()
            self.minimized = False
        else:
            self.body.grid_forget()
            self.minimized = True
        self.scrollUpdate()

    def defUpdate(self, mname, args):
        self.mname.set(mname)
        self.args = args
        self.hdr.grid_forget()
        self.setHeader()
        self.needsSaving()

    def print(self, fd):
        self.printIndent(fd)
        v = self.mname.get()
        print("def {}(".format(v), end="", file=fd)
        if not v.isidentifier():
            if not self.shared.printError:
                self.setBlock(self)
                tk.messagebox.showinfo("Print Error", "Fix bad method name")
                self.shared.printError = True
        for i in range(len(self.args)):
            if i != 0:
                print(", ", end="", file=fd)
            print(self.args[i], end="", file=fd)
            if not self.args[i].isidentifier():
                if not self.shared.printError:
                    self.setBlock(self)
                    tk.messagebox.showinfo("Print Error", "Fix bad argument name")
                    self.shared.printError = True
        print("):", file=fd)
        self.body.print(fd)

    def toNode(self):
        return DefNode(self.mname.get(), self.args, self.body.toNode(), self.minimized)

class IfBlock(Block):
    """
        An if statement has N conditions and N (no else) or N+1 (with else) bodies.
    """
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level

        if node == None:
            self.hdrs = [Block(self, shared)]
            self.minimizeds = [ False ]
            tk.Button(self.hdrs[0], text="if", fg="red", width=0, command=self.cb).grid(row=0, column=0)
            self.conds = [ExpressionBlock(self.hdrs[0], shared, None, False)]
            self.conds[0].grid(row=0, column=1)
            tk.Button(self.hdrs[0], text=":", command=self.cb).grid(row=0, column=2, sticky=tk.W)
            self.bodies = [SeqBlock(self, shared, None, level + 1)]
        else:
            self.bodies = [ SeqBlock(self, shared, n, level + 1) for n in node.bodies ]
            self.hdrs = [ ]
            self.minimizeds = node.minimizeds
            self.conds = [ ]
            for i in range(len(self.bodies)):
                if i < len(node.conds):
                    hdr = Block(self, shared)
                    cond = ExpressionBlock(hdr, shared, node.conds[i], False)
                    self.conds.append(cond)
                    if i == 0:
                        tk.Button(hdr, text="if", fg="red", width=0, command=self.cb).grid(row=0, column=0)
                    else:
                        tk.Button(hdr, text="elif", fg="red", width=0, command=self.cb).grid(row=0, column=0)
                    cond.grid(row=0, column=1)
                    tk.Button(hdr, text=":", command=lambda: self.minmax(self.bodies[i])).grid(row=0, column=2, sticky=tk.W)
                else:
                    hdr = Block(self, shared)
                    tk.Button(hdr, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
                    tk.Button(hdr, text=":", width=0, command=lambda: self.minmax(self.bodies[-1])).grid(row=0, column=1)
                self.hdrs.append(hdr)
        self.gridUpdate()

    def genForm(self):
        self.setForm(IfForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def minmax(self, body):
        which = self.bodies.index(body)
        if self.minimizeds[which]:
            body.grid(row=1, column=0, sticky=tk.W)
            self.update()
            self.minimizeds[which] = False
        else:
            body.grid_forget()
            self.minimizeds[which] = True
        self.gridUpdate()    # ???
        self.scrollUpdate()

    def addElse(self):
        self.bodies.append(SeqBlock(self, shared, None, self.level + 1))
        hdr = Block(self, shared)
        tk.Button(hdr, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        tk.Button(hdr, text=":", width=0, command=lambda: self.minmax(self.bodies[-1])).grid(row=0, column=1)
        self.hdrs.append(hdr)
        self.minimizeds.append(False)
        self.gridUpdate()
        self.needsSaving()

    def removeElse(self):
        self.bodies[len(self.bodies) - 1].grid_forget()
        del self.bodies[len(self.bodies) - 1]
        self.hdrs[len(self.hdrs) - 1].grid_forget()
        del self.hdrs[len(self.hdrs) - 1]
        self.setBlock(self)
        self.needsSaving()

    def insertElif(self):
        hdr = Block(self, self.shared)
        tk.Button(hdr, text="elif", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        cond = ExpressionBlock(hdr, self.shared, None, False)
        cond.grid(row=0, column=1)
        body = SeqBlock(self, self.shared, None, self.level + 1)
        tk.Button(hdr, text=":", command=lambda: self.minmax(body)).grid(row=0, column=2)
        self.hdrs.insert(len(self.conds), hdr)
        self.minimizeds.insert(len(self.conds), False)
        self.bodies.insert(len(self.conds), body)
        self.conds.append(cond)
        self.gridUpdate()
        self.setBlock(self)
        self.needsSaving()

    def gridUpdate(self):
        for i in range(len(self.bodies)):
            if i < len(self.hdrs):
                self.hdrs[i].grid(row=2*i, column = 0, sticky=tk.W)
            if self.minimizeds[i]:
                self.bodies[i].grid_forget()
            else:
                self.bodies[i].grid(row=2*i+1, column = 0, sticky=tk.W)
        self.scrollUpdate()

    def print(self, fd):
        for i in range(len(self.bodies)):
            self.printIndent(fd)
            if i == 0:
                print("if ", end="", file=fd)
                self.conds[i].print(fd)
                print(":", file=fd)
            elif i < len(self.conds):
                print("elif ", end="", file=fd)
                self.conds[i].print(fd)
                print(":", file=fd)
            else:
                print("else:", file=fd)
            self.bodies[i].print(fd)

    def toNode(self):
        return IfNode([c.toNode() for c in self.conds], [b.toNode() for b in self.bodies], self.minimizeds)

class WhileBlock(Block):
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level

        hdr = Block(self, self.shared)
        tk.Button(hdr, text="while", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        self.isWithinLoop = True
        if node == None:
            self.cond = ExpressionBlock(hdr, self.shared, None, False)
            self.body = SeqBlock(self, self.shared, None, level + 1)
            self.orelse = None
            self.minimized = False
            self.minimized2 = False
        else:
            self.cond = ExpressionBlock(hdr, self.shared, node.cond, False)
            self.body = SeqBlock(self, self.shared, node.body, level + 1)
            self.orelse = None if node.orelse == None else SeqBlock(self, self.shared, node.orelse, level + 1)
            self.minimized = node.minimized
            self.minimized2 = node.minimized2
        self.cond.grid(row=0, column=1)
        tk.Button(hdr, text=":", command=self.minmax).grid(row=0, column=2, sticky=tk.W)

        hdr.grid(row=0, column=0, sticky=tk.W)
        self.body.grid(row=1, column=0, sticky=tk.W)
        self.isWithinLoop = False

        if self.orelse == None:
            self.hdr2 = None
        else:
            self.hdr2 = Block(self, self.shared)
            tk.Button(self.hdr2, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
            tk.Button(self.hdr2, text=":", command=self.minmax2).grid(row=0, column=1, sticky=tk.W)
            self.hdr2.grid(row=2, column=0, sticky=tk.W)
            self.orelse.grid(row=3, column=0, sticky=tk.W)

    def genForm(self):
        self.setForm(WhileForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def minmax(self):
        if self.minimized:
            self.body.grid(row=1, column=0, sticky=tk.W)
            self.update()
            self.minimized = False
        else:
            self.body.grid_forget()
            self.minimized = True
        self.scrollUpdate()

    def minmax2(self):
        if self.minimized2:
            self.orelse.grid(row=3, column=0, sticky=tk.W)
            self.update()
            self.minimized2 = False
        else:
            self.orelse.grid_forget()
            self.minimized2 = True
        self.scrollUpdate()

    def addElse(self):
        self.orelse = SeqBlock(self, self.shared, None, self.level + 1)
        self.hdr2 = Block(self, self.shared)
        tk.Button(self.hdr2, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        tk.Button(self.hdr2, text=":", width=0, command=self.minmax2).grid(row=0, column=1)
        self.hdr2.grid(row=2, column=0, sticky=tk.W)
        self.orelse.grid(row=3, column=0, sticky=tk.W)
        self.setBlock(self.orelse.rows[0].what)
        self.needsSaving()

    def removeElse(self):
        self.hdr2.grid_forget()
        self.hdr2 = None
        self.orelse.grid_forget()
        self.orelse = None
        self.setBlock(self)
        self.needsSaving()

    def print(self, fd):
        self.printIndent(fd)
        print("while ", end="", file=fd)
        self.cond.print(fd)
        print(":", file=fd)
        self.body.print(fd)
        if self.orelse != None:
            self.printIndent(fd)
            print("else:", file=fd)
            self.orelse.print(fd)

    def toNode(self):
        return WhileNode(self.cond.toNode(), self.body.toNode(), None if self.orelse == None else self.orelse.toNode(), self.minimized, self.minimized2)

class ForBlock(Block):
    def __init__(self, parent, shared, node, level):
        super().__init__(parent, shared)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level

        hdr = Block(self, shared)
        tk.Button(hdr, text="for", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        self.isWithinLoop = True
        if node == None:
            self.var = NameBlock(hdr, shared, "")
            self.expr = ExpressionBlock(hdr, shared, None, False)
            self.body = SeqBlock(self, shared, None, level + 1)
            self.orelse = None
            self.minimized = False
            self.minimized2 = False
        else:
            self.var = node.var.toBlock(hdr, 0, self)
            self.expr = ExpressionBlock(hdr, shared, node.expr, False)
            self.body = SeqBlock(self, shared, node.body, level + 1)
            self.orelse = None if node.orelse == None else SeqBlock(self, shared, node.orelse, level + 1)
            self.minimized = node.minimized
            self.minimized2 = node.minimized2
        self.var.grid(row=0, column=1)
        tk.Button(hdr, text="in", fg="red", command=self.cb).grid(row=0, column=2)
        self.expr.grid(row=0, column=3)
        tk.Button(hdr, text=":", command=self.minmax).grid(row=0, column=4, sticky=tk.W)

        hdr.grid(row=0, column=0, sticky=tk.W)
        self.body.grid(row=1, column=0, sticky=tk.W)
        self.isWithinLoop = False

        if self.orelse == None:
            self.hdr2 = None
        else:
            self.hdr2 = Block(self, shared)
            tk.Button(self.hdr2, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
            tk.Button(self.hdr2, text=":", command=self.minmax2).grid(row=0, column=1, sticky=tk.W)
            self.hdr2.grid(row=2, column=0, sticky=tk.W)
            self.orelse.grid(row=3, column=0, sticky=tk.W)

    def genForm(self):
        self.setForm(ForForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def minmax(self):
        if self.minimized:
            self.body.grid(row=1, column=0, sticky=tk.W)
            self.update()
            self.minimized = False
        else:
            self.body.grid_forget()
            self.minimized = True
        self.scrollUpdate()

    def minmax2(self):
        if self.minimized2:
            self.orelse.grid(row=3, column=0, sticky=tk.W)
            self.update()
            self.minimized2 = False
        else:
            self.orelse.grid_forget()
            self.minimized2 = True
        self.scrollUpdate()

    def addElse(self):
        self.orelse = SeqBlock(self, self.shared, None, self.level + 1)
        self.hdr2 = Block(self, self.shared)
        tk.Button(self.hdr2, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        tk.Button(self.hdr2, text=":", width=0, command=self.minmax2).grid(row=0, column=1)
        self.hdr2.grid(row=2, column=0, sticky=tk.W)
        self.orelse.grid(row=3, column=0, sticky=tk.W)
        self.setBlock(self.orelse.rows[0].what)
        self.needsSaving()

    def removeElse(self):
        self.hdr2.grid_forget()
        self.hdr2 = None
        self.orelse.grid_forget()
        self.orelse = None
        self.setBlock(self)
        self.needsSaving()

    def print(self, fd):
        self.printIndent(fd)
        print("for ", end="", file=fd)
        self.var.print(fd)
        print(" in ", end="", file=fd)
        self.expr.print(fd)
        print(":", file=fd)
        self.body.print(fd)
        if self.orelse != None:
            self.printIndent(fd)
            print("else:", file=fd)
            self.orelse.print(fd)

    def toNode(self):
        return ForNode(self.var.toNode(), self.expr.toNode(), self.body.toNode(), None if self.orelse == None else self.orelse.toNode(), self.minimized, self.minimized2)
