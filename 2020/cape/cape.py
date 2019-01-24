from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
import subprocess
import sys
import io
import keyword
import tkinter as tk
import tkinter as ttk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename
import argparse
import ast
import contextlib
import tokenize

"""
    A row contains a statement with a menu button
    A list is a sequence of rows
    A method definion contains a header and a list
"""

class Node():
    def toBlock(self, frame):
        return None

    def setComments(self, comments):
        print("setComments")

class NilNode(Node):
    def __init__(self):
        super().__init__()   

    def toBlock(self, frame, level, block):
        return NilBlock(frame, self)

class PassNode(Node):
    def __init__(self):
        super().__init__()   

    def toBlock(self, frame, level, block):
        return PassBlock(frame, self, level, block)

class RowNode(Node):
    def __init__(self, what, lineno):
        super().__init__()   
        self.what = what
        self.lineno = lineno
        self.comment = None

    def setComments(self, comments):
        if self.lineno in comments:
            self.comment = comments[self.lineno]
            print("LINE {0}".format(self.lineno))
        self.what.setComments(comments)

class DefNode(Node):
    def __init__(self, name, args, body, minimized):
        super().__init__()   
        self.name = name
        self.args = args
        self.body = body
        self.minimized = minimized

    def toBlock(self, frame, level, block):
        return DefBlock(frame, self, level)

    def setComments(self, comments):
        self.body.setComments(comments)

class ClassNode(Node):
    def __init__(self, name, bases, body, minimized):
        super().__init__()   
        self.name = name
        self.bases = bases
        self.body = body
        self.minimized = minimized

    def toBlock(self, frame, level, block):
        return ClassBlock(frame, self, level)

    def setComments(self, comments):
        self.body.setComments(comments)

class IfNode(Node):
    def __init__(self, conds, bodies, minimizeds):
        super().__init__()   
        self.conds = conds
        self.bodies = bodies
        self.minimizeds = minimizeds

    def toBlock(self, frame, level, block):
        return IfBlock(frame, self, level)

    def setComments(self, comments):
        for b in self.bodies:
            b.setComments(comments)

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

    def setComments(self, comments):
        self.body.setComments(comments)
        if self.orelse != None:
            self.orelse.setComments(comments)

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

    def setComments(self, comments):
        self.body.setComments(comments)
        if self.orelse != None:
            self.orelse.setComments(comments)

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

class ImportNode(Node):
    def __init__(self, what):
        super().__init__()   
        self.what = what

    def toBlock(self, frame, level, block):
        return ImportBlock(frame, self, level)

class GlobalNode(Node):
    def __init__(self, what):
        super().__init__()   
        self.what = what

    def toBlock(self, frame, level, block):
        return GlobalBlock(frame, self, level)

class AssignNode(Node):
    def __init__(self, left, right, op):
        super().__init__()   
        self.left = left
        self.right = right
        self.op = op

    def toBlock(self, frame, level, block):
        return AssignBlock(frame, self, level, self.op)

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

class IndexNode(Node):
    def __init__(self, array, index):
        super().__init__()   
        self.array = array
        self.index = index

    def toBlock(self, frame, level, block):
        return IndexBlock(frame, self)

class SliceNode(Node):
    def __init__(self, array, start, finish):
        super().__init__()   
        self.array = array
        self.start = start
        self.finish = finish

    def toBlock(self, frame, level, block):
        return SliceBlock(frame, self)

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

    def setComments(self, comments):
        for row in self.rows:
            row.setComments(comments)

class Form(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = False
        self.catchKeys()

    def copy(self):
        global exprBuffer
        exprBuffer = self.block.toNode()
        print("expression copied")

    def delete(self):
        self.copy()
        self.block.parent.delete()
        print("expression deleted")

    def copyStmt(self):
        self.block.parent.copyStmt()

    def delStmt(self):
        self.block.parent.delStmt()

    def catchKeys(self):
        self.bind("<Key>", self.key)
        self.focus_set()

    def key(self, ev):
        if ev.type != "2" or len(ev.char) != 1:    # check if normal KeyPress
            return
        if ev.char == '\003':
            if self.isStatement:
                self.copyStmt()
            elif self.isExpression:
                self.copy()
        elif ev.char == '\177':
            if self.isStatement:
                self.delStmt()
            elif self.isExpression:
                self.delete()

class HelpForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="Help").grid()
        tk.Message(self, width=350, font='Helvetica 14', text="This is a Python editor.  Each Python statement has a '-' button to the left of it that you can click on and allows you to remove the statement or add a new one.  You can also click on statements or expressions themselves to edit those.  'pass' statements can be replaced by other statements.  A '?' expression is a placeholder---you can click on it to fill it in.  Finally, ':' buttons, at the end of 'def' statements and others, can be used to minimize or maximize their bodies.").grid(sticky=tk.W)
        tk.Message(self, width=350, font='Helvetica 14', text="Use 'Import' and 'Export' to load and save Python source files.  The 'Code' button renders a Python 3 program that you can send to a Python interpreter.  Or more easily, you can select 'Run'.").grid(sticky=tk.W)

class TextForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.block = block

        self.lineno = tk.Text(self, width=4, height=30, relief=tk.SUNKEN, wrap=tk.NONE, tabs=('0.2i', tk.RIGHT))
        self.text = tk.Text(self, width=48, height=30, relief=tk.SUNKEN, wrap=tk.NONE)

        ysbar = tk.Scrollbar(self)
        ysbar['command'] = self.text.yview
        self.text['yscrollcommand'] = ysbar.set
        ysbar.grid(row=0, column=2, sticky=tk.S+tk.N+tk.W)

        self.lineno.grid(row=0, column=0, sticky=tk.N+tk.E+tk.S)
        self.text.grid(row=0, column=1, sticky=tk.W+tk.N+tk.E+tk.S)

        xsbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        xsbar['command'] = self.text.xview
        self.text['xscrollcommand'] = xsbar.set
        xsbar.grid(row=1, column=1, sticky=tk.W+tk.E+tk.N)

    def settext(self, text):
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', text)
        self.text.mark_set(tk.INSERT, '1.0')
        self.text.focus()

        for i in range(text.count("\n")):
            self.lineno.insert(tk.END, "\t{}\n".format(i + 1))

    def gettext(self):
        return self.text.get('1.0', tk.END + '-1c')

class RowForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="Select one of the actions below").grid(row=0, columnspan=2)
        tk.Button(self, text="Add a new statement below",
                        command=self.addStmt).grid(row=1, columnspan=2)
        tk.Button(self, text="Insert a new statement above",
                        command=self.insrtStmt).grid(row=2, columnspan=2)
        tk.Button(self, text="Move this statement up",
                        command=self.upStmt).grid(row=3, columnspan=2)
        tk.Button(self, text="Move this statement down",
                        command=self.downStmt).grid(row=4, columnspan=2)
        tk.Button(self, text="copy",
                        command=self.copyStmt).grid(row=5)
        tk.Button(self, text="delete",
                        command=self.delStmt).grid(row=5, column=1)

        tk.Message(self, width=350, font='Helvetica 14', text="Keyboard shortcuts: <return> or <enter> adds a new statement below, while '<ctrl>c' copies the statement, and '<delete>' deletes the statement.").grid(columnspan=2)

        self.bind("<Key>", self.key)
        self.focus_set()

    def key(self, ev):
        if ev.type != "2" or len(ev.char) != 1:    # check if normal KeyPress
            return
        if ev.char == '\r':
            self.addStmt()
        elif ev.char == '\003':
            self.copyStmt()
        elif ev.char == '\177':
            self.delStmt()

    def addStmt(self):
        self.block.addStmt()

    def insrtStmt(self):
        self.block.insrtStmt()

    def upStmt(self):
        self.block.upStmt()

    def downStmt(self):
        self.block.downStmt()

    def copyStmt(self):
        self.block.copyStmt()

    def delStmt(self):
        self.block.copyStmt()
        self.block.delStmt()

class PassForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = False
        self.parent = parent
        self.block = block

        self.bind("<Key>", self.key)
        self.focus_set()

        row = 0
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'pass' statement").grid(row=row, columnspan=2)
        row += 1
        tk.Message(self, width=350, font='Helvetica 14', text="A 'pass' statement does nothing.  You may select one of the statements below to replace the current 'pass' statement").grid(row=row, columnspan=2)
        row += 1
        tk.Button(self, text="define a new method", width=0, command=self.stmtDef).grid(row=row)
        row += 1

        tk.Button(self, text="assignment", width=0, command=self.stmtAssign).grid(row=row)
        self.assignop = tk.StringVar(self)
        self.assignop.set("=")
        assignops = tk.OptionMenu(self, self.assignop, "=", "+=", "-=", "*=", "/=", "//=", "%=", "**=")
        assignops.grid(row=row, column=1, sticky=tk.W)

        row += 1
        tk.Button(self, text="evaluate an expression", width=0, command=self.stmtEval).grid(row=row)
        row += 1
        tk.Button(self, text="if statement", width=0, command=self.stmtIf).grid(row=row)
        row += 1
        tk.Button(self, text="while statement", width=0, command=self.stmtWhile).grid(row=row)
        row += 1
        tk.Button(self, text="for statement", width=0, command=self.stmtFor).grid(row=row)
        row += 1
        if self.block.isWithinLoop:
            tk.Button(self, text="break statement", width=0, command=self.stmtBreak).grid(row=row)
            row += 1
        if self.block.isWithinDef:
            tk.Button(self, text="return statement", width=0, command=self.stmtReturn).grid()
        tk.Button(self, text="global statement", width=0, command=self.stmtGlobal).grid()
        tk.Button(self, text="import statement", width=0, command=self.stmtImport).grid()
        tk.Message(self, width=350, font='Helvetica 14', text="If you copied or deleted a statement, you can paste it by clicking on the following button:").grid(columnspan=2)
        tk.Button(self, text="paste", width=0, command=self.stmtPaste).grid()
        tk.Message(self, width=350, font='Helvetica 14', text="Keyboard shortcuts: '?' inserts an expression, '<ctrl>v' pastes a statement, and 'if', 'while', 'for', and 'return' statements can be inserted by typing their first letter.").grid(columnspan=2)

    def stmtDef(self):
        self.block.stmtDef()

    def stmtAssign(self):
        self.block.stmtAssign(self.assignop.get())

    def stmtEval(self):
        self.block.stmtEval()

    def stmtIf(self):
        self.block.stmtIf()

    def stmtWhile(self):
        self.block.stmtWhile()

    def stmtFor(self):
        self.block.stmtFor()

    def stmtReturn(self):
        self.block.stmtReturn()

    def stmtBreak(self):
        self.block.stmtBreak()

    def stmtGlobal(self):
        self.block.stmtGlobal()

    def stmtImport(self):
        self.block.stmtImport()

    def stmtPaste(self):
        self.block.stmtPaste()

    def key(self, ev):
        if ev.type != "2" or len(ev.char) != 1:    # check if normal KeyPress
            return
        if ev.char == '\026':
            self.stmtPaste()
        elif ev.char == 'i':
            self.stmtIf()
        elif ev.char == 'f':
            self.stmtFor()
        elif ev.char == 'w':
            self.stmtWhile()
        elif self.block.isWithinLoop and ev.char == 'b':
            self.stmtBreak()
        elif self.block.isWithinDef and ev.char == 'r':
            self.stmtReturn()
        elif ev.char == 'd':
            self.stmtDef()
        elif ev.char == '=':
            self.stmtAssign()
        elif ev.char == '?':
            self.stmtEval()

class ExpressionForm(Form):
    def __init__(self, parent, block, lvalue):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = False
        self.parent = parent
        self.block = block
        self.lvalue = lvalue

        frame = tk.Frame(self)
        frame.bind("<Key>", self.key)
        frame.focus_set()
        frame.grid()

        row = 0
        tk.Message(frame, width=350, font='Helvetica 16 bold', text="Select an expression type").grid(row=row, columnspan=2)
        row += 1
        tk.Message(frame, width=350, font='Helvetica 14', text="Either click on one of the types below or use a keyboard shortcut.  For example, if you type an alphabetic character it will automatically know you intend to enter a name, if you type a digit it will know you intend to enter a number, if you type a '=' it will assume you intend to do an assignment, and so on.").grid(row=row, columnspan=2)
        row += 1
        tk.Button(frame, text="name", command=self.exprName).grid(row=row, sticky=tk.W)
        tk.Button(frame, text="x.y", command=self.exprAttr).grid(row=row, column=1, sticky=tk.W)
        tk.Button(frame, text="x[y]", command=self.exprIndex).grid(row=row, column=2, sticky=tk.W)
        row += 1
        if not lvalue:
            tk.Button(frame, text="x[y:z]", command=self.exprSliceYY).grid(row=row, column=0, sticky=tk.W)
            tk.Button(frame, text="x[y:]", command=self.exprSliceYN).grid(row=row, column=1, sticky=tk.W)
            row += 1
            tk.Button(frame, text="x[:z]", command=self.exprSliceNY).grid(row=row, column=0, sticky=tk.W)
            tk.Button(frame, text="x[:]", command=self.exprSliceNN).grid(row=row, column=1, sticky=tk.W)
            row += 1

            tk.Button(frame, text="number", command=self.exprNumber).grid(row=row, sticky=tk.W)
            tk.Button(frame, text="string", command=self.exprString).grid(row=row, column=1, sticky=tk.W)
            row += 1
            tk.Button(frame, text="False", command=self.exprFalse).grid(row=row, column=0, sticky=tk.W)
            tk.Button(frame, text="True", command=self.exprTrue).grid(row=row, column=1, sticky=tk.W)
            tk.Button(frame, text="None", command=self.exprNone).grid(row=row, column=2, sticky=tk.W)
            row += 1
            tk.Button(frame, text="[ ]", command=self.exprList).grid(row=row, sticky=tk.W)
            tk.Button(frame, text="f()", command=self.exprFunc).grid(row=row, column=1, sticky=tk.W)
            row += 1

            tk.Label(frame, text="").grid(row=row)
            row += 1

            tk.Button(frame, text="x <op> y", command=self.exprBinaryop).grid(row=row, sticky=tk.W)
            self.binaryop = tk.StringVar(self)
            self.binaryop.set("+")
            ops = tk.OptionMenu(frame, self.binaryop,
                "+", "-", "*", "/", "//", "%", "**",
                "==", "!=", "<", "<=", ">", ">=",
                "and", "or", "in", "not in")
            ops.grid(row=row, column=1, sticky=tk.W)
            row += 1

            tk.Button(frame, text="<op> x", command=self.exprUnaryop).grid(row=row, sticky=tk.W)
            self.unaryop = tk.StringVar(self)
            self.unaryop.set("-")
            ops = tk.OptionMenu(frame, self.unaryop, "-", "not")
            ops.grid(row=row, column=1, sticky=tk.W)
            row += 1

        tk.Message(frame, width=350, font='Helvetica 14', text="You can also paste in an expression you have copied or deleted using the '<ctrl>v' key or by clicking on the following button:").grid(row=100, columnspan=2)
        tk.Button(self, text="paste", command=self.exprPaste).grid(row=101, columnspan=2)

    def exprNumber(self):
        self.block.exprNumber("")

    def exprFalse(self):
        self.block.exprConstant("False")

    def exprTrue(self):
        self.block.exprConstant("True")

    def exprNone(self):
        self.block.exprConstant("None")

    def exprString(self):
        self.block.exprString()

    def exprName(self):
        self.block.exprName("")

    def exprAttr(self):
        self.block.exprAttr()

    def exprIndex(self):
        self.block.exprIndex()

    def exprSliceYY(self):
        self.block.exprSlice(True, True)

    def exprSliceYN(self):
        self.block.exprSlice(True, False)

    def exprSliceNY(self):
        self.block.exprSlice(False, True)

    def exprSliceNN(self):
        self.block.exprSlice(False, False)

    def exprList(self):
        self.block.exprList()

    def exprAssign(self):
        self.block.exprAssign(self.assignop.get())

    def exprUnaryop(self):
        self.block.exprUnaryop(self.unaryop.get())

    def exprBinaryop(self):
        self.block.exprBinaryop(self.binaryop.get())

    def exprFunc(self):
        self.block.exprFunc()

    def exprPaste(self):
        self.block.exprPaste()

    def key(self, ev):
        if ev.type != "2" or len(ev.char) != 1:    # check if normal KeyPress
            return
        if ev.char == '\026':
            self.block.exprPaste()
        elif ev.char.isidentifier():
            self.block.exprName(ev.char)
        elif ev.char == '.':
            self.block.exprAttr()
        elif ev.char == ']':
            self.block.exprIndex()
        elif not self.lvalue:
            if ev.char.isdigit():
                self.block.exprNumber(ev.char)
            elif ev.char == '"' or ev.char == "'":
                self.block.exprString()
            elif ev.char == '(':
                self.block.exprFunc()
            elif ev.char == '[':
                self.block.exprList()
            elif ev.char == ':':
                self.block.exprSlice(True, True)
            elif ev.char == '=':
                self.block.exprAssign("==")
            elif ev.char == '!':
                self.block.exprAssign("!=")
            elif ev.char in "+-*/%<>":
                self.block.exprBinaryop(ev.char)
            elif ev.char == "&":
                self.block.exprBinaryop("and")
            elif ev.char == "|":
                self.block.exprBinaryop("or")
            elif ev.char == "~":
                self.block.exprUnaryop("not")
            else:
                print("key event {}".format(ev.char))
        else:
            print("limited expressions left of assignment operator".format(ev.char))

class DefForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="Set method information").grid(row=0, columnspan=2)
        tk.Message(self, width=350, font='Helvetica 14', text="A method has a name, a list of names of arguments, and a 'body'.  With this form, you can edit the method name and arguments.").grid(row=1, columnspan=2)
        tk.Label(self, text="Method name: ").grid(row=2, sticky=tk.W)
        self.entry = tk.Entry(self)
        self.entry.insert(tk.END, block.mname.get())
        self.entry.bind('<Return>', self.keyEnter)
        self.entry.grid(row=2, column=1)
        self.args = [ ]
        for arg in block.args:
            self.addArg(arg)
        ma = tk.Button(self, text="+ Add argument", command=self.newArg)
        ma.grid(row=100, column=0)
        enter = tk.Button(self, text="Enter", command=self.cb)
        enter.grid(row=100, column=1, sticky=tk.E)

    def newArg(self):
        self.addArg("")

    def addArg(self, name):
        nargs = len(self.args)
        tk.Label(self, text="Argument {}:".format(nargs+1)).grid(row=nargs+3, sticky=tk.W)
        e = tk.Entry(self)
        e.insert(tk.END, name)
        e.grid(row=nargs+3, column=1)
        e.focus()
        self.args.append(e)

    def cb(self):
        name = self.entry.get()
        if name in keyword.kwlist:
            messagebox.showinfo("Name Error", "'{}' is a Python keyword".format(name))
            return
        if not name.isidentifier():
            messagebox.showinfo("Format Error", "'{}' is not a valid method name".format(name))
            return

        args = [ ]
        for arg in self.args:
            a = arg.get()
            if a in keyword.kwlist:
                messagebox.showinfo("Name Error", "'{}' is a Python keyword".format(name))
            if not a.isidentifier():
                messagebox.showinfo("Format Error", "'{}' is not a valid argument name".format(a))
                return
            args.append(a)
        self.block.defUpdate(name, args)

    def keyEnter(self, x):
        self.cb()

class ClassForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="Set class information").grid(row=0, columnspan=2)
        tk.Message(self, width=350, font='Helvetica 14', text="A method has a name, a list of bases, and a 'body'.  With this form, you can edit the method name and bases.").grid(row=1, columnspan=2)
        tk.Label(self, text="Class name: ").grid(row=2, sticky=tk.W)
        self.entry = tk.Entry(self)
        self.entry.insert(tk.END, block.cname.get())
        self.entry.bind('<Return>', self.keyEnter)
        self.entry.grid(row=2, column=1)
        enter = tk.Button(self, text="Enter", command=self.cb)
        enter.grid(row=2, column=2, sticky=tk.E)

        ma = tk.Button(self, text="+ Add a new base class", command=self.addBaseClass)
        ma.grid(row=3, column=0, columnspan=2)
        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=4, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=4, column=1)

    def addBaseClass(self):
        self.block.addBaseClass(None)
        self.block.setBlock(self.block.bases[-1])

    def cb(self):
        name = self.entry.get()
        if name in keyword.kwlist:
            messagebox.showinfo("Name Error", "'{}' is a Python keyword".format(name))
            return
        if not name.isidentifier():
            messagebox.showinfo("Format Error", "'{}' is not a valid method name".format(name))
            return

        self.block.classUpdate(name)

    def keyEnter(self, x):
        self.cb()

class IfForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'if' statement").grid(columnspan=2)
        tk.Message(self, width=350, font='Helvetica 14', text="An 'if' statement has an 'if' clause, zero or more 'elif' clauses, and optionally an 'else' clause'.").grid(row=1, columnspan=2)
        if len(block.conds) == len(block.bodies):
            eb = tk.Button(self, text="Add 'else' clause", command=self.addElse)
        else:
            eb = tk.Button(self, text="Remove 'else' clause", command=self.removeElse)
        eb.grid(row=2)
        ei = tk.Button(self, text="Insert 'elif' clause", command=self.insertElif)
        ei.grid(row=2, column=1)

    def addElse(self):
        self.block.addElse()

    def removeElse(self):
        self.block.removeElse()

    def insertElif(self):
        self.block.insertElif()

class ForForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'for' statement").grid()
        tk.Message(self, width=350, font='Helvetica 14', text="A 'for' statement specifies a 'loop variable', a list, and a 'body'.  The body is executed for each entry in the list, with the loop variable set to the value of the entry.").grid(row=1)
        if block.orelse == None:
            eb = tk.Button(self, text="Add 'else' clause", command=self.addElse)
        else:
            eb = tk.Button(self, text="Remove 'else' clause", command=self.removeElse)
        eb.grid(row=2)

    def addElse(self):
        self.block.addElse()

    def removeElse(self):
        self.block.removeElse()

class WhileForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'while' statement").grid()
        tk.Message(self, width=350, font='Helvetica 14', text="A 'while' statement has a 'loop condition' and a 'body'.  The body is executed repeatedly as long as the loop condition holds.").grid(row=1)
        if block.orelse == None:
            eb = tk.Button(self, text="Add 'else' clause", command=self.addElse)
        else:
            eb = tk.Button(self, text="Remove 'else' clause", command=self.removeElse)
        eb.grid(row=2)

    def addElse(self):
        self.block.addElse()

    def removeElse(self):
        self.block.removeElse()

class ReturnForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'return' statement").grid()
        tk.Message(self, width=350, font='Helvetica 14', text="A 'return' statement' terminates a method and causes the method to return a value.").grid(row=1)

class BreakForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'break' statement").grid()
        tk.Message(self, width=350, font='Helvetica 14', text="A 'break' statement' terminates the loop that it is in.").grid(row=1)

class GlobalForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'global' statement").grid()
        tk.Message(self, width=350, font='Helvetica 14', text="A 'global' statement' lists names of variables that are global in scope.").grid(row=1)

class ImportForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'import' statement").grid()
        tk.Message(self, width=350, font='Helvetica 14', text="An 'import' statement' includes a module.").grid(row=1)

class ListForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'list' expression").grid(columnspan=2)
        tk.Message(self, width=350, font='Helvetica 14', text="A 'list' is simply a sequence of expressions").grid(row=1,columnspan=2)
        ma = tk.Button(self, text="+ Add a new expression to the list", command=self.addEntry)
        ma.grid(row=2, column=0, columnspan=2)
        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=3, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=3, column=1)

    def addEntry(self):
        self.block.addEntry(None)
        self.block.setBlock(self.block.entries[-1])

class IndexForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'index' expression").grid(columnspan=2)
        tk.Message(self, width=350, font='Helvetica 14', text="An index expression is of the form x[y], where x is a list or a string and y some expression to index into the list or string").grid(row=1,columnspan=2)
        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=2, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=2, column=1)

class AttrForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'reference' expression").grid(columnspan=2)
        tk.Message(self, width=350, font='Helvetica 14', text="A reference expression is of the form x.y, where x is an expression that expresses an object and y the name of a field in the object.").grid(row=1,columnspan=2)
        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=2, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=2, column=1)

class SliceForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'slice' expression").grid(columnspan=2)
        tk.Message(self, width=350, font='Helvetica 14', text="A slice expression is of the form x[y:z], where x is a list or a string, y some expression to index into the list or string, and z some expression that signifies the end of the slice.  If y is absent, 0 is assumed.  If z is absent, the end of the list or string is assumed.").grid(row=1,columnspan=2)
        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=2, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=2, column=1)

class BinaryopForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="binary operation").grid(columnspan=2)
        tk.Message(self, width=350, font='Helvetica 14', text="A binary operation is an operation with two operands.").grid(row=1,columnspan=2)
        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=2, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=2, column=1)

class UnaryopForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="unary operation").grid(columnspan=2)
        tk.Message(self, width=350, font='Helvetica 14', text="A unary operation is an operation with a single operand.").grid(row=1,columnspan=2)
        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=2, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=2, column=1)

class ConstantForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="Constant").grid(columnspan=2)
        tk.Message(self, width=350, font='Helvetica 14', text="Python supports three constants: False, True, and None.").grid(row=1,columnspan=2)
        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=2, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=2, column=1)

class NilForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="empty index").grid(columnspan=2)
        tk.Message(self, width=350, font='Helvetica 14', text="An empty index is used in a slice to indicate the beginning or end of a slice.  You can delete it if you want to set the beginning or end.").grid(row=1,columnspan=2)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=2, columnspan=2)

class FuncForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="function calll").grid(columnspan=2)
        tk.Message(self, width=350, font='Helvetica 14', text="A function call is of the form f(list of arguments).  Here 'f' can be an expression in its own right.").grid(row=1, columnspan=2)
        ma = tk.Button(self, text="+ Add a new argument", command=self.addArg)
        ma.grid(row=2, column=0, columnspan=2)
        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=3, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=3, column=1)

    def addArg(self):
        self.block.addArg(None)
        self.block.setBlock(self.block.args[-1])

class AssignForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'assignment'").grid()
        tk.Message(self, width=350, font='Helvetica 14', text="An 'assignment' operation is used to update the variable on the left of assignment operation symbol using the value that is on the right.").grid(row=1)

class StringForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="Set the contents of the string (no need for escaping)").grid(row=0, columnspan=2)
        tk.Label(self, text="String: ").grid(row=1)
        self.entry = tk.Entry(self)
        self.entry.bind('<Return>', self.keyEnter)
        self.entry.insert(tk.END, block.string.get())
        self.entry.grid(row=1, column=1)
        enter = tk.Button(self, text="Enter", command=self.cb)
        enter.grid(row=1, column=2)
        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=2, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=2, column=1)

    def cb(self):
        self.block.setContents(self.entry.get())

    def keyEnter(self, ev):
        self.cb()

class NameForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="Set the name").grid(row=0, columnspan=2)
        tk.Label(self, text="Name: ").grid(row=1)
        self.entry = tk.Entry(self)
        self.entry.bind('<Return>', self.keyEnter)
        self.entry.insert(tk.END, block.vname.get())
        self.entry.grid(row=1, column=1)
        enter = tk.Button(self, text="Enter", command=self.cb)
        enter.grid(row=1, column=2)
        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=2, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=2, column=1)

    def cb(self):
        v = self.entry.get()
        if v in keyword.kwlist:
            messagebox.showinfo("Name Error", "'{}' is a Python keyword".format(v))
        elif not v.isidentifier():
            messagebox.showinfo("Format Error", "'{}' is not a valid variable name".format(v))
        else:
            self.block.setName(v)

    def keyEnter(self, ev):
        self.cb()

class NumberForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)   
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="Set the number (integer or float)").grid(row=0, columnspan=2)
        tk.Label(self, text="Number: ").grid(row=1)
        self.entry = tk.Entry(self)
        self.entry.bind('<Return>', self.keyEnter)
        self.entry.insert(tk.END, block.value.get())
        self.entry.grid(row=1, column=1)
        enter = tk.Button(self, text="Enter", command=self.cb)
        enter.grid(row=1, column=2)
        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=2, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=2, column=1)

    def cb(self):
        try:
            float(self.entry.get())
            self.block.setValue(self.entry.get())
        except ValueError:
            messagebox.showinfo("Format Error", "'{}' is not a valid number".format(self.entry.get()))

    def keyEnter(self, ev):
        self.cb()

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
        scrollable.update()

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
                messagebox.showinfo("Print Error", "Fix bad variable name")
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
                messagebox.showinfo("Print Error", "Fix bad number")
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

class IndexBlock(Block):
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
        tk.Button(self, text='[', command=self.cb).grid(row=0, column=1)
        if node == None:
            self.index = ExpressionBlock(self, None, False)
        else:
            self.index = ExpressionBlock(self, node.index, False)
        self.index.grid(row=0, column=2)
        tk.Button(self, text=']', command=self.cb).grid(row=0, column=3)

    def cb(self):
        self.setBlock(self)

    def genForm(self):
        self.setForm(IndexForm(confarea, self))

    def print(self, fd):
        self.array.print(fd)
        print("[", end="", file=fd)
        self.index.print(fd)
        print("]", end="", file=fd)

    def toNode(self):
        return IndexNode(self.array.toNode(), self.index.toNode())

class SliceBlock(Block):
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
        tk.Button(self, text='[', command=self.cb).grid(row=0, column=1)
        if node == None:
            self.start = ExpressionBlock(self, None, False)
        else:
            self.start = ExpressionBlock(self, node.start, False)
        self.start.grid(row=0, column=2)
        tk.Button(self, text=':', command=self.cb).grid(row=0, column=3)
        if node == None:
            self.finish = ExpressionBlock(self, None, False)
        else:
            self.finish = ExpressionBlock(self, node.finish, False)
        self.finish.grid(row=0, column=4)
        tk.Button(self, text=']', command=self.cb).grid(row=0, column=5)

    def cb(self):
        self.setBlock(self)

    def genForm(self):
        self.setForm(SliceForm(confarea, self))

    def print(self,fd):
        self.array.print(fd)
        print("[", end="", file=fd)
        self.start.print(fd)
        print(":", end="", file=fd)
        self.finish.print(fd)
        print("]", end="", file=fd)

    def toNode(self):
        return SliceNode(self.array.toNode(), self.start.toNode(), self.finish.toNode())

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
                messagebox.showinfo("Print Error", "Fix bad method name")
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

    def exprIndex(self):
        self.what.grid_forget()
        self.what = IndexBlock(self, None)
        self.what.grid()
        self.init = True
        self.setBlock(self.what.array)
        self.needsSaving()

    def exprSlice(self, left, right):
        self.what.grid_forget()
        array = ExpressionNode(None)
        start = ExpressionNode(None if left else NilNode())
        finish = ExpressionNode(None if right else NilNode())
        self.what = SliceBlock(self, SliceNode(array, start, finish))
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

    def exprAssign(self, op):
        self.what.grid_forget()
        self.what = AssignBlock(self, None, 0, op)
        self.what.grid()
        self.init = True
        self.setBlock(self.what.left)
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
                messagebox.showinfo("Print Error", "Fix uninitialized expression")
                printError = True

    def toNode(self):
        return ExpressionNode(self.what.toNode() if self.init else None)

class NilBlock(Block):
    def __init__(self, parent, node):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = False
        self.parent = parent
        tk.Button(self, text="", width=0, command=self.cb).grid()

    def genForm(self):
        f = NilForm(confarea, self)
        self.setForm(f)

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        pass

    def toNode(self):
        return NilNode()

class AssignBlock(Block):
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
        self.setForm(AssignForm(confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        self.printIndent(fd)
        self.left.print(fd)
        print(" {} ".format(self.op), end="", file=fd)
        self.right.print(fd)
        print("", file=fd)

    def toNode(self):
        return AssignNode(self.left.toNode(), self.right.toNode(), self.op)

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

    def stmtDef(self):
        self.rowblk.what.grid_forget()
        self.rowblk.what = DefBlock(self.rowblk, None, self.level)
        self.rowblk.what.grid(row=0, column=1, sticky=tk.W)
        self.setBlock(self.rowblk.what)
        self.needsSaving()

    def stmtAssign(self, op):
        self.rowblk.what.grid_forget()
        self.rowblk.what = AssignBlock(self.rowblk, None, self.level, op)
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

class GlobalBlock(Block):
    def __init__(self, parent, node, level):
        super().__init__(parent)   
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.level = level
        tk.Button(self, text="global", fg="red", command=self.cb).grid(row=0, column=0)
        if node == None:
            self.var = NameBlock(self, "")
        else:
            self.var = NameBlock(self, node.what)
        self.var.grid(row=0, column=1)

    def genForm(self):
        self.setForm(GlobalForm(confarea, self))

    def cb(self):
        self.setBlock(self)

    def print(self, fd):
        self.printIndent(fd)
        print("global ", end="", file=fd)
        self.var.print(fd)
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

        menu = tk.Button(self, text="-", width=3, command=self.listcmd)
        menu.grid(row=0, column=0, sticky=tk.W)
        if node == None:
            self.what = PassBlock(self, None, level, self)
        else:
            self.what = node.what.toBlock(self, level, self)
        self.what.grid(row=0, column=1, sticky=tk.W)
        if node != None and node.comment != None:
            tk.Label(self, text=node.comment).grid(row=0, column=2, sticky=tk.N+tk.W)

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
        self.what.print(fd)

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
                messagebox.showinfo("Print Error", "Fix bad method name")
                printError = True
        for i in range(len(self.args)):
            if i != 0:
                print(", ", end="", file=fd)
            print(self.args[i], end="", file=fd)
            if not self.args[i].isidentifier():
                if not printError:
                    self.setBlock(self)
                    messagebox.showinfo("Print Error", "Fix bad argument name")
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
            self.minimizeds = [ Falsies[0] ]
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
        self.gridUpdate()

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
        self.isWithinLoop = True

        hdr = Block(self)
        tk.Button(hdr, text="while", fg="red", width=0, command=self.cb).grid(row=0, column=0)
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

    def minmax2(self):
        if self.minimized2:
            self.orelse.grid(row=3, column=0, sticky=tk.W)
            self.update()
            self.minimized2 = False
        else:
            self.orelse.grid_forget()
            self.minimized2 = True

    def addElse(self):
        self.orelse = SeqBlock(self, None, self.level + 1)
        self.hdr2 = Block(self)
        tk.Button(self.hdr2, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        tk.Button(self.hdr2, text=":", width=0, command=self.minmax2).grid(row=0, column=1)
        self.hdr2.grid(row=2, column=0, sticky=tk.W)
        self.orelse.grid(row=3, column=0, sticky=tk.W)
        self.setBlock(self.orelse.what)
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
        self.isWithinLoop = True

        hdr = Block(self)
        tk.Button(hdr, text="for", fg="red", width=0, command=self.cb).grid(row=0, column=0)
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

    def minmax2(self):
        if self.minimized2:
            self.orelse.grid(row=3, column=0, sticky=tk.W)
            self.update()
            self.minimized2 = False
        else:
            self.orelse.grid_forget()
            self.minimized2 = True

    def addElse(self):
        self.orelse = SeqBlock(self, None, self.level + 1)
        self.hdr2 = Block(self)
        tk.Button(self.hdr2, text="else", fg="red", width=0, command=self.cb).grid(row=0, column=0)
        tk.Button(self.hdr2, text=":", width=0, command=self.minmax2).grid(row=0, column=1)
        self.hdr2.grid(row=2, column=0, sticky=tk.W)
        self.orelse.grid(row=3, column=0, sticky=tk.W)
        self.setBlock(self.orelse.what)
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
        self.canvas = tk.Canvas(frame, width=750, height=475)
        sb = tk.Scrollbar(frame, width=width, orient=tk.VERTICAL)

        sb.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb.config(command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)

        self.canvas.bind('<Configure>', self.__fill_canvas)

        # base class initialization
        tk.Frame.__init__(self, frame)         

        # assign this obj (the inner frame) to the windows item of the canvas
        self.windows_item = self.canvas.create_window(0,0, window=self, anchor=tk.NW)

    def __fill_canvas(self, event):
        "Enlarge the windows item to the canvas width"

        canvas_width = event.width
        self.canvas.itemconfig(self.windows_item, width = canvas_width)        

    def update(self):
        "Update the canvas and the scrollregion"

        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))

class TopLevel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth=1, relief=tk.SUNKEN)   
        self.parent = parent
        self.curFile = None
        self.curDir = None

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
        # progarea.configure(bd=2, highlightbackground="green", highlightcolor="green", highlightthickness=2)
        self.progarea.grid_propagate(0)

        global scrollable
        scrollable = Scrollable(self.progarea, width=16)
        self.program = SeqBlock(scrollable, None, 0)
        self.program.grid(sticky=tk.W)
        scrollable.update()

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
        if not saved:
            messagebox.showinfo("Warning", "You must save the program first")
            return

        filename = askopenfilename(defaultextension='.py',
                                     filetypes=(('Python source files', '*.py'),
                                                ('All files', '*.*')))
        if filename:
            self.curFile = os.path.basename(filename)
            self.curDir = os.path.dirname(filename)
            with open(filename, "r") as fd:
                code = fd.read()
                rtree = ast.parse(code)
                ftree = pformat(rtree)
                # with open("cape.log", "w") as log:
                #     log.write(ftree)
                n = eval(ftree)
                comments = self.extractComments(code)
                n.setComments(comments)
                print(comments)

                global scrollable
                if self.program != None:
                    self.program.grid_forget()
                self.program = SeqBlock(scrollable, n, 0)
                self.program.grid(sticky=tk.W)
                scrollable.update()

    def save(self):
        node = self.program.toNode()
        if self.curFile == None:
            filename = asksaveasfilename(defaultextension='.py',
                                     filetypes=(('Python source files', '*.py'),
                                                ('All files', '*.*')))
        else:
            filename = asksaveasfilename(initialdir=self.curDir, initialfile=self.curFile, defaultextension='.py',
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
                    subprocess.call(['python', path])
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
        curForm.settext(f.getvalue())
        curForm.grid(row=0, column=0, sticky=tk.E+tk.S+tk.W+tk.N)
        curForm.update()

    def quit(self):
        if saved:
            sys.exit(0)
        else:
            messagebox.showinfo("Warning", "You must save the program first")

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
    assert len(targets) == 1
    return RowNode(AssignNode(targets[0], value, "="), lineno)

def AugAssign(lineno, col_offset, target, op, value):
    return RowNode(AssignNode(target, value, op + '='), lineno)

def Name(lineno, col_offset, id, ctx):
    return ExpressionNode(NameNode(id))

def Subscript(lineno, col_offset, value, slice, ctx):
    return ExpressionNode(IndexNode(value, slice))

def Index(value):
    return value

def Num(lineno, col_offset, n):
    return ExpressionNode(NumberNode(n))

def For(lineno, col_offset, target, iter, body, orelse):
    return RowNode(ForNode(target.what, iter, SeqNode(body),
        None if orelse == [] else SeqNode(orelse), False, False), lineno)

def While(lineno, col_offset, test, body, orelse):
    return RowNode(WhileNode(test, SeqNode(body), lineno,
        None if orelse == [] else SeqNode(orelse), False, False))

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
    assert len(names) == 1
    return RowNode(GlobalNode(names[0]), lineno)

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

########################################################################
# This code borrowed from https://github.com/asottile/astpretty

AST = (ast.AST,)
expr_context = (ast.expr_context,)

try:  # pragma: no cover (with typed-ast)
    from typed_ast import ast27
    from typed_ast import ast3
except ImportError:  # pragma: no cover (without typed-ast)
    typed_support = False
else:  # pragma: no cover (with typed-ast)
    AST += (ast27.AST, ast3.AST)
    expr_context += (ast27.expr_context, ast3.expr_context)
    typed_support = True


def _is_sub_node(node):
    return isinstance(node, AST) and not isinstance(node, expr_context)


def _is_leaf(node):
    for field in node._fields:
        attr = getattr(node, field)
        if _is_sub_node(attr):
            return False
        elif isinstance(attr, (list, tuple)):
            for val in attr:
                if _is_sub_node(val):
                    return False
    else:
        return True


def _fields(n, show_offsets=True):
    if show_offsets and hasattr(n, 'lineno') and hasattr(n, 'col_offset'):
        return ('lineno', 'col_offset') + n._fields
    else:
        return n._fields


def _leaf(node, show_offsets=True):
    if isinstance(node, AST):
        return '{}({})'.format(
            type(node).__name__,
            ', '.join(
                '{}={}'.format(
                    field,
                    _leaf(getattr(node, field), show_offsets=show_offsets),
                )
                for field in _fields(node, show_offsets=show_offsets)
            ),
        )
    elif isinstance(node, list):
        return '[{}]'.format(
            ', '.join(_leaf(x, show_offsets=show_offsets) for x in node),
        )
    else:
        return repr(node)


def pformat(node, indent='    ', show_offsets=True, _indent=0):
    if node is None:  # pragma: no cover (py35+ unpacking in literals)
        return repr(node)
    elif isinstance(node, str):  # pragma: no cover (ast27 typed-ast args)
        return repr(node)
    elif _is_leaf(node):
        return _leaf(node, show_offsets=show_offsets)
    else:
        class state:
            indent = _indent

        @contextlib.contextmanager
        def indented():
            state.indent += 1
            yield
            state.indent -= 1

        def indentstr():
            return state.indent * indent

        def _pformat(el, _indent=0):
            return pformat(
                el, indent=indent, show_offsets=show_offsets,
                _indent=_indent,
            )

        out = type(node).__name__ + '(\n'
        with indented():
            for field in _fields(node, show_offsets=show_offsets):
                attr = getattr(node, field)
                if attr == []:
                    representation = '[]'
                elif (
                        isinstance(attr, list) and
                        len(attr) == 1 and
                        isinstance(attr[0], AST) and
                        _is_leaf(attr[0])
                ):
                    representation = '[{}]'.format(_pformat(attr[0]))
                elif isinstance(attr, list):
                    representation = '[\n'
                    with indented():
                        for el in attr:
                            representation += '{}{},\n'.format(
                                indentstr(), _pformat(el, state.indent),
                            )
                    representation += indentstr() + ']'
                elif isinstance(attr, AST):
                    representation = _pformat(attr, state.indent)
                else:
                    representation = repr(attr)
                out += '{}{}={},\n'.format(indentstr(), field, representation)
        out += indentstr() + ')'
        return out

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
