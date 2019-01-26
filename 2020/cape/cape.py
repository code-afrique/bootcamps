import os
import tempfile
import subprocess
import sys
import io
import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import tokenize

import pparse
from form import *
from node import *

"""
    A row contains a statement with a menu button and a comment
    A list is a sequence of rows
    A method definion contains a header and a list
"""

class EmptyNode(Node):
    def __init__(self):
        super().__init__()

    def toBlock(self, frame, level, block):
        return EmptyBlock(frame, self, level)

class RowNode(Node):
    def __init__(self, what, lineno):
        super().__init__()
        self.what = what
        self.lineno = lineno
        self.comment = None

    def findRow(self, lineno):
        return self.what.findRow(lineno)

class DefNode(Node):
    def __init__(self, name, args, body, minimized):
        super().__init__()
        self.name = name
        self.args = args
        self.body = body
        self.minimized = minimized

    def toBlock(self, frame, level, block):
        return DefBlock(frame, self, level)

    def findRow(self, lineno):
        return self.body.findRow(lineno)

class ClassNode(Node):
    def __init__(self, name, bases, body, minimized):
        super().__init__()
        self.name = name
        self.bases = bases
        self.body = body
        self.minimized = minimized

    def toBlock(self, frame, level, block):
        return ClassBlock(frame, self, level)

    def findRow(self, lineno):
        return self.body.findRow(lineno)

class IfNode(Node):
    def __init__(self, conds, bodies, minimizeds):
        super().__init__()
        self.conds = conds
        self.bodies = bodies
        self.minimizeds = minimizeds

    def toBlock(self, frame, level, block):
        return IfBlock(frame, self, level)

    def findRow(self, lineno):
        for b in self.bodies:
            loc = b.findRow(lineno)
            if loc != None:
                return loc
        return None

class WhileNode(Node):
    def __init__(self, cond, body, orelse, minimized, minimized2):
        super().__init__()
        self.cond = cond
        self.body = body
        self.orelse = orelse
        self.minimized = minimized
        self.minimized2 = minimized2

    def toBlock(self, frame, level, block):
        return WhileBlock(frame, self, level)

    def findRow(self, lineno):
        loc = self.body.findRow(lineno)
        if loc == None and self.orelse != None:
            loc = self.orelse.findRow(lineno)
        return loc

class ForNode(Node):
    def __init__(self, var, expr, body, orelse, minimized, minimized2):
        super().__init__()
        self.var = var
        self.expr = expr
        self.body = body
        self.orelse = orelse
        self.minimized = minimized
        self.minimized2 = minimized2

    def toBlock(self, frame, level, block):
        return ForBlock(frame, self, level)

    def findRow(self, lineno):
        loc = self.body.findRow(lineno)
        if loc == None and self.orelse != None:
            loc = self.orelse.findRow(lineno)
        return loc

class ReturnNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return ReturnBlock(frame, self, level)

class BreakNode(Node):
    def __init__(self):
        super().__init__()

    def toBlock(self, frame, level, block):
        return BreakBlock(frame, self, level)

class ContinueNode(Node):
    def __init__(self):
        super().__init__()

    def toBlock(self, frame, level, block):
        return ContinueBlock(frame, self, level)

class ImportNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return ImportBlock(frame, self, level)

class GlobalNode(Node):
    def __init__(self, names):
        super().__init__()
        self.names = names

    def toBlock(self, frame, level, block):
        return GlobalBlock(frame, self, level)

class AssignNode(Node):
    def __init__(self, targets, value):
        super().__init__()
        self.targets = targets
        self.value = value

    def toBlock(self, frame, level, block):
        return AssignBlock(frame, self, level)

class AugassignNode(Node):
    def __init__(self, left, right, op):
        super().__init__()
        self.left = left
        self.right = right
        self.op = op

    def toBlock(self, frame, level, block):
        return AugassignBlock(frame, self, level, self.op)

class BinaryopNode(Node):
    def __init__(self, left, right, op):
        super().__init__()
        self.left = left
        self.right = right
        self.op = op

    def toBlock(self, frame, level, block):
        return BinaryopBlock(frame, self, self.op)

class UnaryopNode(Node):
    def __init__(self, right, op):
        super().__init__()
        self.right = right
        self.op = op

    def toBlock(self, frame, level, block):
        return UnaryopBlock(frame, self, self.op)

class SubscriptNode(Node):
    def __init__(self, array, slice):
        super().__init__()
        self.array = array
        self.slice = slice

    def toBlock(self, frame, level, block):
        isSlice, lower, upper, step = self.slice
        return SubscriptBlock(frame, self, isSlice)

class FuncNode(Node):
    def __init__(self, func, args):
        super().__init__()
        self.func = func
        self.args = args

    def toBlock(self, frame, level, block):
        return FuncBlock(frame, self)

class ListNode(Node):
    def __init__(self, entries):
        super().__init__()
        self.entries = entries

    def toBlock(self, frame, level, block):
        return ListBlock(frame, self)

class TupleNode(Node):
    def __init__(self, entries):
        super().__init__()
        self.entries = entries

    def toBlock(self, frame, level, block):
        return TupleBlock(frame, self)

class AttrNode(Node):
    def __init__(self, array, ref):
        super().__init__()
        self.array = array
        self.ref = ref

    def toBlock(self, frame, level, block):
        return AttrBlock(frame, self)

class EvalNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return EvalBlock(frame, self, level)

class NumberNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return NumberBlock(frame, self.what)

class ConstantNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return ConstantBlock(frame, self.what)

class NameNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return NameBlock(frame, self.what)

class StringNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return StringBlock(frame, self.what)

class ExpressionNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return ExpressionBlock(frame, self.what, False)

class SeqNode(Node):
    def __init__(self, rows):
        super().__init__()
        self.rows = rows

    def toBlock(self, frame, level, block):
        return SeqBlock(frame, self.rows, level)

    def findRow(self, lineno):
        for i in range(len(self.rows)):
            if self.rows[i].lineno >= lineno:
                return (self, i)
            r = self.rows[i].findRow(lineno)
            if r != None:
                return r
        return None

class Block(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth=1, relief=tk.SUNKEN)
        self.isExpression = False
        self.isStatement = False
        self.isWithinDef = False if parent == None else parent.isWithinDef
        self.isWithinLoop = False if parent == None else parent.isWithinLoop

    def printIndent(self, fd):
        for i in range(self.level):
            print("    ", end="", file=fd)

    def scrollUpdate(self):
        global scrollable
        scrollable.scrollUpdate()

    def setForm(self, f):
        global curForm

        if curForm:
            curForm.grid_forget()
        curForm = f
        if f:
            f.grid(row=0, column=0, sticky=tk.E)
            f.update()
            f.catchKeys()

    def genForm(self):
        print("genForm")

    def setBlock(self, b):
        global curBlock

        if curBlock:
            curBlock.configure(bd=1, highlightbackground="white", highlightcolor="white", highlightthickness=1)
        curBlock = b
        if b:
            b.configure(bd=2, highlightbackground="red", highlightcolor="red", highlightthickness=2)
            b.update()
            b.genForm()

        self.scrollUpdate()

    def needsSaving(self):
        global saved
        saved = False

    def newPassBlock(self, parent, node, level, rowblk):
        return PassBlock(parent, node, level, rowblk)

class NameBlock(Block):
    def __init__(self, parent, vname):
        super().__init__(parent)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.vname = tk.StringVar()
        self.btn = tk.Button(self, textvariable=self.vname, fg="blue", width=0, command=self.cb)
        self.vname.set(vname)
        self.btn.grid(row=0, column=0)

    def genForm(self):
        f = NameForm(confarea, self)
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
            global printError
            if not printError:
                self.setBlock(self)
                tk.messagebox.showinfo("Print Error", "Fix bad variable name")
                printError = True

    def toNode(self):
        return NameNode(self.vname.get())

class NumberBlock(Block):
    def __init__(self, parent, value):
        super().__init__(parent)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.value = tk.StringVar()
        self.value.set(value)
        self.btn = tk.Button(self, textvariable=self.value, fg="blue", width=0, command=self.cb)
        self.btn.grid(row=0, column=0)

    def genForm(self):
        f = NumberForm(confarea, self)
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
            global printError
            if not printError:
                self.setBlock(self)
                tk.messagebox.showinfo("Print Error", "Fix bad number")
                printError = True

    def toNode(self):
        return NumberNode(self.value.get())

class ConstantBlock(Block):
    def __init__(self, parent, value):
        super().__init__(parent)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.value = tk.StringVar()
        self.value.set(value)
        self.btn = tk.Button(self, textvariable=self.value, fg="purple", width=0, command=self.cb)
        self.btn.grid(row=0, column=0)

    def genForm(self):
        self.setForm(ConstantForm(confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        print(self.value.get(), end="", file=fd)

    def toNode(self):
        return ConstantNode(self.value.get())

class StringBlock(Block):
    def __init__(self, parent, value):
        super().__init__(parent)
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
        f = StringForm(confarea, self)
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
    def __init__(self, parent, node, isSlice):
        super().__init__(parent)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.isSlice = isSlice
        if node == None:
            self.array = ExpressionBlock(self, None, False)
        else:
            self.array = ExpressionBlock(self, node.array, False)
        self.array.grid(row=0, column=0)
        tk.Button(self, text='[', command=self.cb).grid(row=0, column=1)
        self.colon1 = tk.Button(self, text=':', command=self.cb)
        self.colon2 = tk.Button(self, text=':', command=self.cb)
        self.eol = tk.Button(self, text=']', command=self.cb)

        if node == None:
            if isSlice:
                self.lower = None
            else:
                self.lower = ExpressionBlock(self, None, False)
            self.upper = self.step = None
        else:
            isSlice, lower, upper, step = node.slice
            assert isSlice == self.isSlice
            if self.isSlice:
                if lower == None:
                    self.lower = None
                else:
                    self.lower = ExpressionBlock(self, lower, False)
                if upper == None:
                    self.upper = None
                else:
                    self.upper = ExpressionBlock(self, upper, False)
                if step == None:
                    self.step = None
                else:
                    self.step = ExpressionBlock(self, step, False)
            else:
                self.lower = ExpressionBlock(self, lower, False)
                self.upper = self.step = None
        self.updateGrid()

    def cb(self):
        self.setBlock(self)

    def genForm(self):
        self.setForm(SubscriptForm(confarea, self))

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
        self.lower = ExpressionBlock(self, None, False)
        self.updateGrid()
        self.setBlock(self.lower)

    def addUpper(self):
        self.upper = ExpressionBlock(self, None, False)
        self.updateGrid()
        self.setBlock(self.upper)

    def addStep(self):
        self.step = ExpressionBlock(self, None, False)
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
    def __init__(self, parent, node):
        super().__init__(parent)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        if node == None:
            self.array = ExpressionBlock(self, None, False)
        else:
            self.array = ExpressionBlock(self, node.array, False)
        self.array.grid(row=0, column=0)
        tk.Button(self, text='.', command=self.cb).grid(row=0, column=1)
        if node == None:
            self.ref = NameBlock(self, "")
        else:
            self.ref = node.ref.toBlock(self, 0, self)
        self.ref.grid(row=0, column=2)

    def cb(self):
        self.setBlock(self)

    def genForm(self):
        self.setForm(AttrForm(confarea, self))

    def print(self, fd):
        self.array.print(fd)
        print(".", end="", file=fd)
        self.ref.print(fd)

    def toNode(self):
        return AttrNode(self.array.toNode(), self.ref.toNode())

class UnaryopBlock(Block):
    def __init__(self, parent, node, op):
        super().__init__(parent)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.op = op

        left = tk.Button(self, text=op, fg="purple", width=0, command=self.cb)
        left.grid(row=0, column=0)

        if node == None:
            self.right = ExpressionBlock(self, None, False)
        else:
            self.right = ExpressionBlock(self, node.right, False)
        self.right.grid(row=0, column=1)

    def genForm(self):
        self.setForm(UnaryopForm(confarea, self))

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
    def __init__(self, parent, node, op):
        super().__init__(parent)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.op = op

        if node == None:
            self.left = ExpressionBlock(self, None, False)
            self.middle = tk.Button(self, text=op, fg="purple", width=0, command=self.cb)
            self.right = ExpressionBlock(self, None, False)
        else:
            self.left = ExpressionBlock(self, node.left, False)
            self.middle = tk.Button(self, text=node.op, fg="purple", width=0, command=self.cb)
            self.right = ExpressionBlock(self, node.right, False)

        self.left.grid(row=0, column=0)
        self.middle.grid(row=0, column=1)
        self.right.grid(row=0, column=2)

    def genForm(self):
        self.setForm(BinaryopForm(confarea, self))

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
    def __init__(self, parent, node, level):
        super().__init__(parent)
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

        self.hdr = Block(self)
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
            self.body = SeqBlock(self, None, level + 1)
        else:
            self.body = SeqBlock(self, node.body, level + 1)
        if not self.minimized:
            self.body.grid(row=1, column=0, sticky=tk.W)

    def genForm(self):
        self.setForm(ClassForm(confarea, self))

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
            base = ExpressionBlock(self.hdr, None, False)
        else:
            base = ExpressionBlock(self.hdr, node, False)
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
        global printError

        self.printIndent(fd)
        v = self.cname.get()
        print("class {}(".format(v), end="", file=fd)
        if not v.isidentifier():
            if not printError:
                self.setBlock(self)
                tk.messagebox.showinfo("Print Error", "Fix bad method name")
                printError = True
        for i in range(len(self.bases)):
            if i != 0:
                print(", ", end="", file=fd)
            self.bases[i].print(fd)
        print("):", file=fd)
        self.body.print(fd)

    def toNode(self):
        return ClassNode(self.cname.get(), self.bases, self.body.toNode(), self.minimized)

class FuncBlock(Block):
    def __init__(self, parent, node):
        super().__init__(parent)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent

        if node == None:
            self.func = ExpressionBlock(self, None, False)
        else:
            self.func = ExpressionBlock(self, node.func, False)
        self.func.grid(row=0, column=0)

        tk.Button(self, text="(", width=0, command=self.cb).grid(row=0, column=1)
        self.eol = tk.Button(self, text=")", width=0, command=self.cb)

        self.args = [ ]
        if node != None:
            for arg in node.args:
                self.addArg(arg)
        self.gridUpdate()

    def genForm(self):
        self.setForm(FuncForm(confarea, self))

    def cb(self):
        self.setBlock(self)

    def addArg(self, node):
        if node == None:
            arg = ExpressionBlock(self, None, False)
        else:
            arg = ExpressionBlock(self, node, False)
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
    def __init__(self, parent, node):
        super().__init__(parent)
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
        self.setForm(ListForm(confarea, self))

    def cb(self):
        self.setBlock(self)

    def addEntry(self, node):
        if node == None:
            e = ExpressionBlock(self, None, False)
        else:
            e = ExpressionBlock(self, node, False)
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
    def __init__(self, parent, node):
        super().__init__(parent)
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
        self.setForm(TupleForm(confarea, self))

    def cb(self):
        self.setBlock(self)

    def addEntry(self, node):
        if node == None:
            e = ExpressionBlock(self, None, False)
        else:
            e = ExpressionBlock(self, node, False)
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
    def __init__(self, parent, node, lvalue):
        super().__init__(parent)
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

    def delete(self):
        self.what.grid_forget()
        self.what = tk.Button(self, text="?", width=0, command=self.cb)
        self.what.grid()
        self.init = False
        self.setBlock(self)
        self.needsSaving()

    def genForm(self):
        f = ExpressionForm(confarea, self, self.lvalue)
        self.setForm(f)

    def cb(self):
        self.setBlock(self)

    def exprNumber(self, v):
        self.what.grid_forget()
        self.what = NumberBlock(self, v)
        self.what.grid()
        self.init = True
        self.setBlock(self.what)
        self.needsSaving()

    def exprConstant(self, value):
        self.what.grid_forget()
        self.what = ConstantBlock(self, value)
        self.what.grid()
        self.init = True
        self.setBlock(self.what)
        self.needsSaving()

    def exprString(self):
        self.what.grid_forget()
        self.what = StringBlock(self, "")
        self.what.grid()
        self.init = True
        self.setBlock(self.what)
        self.needsSaving()

    def exprName(self, v):
        self.what.grid_forget()
        self.what = NameBlock(self, v)
        self.what.grid()
        self.init = True
        self.setBlock(self.what)
        self.needsSaving()

    def exprSubscript(self, isSlice):
        self.what.grid_forget()
        self.what = SubscriptBlock(self, None, isSlice)
        self.what.grid()
        self.init = True
        self.setBlock(self.what.array)
        self.needsSaving()

    def exprAttr(self):
        self.what.grid_forget()
        self.what = AttrBlock(self, None)
        self.what.grid()
        self.init = True
        self.setBlock(self.what.array)
        self.needsSaving()

    def exprList(self):
        self.what.grid_forget()
        self.what = ListBlock(self, None)
        self.what.grid()
        self.init = True
        self.setBlock(self.what)
        self.needsSaving()

    def exprTuple(self):
        self.what.grid_forget()
        self.what = TupleBlock(self, None)
        self.what.grid()
        self.init = True
        self.setBlock(self.what)
        self.needsSaving()

    def exprUnaryop(self, op):
        self.what.grid_forget()
        self.what = UnaryopBlock(self, None, op)
        self.what.grid()
        self.init = True
        self.setBlock(self.what.right)
        self.needsSaving()

    def exprBinaryop(self, op):
        self.what.grid_forget()
        self.what = BinaryopBlock(self, None, op)
        self.what.grid()
        self.init = True
        self.setBlock(self.what.left)
        self.needsSaving()

    def exprFunc(self):
        self.what.grid_forget()
        self.what = FuncBlock(self, None)
        self.what.grid()
        self.init = True
        self.setBlock(self.what.func)
        self.needsSaving()

    def exprPaste(self):
        global exprBuffer
        if exprBuffer != None:
            self.what.grid_forget()
            self.what = exprBuffer.toBlock(self, 0, self)
            self.what.grid(row=0, column=1, sticky=tk.W)
            self.init = True
            self.setBlock(self.what)
            self.needsSaving()

    def print(self, fd):
        if self.init:
            self.what.print(fd)
        else:
            print("?", end="", file=fd)
            global printError
            if not printError:
                self.setBlock(self)
                tk.messagebox.showinfo("Print Error", "Fix uninitialized expression")
                printError = True

    def toNode(self):
        return ExpressionNode(self.what.toNode() if self.init else None)

class AssignBlock(Block):
    def __init__(self, parent, node, level):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level

        if node == None:
            self.targets = [ExpressionBlock(self, None, True)]
            self.value = ExpressionBlock(self, None, False)
        else:
            self.targets = [ExpressionBlock(self, t, True) for t in node.targets]
            self.value = ExpressionBlock(self, node.value, False)

        column = 0
        for t in self.targets:
            t.grid(row=0, column=column)
            column += 1
            tk.Button(self, text='=', fg="purple", command=self.cb).grid(row=0, column=column)
            column += 1
        self.value.grid(row=0, column=column)

    def genForm(self):
        self.setForm(AssignForm(confarea, self))

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
    def __init__(self, parent, node, level, op):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        self.op = op
        if node == None:
            self.left = ExpressionBlock(self, None, True)
            middle = tk.Button(self, text=op, fg="purple", command=self.cb)
            self.right = ExpressionBlock(self, None, False)
        else:
            self.left = ExpressionBlock(self, node.left, True)
            middle = tk.Button(self, text=op, fg="purple", command=self.cb)
            self.right = ExpressionBlock(self, node.right, False)
        self.left.grid(row=0, column=0)
        middle.grid(row=0, column=1)
        self.right.grid(row=0, column=2)

    def genForm(self):
        self.setForm(AugassignForm(confarea, self))

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
    def __init__(self, parent, node, level, rowblk):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        self.rowblk = rowblk
        btn = tk.Button(self, text="pass", fg="red", width=0, command=self.cb)
        btn.grid(row=0, column=0)

    def genForm(self):
        f = PassForm(confarea, self)
        self.setForm(f)

    def cb(self):
        self.setBlock(self)

    def stmtEmpty(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = EmptyBlock(self.rowblk, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk)
        self.needsSaving()

    def stmtDef(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = DefBlock(self.rowblk, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what)
        self.needsSaving()

    def stmtAugassign(self, op):
        self.rowblk.what.grid_forget()
        self.rowblk.what = AssignBlock(self.rowblk, None, self.level) if op == '=' else AugassignBlock(self.rowblk, None, self.level, op)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.left)
        self.needsSaving()

    def stmtEval(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = EvalBlock(self.rowblk, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.expr)
        self.needsSaving()

    def stmtIf(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = IfBlock(self.rowblk, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.conds[0])
        self.needsSaving()

    def stmtWhile(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = WhileBlock(self.rowblk, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.cond)
        self.needsSaving()

    def stmtFor(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ForBlock(self.rowblk, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.var)
        self.needsSaving()

    def stmtReturn(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ReturnBlock(self.rowblk, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.expr)
        self.needsSaving()

    def stmtBreak(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = BreakBlock(self.rowblk, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what)
        self.needsSaving()

    def stmtContinue(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ContinueBlock(self.rowblk, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what)
        self.needsSaving()

    def stmtGlobal(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = GlobalBlock(self.rowblk, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.var)
        self.needsSaving()

    def stmtImport(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = ImportBlock(self.rowblk, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what.module)
        self.needsSaving()

    def stmtPaste(self):
        global stmtBuffer
        if stmtBuffer != None:
            self.rowblk.what.grid_forget()
            self.rowblk.what = stmtBuffer.toBlock(self.rowblk, self.level, self.rowblk)
            self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
            self.setBlock(self.rowblk.what)
        self.needsSaving()

    def print(self, fd):
        self.printIndent(fd)
        print("pass", file=fd)

    def toNode(self):
        return PassNode()

class EmptyBlock(Block):
    def __init__(self, parent, node, level):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        # btn = tk.Button(self, text="", fg="red", width=0, command=self.cb)
        # btn.grid(row=0, column=0)

    def genForm(self):
        # f = EmptyForm(confarea, self)
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
    def __init__(self, parent, node, level):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        if node == None:
            self.expr = ExpressionBlock(self, None, False)
        else:
            self.expr = ExpressionBlock(self, node.what, False)
        self.expr.grid()

    def print(self, fd):
        self.printIndent(fd)
        self.expr.print(fd)
        print("", file=fd)

    def toNode(self):
        return EvalNode(self.expr.toNode())

class ReturnBlock(Block):
    def __init__(self, parent, node, level):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        tk.Button(self, text="return", fg="red", command=self.cb).grid(row=0, column=0)
        if node == None:
            self.expr = ExpressionBlock(self, None, False)
        else:
            self.expr = ExpressionBlock(self, node.what, False)
        self.expr.grid(row=0, column=1)

    def genForm(self):
        self.setForm(ReturnForm(confarea, self))

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
    def __init__(self, parent, node, level):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        tk.Button(self, text="break", fg="red", command=self.cb).grid(row=0, column=0)

    def genForm(self):
        self.setForm(BreakForm(confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        self.printIndent(fd)
        print("break", file=fd)

    def toNode(self):
        return BreakNode()

class ContinueBlock(Block):
    def __init__(self, parent, node, level):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        tk.Button(self, text="continue", fg="red", command=self.cb).grid(row=0, column=0)

    def genForm(self):
        self.setForm(ContinueForm(confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        self.printIndent(fd)
        print("continue", file=fd)

    def toNode(self):
        return ContinueNode()

class GlobalBlock(Block):
    def __init__(self, parent, node, level):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        tk.Button(self, text="global", fg="red", command=self.cb).grid(row=0, column=0)
        if node == None:
            self.vars = [NameBlock(self, "")]
        else:
            self.vars = [NameBlock(self, n) for n in node.names]

        column = 1
        for i in range(len(self.vars)):
            if i > 0:
                tk.Button(self, text=",", command=self.cb).grid(row=0, column=column)
                column += 1
            self.vars[i].grid(row=0, column=column)
            column += 1

    def genForm(self):
        self.setForm(GlobalForm(confarea, self))

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
    def __init__(self, parent, node, level):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        tk.Button(self, text="import", fg="red", command=self.cb).grid(row=0, column=0)
        if node == None:
            self.module = NameBlock(self, "")
        else:
            self.module = NameBlock(self, node.what)
        self.module.grid(row=0, column=1)

    def genForm(self):
        self.setForm(ImportForm(confarea, self))

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
    def __init__(self, parent, node, level, row):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = False
        self.parent = parent
        self.level = level
        self.row = row
        self.comment = tk.StringVar()

        menu = tk.Button(self, text="-", width=3, command=self.listcmd)
        menu.grid(row=0, column=0, sticky=tk.W)
        if node == None:
            self.what = PassBlock(self, None, level, self)
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
        f = RowForm(confarea, self)
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
        global stmtBuffer
        stmtBuffer = self.what.toNode()
        print("statement copied")

    def delStmt(self):
        self.parent.delete(self.row)
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
    def __init__(self, parent, node, level):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = False
        self.parent = parent
        self.level = level
        self.rows = []
        if node == None:
            self.insert(0)
        else:
            for i in range(len(node.rows)):
                self.rows.append(RowBlock(self, node.rows[i], self.level, i))
            self.gridUpdate()

    def insert(self, row):
        rb = RowBlock(self, None, self.level, row)
        self.rows.insert(row, rb)
        self.gridUpdate()
        self.setBlock(rb.what)

    def delete(self, row):
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
    def __init__(self, parent, node, level):
        super().__init__(parent)
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
            self.body = SeqBlock(self, None, level + 1)
        else:
            self.body = SeqBlock(self, node.body, level + 1)
        if not self.minimized:
            self.body.grid(row=1, column=0, sticky=tk.W)

    def setHeader(self):
        self.hdr = Block(self)
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
        f = DefForm(confarea, self)
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
        global printError

        self.printIndent(fd)
        v = self.mname.get()
        print("def {}(".format(v), end="", file=fd)
        if not v.isidentifier():
            if not printError:
                self.setBlock(self)
                tk.messagebox.showinfo("Print Error", "Fix bad method name")
                printError = True
        for i in range(len(self.args)):
            if i != 0:
                print(", ", end="", file=fd)
            print(self.args[i], end="", file=fd)
            if not self.args[i].isidentifier():
                if not printError:
                    self.setBlock(self)
                    tk.messagebox.showinfo("Print Error", "Fix bad argument name")
                    printError = True
        print("):", file=fd)
        self.body.print(fd)

    def toNode(self):
        return DefNode(self.mname.get(), self.args, self.body.toNode(), self.minimized)

class IfBlock(Block):
    """
        An if statement has N conditions and N (no else) or N+1 (with else) bodies.
    """
    def __init__(self, parent, node, level):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level

        if node == None:
            self.hdrs = [Block(self)]
            self.minimizeds = [ False ]
            tk.Button(self.hdrs[0], text="if", fg="red", width=0, command=self.cb).grid(row=0, column=0)
            self.conds = [ExpressionBlock(self.hdrs[0], None, False)]
            self.conds[0].grid(row=0, column=1)
            tk.Button(self.hdrs[0], text=":", command=self.cb).grid(row=0, column=2, sticky=tk.W)
            self.bodies = [SeqBlock(self, None, level + 1)]
        else:
            self.bodies = [ SeqBlock(self, n, level + 1) for n in node.bodies ]
            self.hdrs = [ ]
            self.minimizeds = node.minimizeds
            self.conds = [ ]
            for i in range(len(self.bodies)):
                if i < len(node.conds):
                    hdr = Block(self)
                    cond = ExpressionBlock(hdr, node.conds[i], False)
                    self.conds.append(cond)
                    if i == 0:
                        tk.Button(hdr, text="if", fg="red", width=0, command=self.cb).grid(row=0, column=0)
                    else:
                        tk.Button(hdr, text="elif", fg="red", width=0, command=self.cb).grid(row=0, column=0)
                    cond.grid(row=0, column=1)
                    tk.Button(hdr, text=":", command=lambda: self.minmax(self.bodies[i])).grid(row=0, column=2, sticky=tk.W)
                else:
                    hdr = Block(self)
                    tk.Button(hdr, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
                    tk.Button(hdr, text=":", width=0, command=lambda: self.minmax(self.bodies[-1])).grid(row=0, column=1)
                self.hdrs.append(hdr)
        self.gridUpdate()

    def genForm(self):
        self.setForm(IfForm(confarea, self))

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
        self.bodies.append(SeqBlock(self, None, self.level + 1))
        hdr = Block(self)
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
        hdr = Block(self)
        tk.Button(hdr, text="elif", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        cond = ExpressionBlock(hdr, None, False)
        cond.grid(row=0, column=1)
        body = SeqBlock(self, None, self.level + 1)
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
    def __init__(self, parent, node, level):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level

        hdr = Block(self)
        tk.Button(hdr, text="while", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        self.isWithinLoop = True
        if node == None:
            self.cond = ExpressionBlock(hdr, None, False)
            self.body = SeqBlock(self, None, level + 1)
            self.orelse = None
            self.minimized = False
            self.minimized2 = False
        else:
            self.cond = ExpressionBlock(hdr, node.cond, False)
            self.body = SeqBlock(self, node.body, level + 1)
            self.orelse = None if node.orelse == None else SeqBlock(self, node.orelse, level + 1)
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
            self.hdr2 = Block(self)
            tk.Button(self.hdr2, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
            tk.Button(self.hdr2, text=":", command=self.minmax2).grid(row=0, column=1, sticky=tk.W)
            self.hdr2.grid(row=2, column=0, sticky=tk.W)
            self.orelse.grid(row=3, column=0, sticky=tk.W)

    def genForm(self):
        self.setForm(WhileForm(confarea, self))

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
        self.orelse = SeqBlock(self, None, self.level + 1)
        self.hdr2 = Block(self)
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
    def __init__(self, parent, node, level):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level

        hdr = Block(self)
        tk.Button(hdr, text="for", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        self.isWithinLoop = True
        if node == None:
            self.var = NameBlock(hdr, "")
            self.expr = ExpressionBlock(hdr, None, False)
            self.body = SeqBlock(self, None, level + 1)
            self.orelse = None
            self.minimized = False
            self.minimized2 = False
        else:
            self.var = node.var.toBlock(hdr, 0, self)
            self.expr = ExpressionBlock(hdr, node.expr, False)
            self.body = SeqBlock(self, node.body, level + 1)
            self.orelse = None if node.orelse == None else SeqBlock(self, node.orelse, level + 1)
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
            self.hdr2 = Block(self)
            tk.Button(self.hdr2, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
            tk.Button(self.hdr2, text=":", command=self.minmax2).grid(row=0, column=1, sticky=tk.W)
            self.hdr2.grid(row=2, column=0, sticky=tk.W)
            self.orelse.grid(row=3, column=0, sticky=tk.W)

    def genForm(self):
        self.setForm(ForForm(confarea, self))

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
        self.orelse = SeqBlock(self, None, self.level + 1)
        self.hdr2 = Block(self)
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

class Scrollable(Block):
    """
       Make a frame scrollable with a scrollbar
       After adding or removing widgets to the scrollable frame,
       call the update() method to refresh the scrollable area.
    """

    def __init__(self, frame, width=16):
        super().__init__(None)
        self.canvas = tk.Canvas(frame, width=725, height=475)
        self.canvas.isWithinDef = False     # ???
        self.canvas.isWithinLoop = False    # ???
        ysb = tk.Scrollbar(frame, width=width, orient=tk.VERTICAL)
        xsb = tk.Scrollbar(frame, width=width, orient=tk.HORIZONTAL)
        self.canvas.configure(bd=2, highlightbackground="red", highlightcolor="red", highlightthickness=2)

        self.stuff = Block(self.canvas)
        self.stuff.configure(bd=2, highlightbackground="green", highlightcolor="green", highlightthickness=2)

        ysb.grid(row=0, column=0, sticky=tk.N+tk.S)
        self.canvas.grid(row=0, column=1)
        xsb.grid(row=1, column=1, sticky=tk.W+tk.E)

        ysb.config(command=self.canvas.yview)
        xsb.config(command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=xsb.set)
        self.canvas.configure(yscrollcommand=ysb.set)

        self.canvas.bind('<Configure>', self.__fill_canvas)
        # self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # base class initialization
        tk.Frame.__init__(self, frame)

        # assign this obj (the inner frame) to the windows item of the canvas
        self.windows_item = self.canvas.create_window(0, 0, window=self.stuff, anchor=tk.NW)

    """
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta/120), "units")
    """

    def __fill_canvas(self, event):
        "Enlarge the windows item to the canvas width"

        canvas_width = event.width
        canvas_height = event.height
        # self.canvas.itemconfig(self.windows_item, width = canvas_width)
        # self.canvas.itemconfig(self.windows_item, height = canvas_height)

    def scrollUpdate(self):
        "Update the canvas and the scrollregion"

        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))
        # self.canvas.config(scrollregion=self.canvas.bbox("all"))

class TopLevel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth=1, relief=tk.SUNKEN)
        self.parent = parent
        self.curFile = None
        self.curDir = None
        self.program = None

        # self.configure(bd=2, highlightbackground="blue", highlightcolor="blue", highlightthickness=2)

        # menubar = tk.Frame(self, borderwidth=1, relief=tk.SUNKEN, style="Custom.TFrame")
        menubar = tk.Frame(self)
        tk.Button(menubar, text="Import", command=self.load).grid(row=0, column=0, sticky=tk.W)
        tk.Button(menubar, text="Export", command=self.save).grid(row=0, column=1, sticky=tk.W)
        tk.Button(menubar, text="Code", command=self.text).grid(row=0, column=2, sticky=tk.W)
        tk.Button(menubar, text="Run", command=self.run).grid(row=0, column=3, sticky=tk.W)
        tk.Button(menubar, text="Help", command=self.help).grid(row=0, column=4, sticky=tk.W)
        tk.Button(menubar, text="Quit", command=self.quit).grid(row=0, column=5, sticky=tk.W)
        # menubar.configure(bd=2, highlightbackground="green", highlightcolor="green", highlightthickness=2)
        menubar.grid(row=0, column=0, sticky=tk.W, columnspan=2)

        frame = tk.Frame(self, width=1200, height=500)
        frame.grid(row=1, column=0, sticky=tk.W)
        frame.grid_propagate(0)
        # frame.configure(bd=2, highlightbackground="purple", highlightcolor="purple", highlightthickness=2)

        global confarea
        # confarea = tk.Frame(frame, width=400, height=475, bd=10, highlightbackground="green", highlightcolor="green", highlightthickness=3)
        confarea = tk.Frame(frame, width=400, height=475)
        # confarea.configure(bd=2, highlightbackground="green", highlightcolor="green", highlightthickness=2)
        confarea.grid_propagate(0)

        # self.progarea = tk.Frame(frame, width=750, height=500, highlightbackground="green", highlightcolor="green", highlightthickness=3)
        self.progarea = tk.Frame(frame, width=750, height=500)
        # self.progarea = Block(frame)
        # progarea.configure(bd=2, highlightbackground="green", highlightcolor="green", highlightthickness=2)
        self.progarea.grid_propagate(0)

        global scrollable
        scrollable = Scrollable(self.progarea, width=16)
        self.program = SeqBlock(scrollable.stuff, None, 0)
        self.program.grid(sticky=tk.W)
        scrollable.scrollUpdate()

        # confarea.place(x=0, y=0)
        # self.progarea.place(x=400, y=0)
        # confarea.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.BOTH, expand=tk.YES)
        # self.progarea.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.BOTH, expand=tk.YES)
        confarea.grid(row=0, column=0, sticky=tk.N)
        self.progarea.grid(row=0, column=1, sticky=tk.NW)

        self.help()

    def print(self):
        global printError
        printError = False

        print("'=== START OF PROGRAM ==='")
        self.program.print(sys.stdout)
        print("'=== END OF PROGRAM ==='")

    def extractComments(self, code):
        comments = {}
        fd = io.StringIO(code)
        for toktype, tokval, begin, end, line in tokenize.generate_tokens(fd.readline):
            if toktype == tokenize.COMMENT:
                (row, col) = begin
                comments[row] = tokenize.untokenize([(toktype, tokval)])
        return comments

    def load(self):
        global saved

        if not saved:
            tk.messagebox.showinfo("Warning", "You must save the program first")
            saved = True
            return

        filename = tk.filedialog.askopenfilename(defaultextension='.py',
                                     filetypes=(('Python source files', '*.py'),
                                                ('All files', '*.*')))
        if filename:
            self.curFile = os.path.basename(filename)
            self.curDir = os.path.dirname(filename)
            with open(filename, "r") as fd:
                code = fd.read()
                tree = pparse.pparse(code)
                n = eval(tree)
                comments = self.extractComments(code)
                for lineno, text in comments.items():
                    (sb, i) = n.findRow(lineno)
                    row = sb.rows[i]
                    if lineno < row.lineno:
                        row = RowNode(EmptyNode(), lineno)
                        sb.rows.insert(i, row)
                    row.comment = text[1:]

                global scrollable
                if self.program != None:
                    self.program.grid_forget()
                self.program = SeqBlock(scrollable.stuff, n, 0)
                self.program.grid(sticky=tk.W)
                scrollable.scrollUpdate()

                saved = True

    def save(self):
        node = self.program.toNode()
        if self.curFile == None:
            filename = tk.filedialog.asksaveasfilename(defaultextension='.py',
                                     filetypes=(('Python source files', '*.py'),
                                                ('All files', '*.*')))
        else:
            filename = tk.filedialog.asksaveasfilename(initialdir=self.curDir, initialfile=self.curFile, defaultextension='.py',
                                     filetypes=(('Python source files', '*.py'),
                                                ('All files', '*.*')))
        if filename:
            self.curFile = os.path.basename(filename)
            self.curDir = os.path.dirname(filename)
            with open(filename, "w") as fd:
                self.program.print(fd)
                print("saved")
                global saved
                saved = True

    def run(self):
        global printError
        printError = False

        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'w') as tmp:
                self.program.print(tmp)
                tmp.close()
                if printError:
                    print("===== Fix program first =====")
                else:
                    print("===== Start running =====")
                    # subprocess.Popen(['python3', path])
                    subprocess.call(['python3', path])
                    print("===== Done =====")
        finally:
            os.remove(path)

    def help(self):
        global confarea, curForm

        if curForm:
            curForm.grid_forget()
        curForm = HelpForm(confarea, self)
        curForm.grid(row=0, column=0, sticky=tk.E)
        curForm.update()

    def text(self):
        global confarea, curForm

        if curForm:
            curForm.grid_forget()
        curForm = TextForm(confarea, self)

        global printError
        printError = False

        f = io.StringIO("")
        self.program.print(f)
        if not printError:
            curForm.settext(f.getvalue())
            curForm.grid(row=0, column=0, sticky=tk.E+tk.S+tk.W+tk.N)
            curForm.update()

    def quit(self):
        global saved
        if saved:
            sys.exit(0)
        else:
            tk.messagebox.showinfo("Warning", "You must save the program first")
            saved = True

########################################################################
def Module(body):
    return SeqNode(body)

def FunctionDef(lineno, col_offset, name, args, body, decorator_list, returns):
    return RowNode(DefNode(name, args, SeqNode(body), False), lineno)

def ClassDef(lineno, col_offset, name, bases, keywords, body, decorator_list):
    return RowNode(ClassNode(name, [ExpressionNode(x.what) for x in bases], SeqNode(body), False), lineno)

def arguments(args, vararg, kwonlyargs, kw_defaults, kwarg, defaults):
    return args

def args(lineno, col_offset, arg, annotation):
    return arg

def Assign(lineno, col_offset, targets, value):
    return RowNode(AssignNode(targets, value), lineno)

def AugAssign(lineno, col_offset, target, op, value):
    return RowNode(AugassignNode(target, value, op + '='), lineno)

def Name(lineno, col_offset, id, ctx):
    return ExpressionNode(NameNode(id))

def Subscript(lineno, col_offset, value, slice, ctx):
    return ExpressionNode(SubscriptNode(value, slice))

def Index(value):
    return (False, value, None, None)

def Slice(lower, upper, step):
    return (True, lower, upper, step)

def Num(lineno, col_offset, n):
    return ExpressionNode(NumberNode(n))

def For(lineno, col_offset, target, iter, body, orelse):
    return RowNode(ForNode(target.what, iter, SeqNode(body),
        None if orelse == [] else SeqNode(orelse), False, False), lineno)

def While(lineno, col_offset, test, body, orelse):
    return RowNode(WhileNode(test, SeqNode(body),
        None if orelse == [] else SeqNode(orelse), False, False), lineno)

def If(lineno, col_offset, test, body, orelse):
    if orelse == []:
        return RowNode(IfNode([test], [SeqNode(body)], [False]), lineno)
    elif len(orelse) == 1:
        row = orelse[0]
        assert isinstance(row, RowNode)
        stmt = row.what
        if isinstance(stmt, IfNode):
            return RowNode(IfNode([test] + stmt.conds, [SeqNode(body)] + stmt.bodies, [False] + stmt.minimizeds), lineno)
        else:
            return RowNode(IfNode([test], [SeqNode(body), SeqNode(orelse)], [False, False]), lineno)
    else:
        return RowNode(IfNode([test], [SeqNode(body), SeqNode(orelse)], [False, False]), lineno)

def Compare(lineno, col_offset, left, ops, comparators):
    assert len(ops) == 1
    assert len(comparators) == 1
    return ExpressionNode(BinaryopNode(left, comparators[0], ops[0]))

def Is():
    return "is"

def IsNot():
    return "is not"

def Eq():
    return "=="

def NotEq():
    return "!="

def Lt():
    return "<"

def LtE():
    return "<="

def Gt():
    return ">"

def GtE():
    return ">="

def Return(lineno, col_offset, value):
    return RowNode(ReturnNode(value), lineno)

def Break(lineno, col_offset):
    return RowNode(BreakNode(), lineno)

def Continue(lineno, col_offset):
    return RowNode(ContinueNode(), lineno)

def Pass(lineno, col_offset):
    return RowNode(PassNode(), lineno)

def Call(lineno, col_offset, func, args, keywords, starargs=None, kwargs=None):
    return ExpressionNode(FuncNode(func, args))

def Load():
    return None

def Store():
    return None

def List(lineno, col_offset, elts, ctx):
    return ExpressionNode(ListNode(elts))

def Tuple(lineno, col_offset, elts, ctx):
    return ExpressionNode(TupleNode(elts))

def Expr(lineno, col_offset, value):
    return RowNode(EvalNode(value), lineno)

def Attribute(lineno, col_offset, value, attr, ctx):
    return ExpressionNode(AttrNode(value, NameNode(attr)))

def arg(lineno, col_offset, arg, annotation):
    return arg

def Str(lineno, col_offset, s):
    return ExpressionNode(StringNode(s))

def NameConstant(lineno, col_offset, value):
    return ExpressionNode(ConstantNode(str(value)))

def BinOp(lineno, col_offset, left, op, right):
    return ExpressionNode(BinaryopNode(left, right, op))

def UnaryOp(lineno, col_offset, op, operand):
    return ExpressionNode(UnaryopNode(operand, op))

def BoolOp(lineno, col_offset, op, values):
    return ExpressionNode(BinaryopNode(values[0], values[1], op))

def alias(name, asname):
    return name

def keyword(arg, value):
    return None

def Import(lineno, col_offset, names):
    assert len(names) == 1
    return RowNode(ImportNode(names[0]), lineno)

def ImportFrom(lineno, col_offset, module, names, level):
    assert len(names) == 1
    return RowNode(ImportNode(names[0]), lineno)

def Global(lineno, col_offset, names):
    return RowNode(GlobalNode(names), lineno)

def Add():
    return "+"

def Sub():
    return "-"

def Div():
    return "/"

def FloorDiv():
    return "//"

def Mod():
    return "%"

def Mult():
    return "*"

def Pow():
    return "**"

def USub():
    return "-"

def Not():
    return "not"

def Or():
    return "or"

def And():
    return "and"

def In():
    return "in"

def NotIn():
    return "not in"

#####

def Try(lineno, col_offset, body, handlers, orelse, finalbody):
    assert False, "'try' not yet implemented"
    return RowNode(PassNode(), lineno)

def ExceptHandler(lineno, col_offset, type, name, body):
    assert False, "'try' not yet implemented"
    return RowNode(PassNode(), lineno)

def IfExp(lineno, col_offset, test, body, orelse):
    assert False, "'if else' not yet implemented"
    return ExpressionNode(ConstantNode("IFELSE"))

def Assert(lineno, col_offset, test, msg):
    assert False, "'assert' not yet implemented"
    return RowNode(PassNode(), lineno)

def ListComp(lineno, col_offset, elt, generators):
    assert False, "comprehensions not yet implemented"
    return ExpressionNode(ConstantNode("COMPREHENSION"))

def GeneratorExp(lineno, col_offset, elt, generators):
    assert False, "comprehensions not yet implemented"
    return ExpressionNode(ConstantNode("GENERATOR"))

def comprehension(target, iter, ifs, is_async=0):
    assert False, "comprehensions not yet implemented"
    return None

def Delete(lineno, col_offset, targets):
    assert False, "'delete' not yet implemented"
    return RowNode(PassNode(), lineno)

def Del():
    assert False, "'delete' not yet implemented"
    return None

def Lambda(lineno, col_offset, args, body):
    assert False, "'lambda' not yet implemented"
    return ExpressionNode(ConstantNode("LAMBDA"))

def Dict(lineno, col_offset, keys, values):
    assert False, "dictionaries not yet implemented"
    return ExpressionNode(ConstantNode("DICT"))

def With(lineno, col_offset, items, body):
    assert False, "'with' not yet implemented"
    return RowNode(PassNode(), lineno)

def withitem(context_expr, optional_vars):
    assert False, "'with' not yet implemented"
    return None

def Yield(lineno, col_offset, value):
    assert False, "'yield' not yet implemented"
    return RowNode(PassNode(), lineno)

########################################################################

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Code Afrique Python Editor")
    root.geometry("1250x550")
    curForm = None
    curBlock = None
    stmtBuffer = None
    exprBuffer = None
    saved = True
    tl = TopLevel(root)
    tl.grid()
    tl.grid_propagate(0)

    root.mainloop()
