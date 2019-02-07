import keyword as kw
import tkinter as tk
import tkinter.scrolledtext

class Form(tk.Frame):

    def __init__(self, parent, block):
        super().__init__(parent)
        self.parent = parent
        self.block = block
        self.isExpression = False
        self.isStatement = False
        self.catchKeys()

    def deleteKey(self, event):
        self.block.cut(False)

    def cutKey(self, event):
        self.block.cut(True)

    def copyKey(self, event):
        self.block.copy()

    def pasteKey(self, event):
        self.block.paste()

    def leftKey(self, event):
        self.block.setBlock(self.block.goLeft())

    def rightKey(self, event):
        self.block.setBlock(self.block.goRight())

    def upKey(self, event):
        self.block.setBlock(self.block.goUp())

    def downKey(self, event):
        self.block.setBlock(self.block.goDown())

    def catchKeys(self):
        self.bind("<<Cut>>", self.cutKey)
        self.bind("<<Copy>>", self.copyKey)
        self.bind("<<Paste>>", self.pasteKey)
        self.bind("<Delete>", self.deleteKey)
        self.bind("<Left>", self.leftKey)
        self.bind("<Right>", self.rightKey)
        self.bind("<Up>", self.upKey)
        self.bind("<Down>", self.downKey)
        self.bind("<Key>", self.key)
        self.focus_set()

    def key(self, ev):
        if ((ev.type != "2") or (len(ev.char) != 1)):    # check if normal KeyPress
            return
        if (ev.char == ""):
            self.deleteKey(ev)

class HelpForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="Help").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="This is a Python editor.  Each Python statement has a '-' button to the left of it that you can click on and allows you to remove the statement or add a new one.  You can also click on statements or expressions themselves to edit those.  'pass' statements can be replaced by other statements.  A '?' expression is a placeholder---you can click on it to fill it in.  Finally, ':' buttons, at the end of 'def' statements and others, can be used to minimize or maximize their bodies.").grid(sticky=tk.W)
        tk.Message(self, width=350, font="Helvetica 14", text="Under the 'Actions' menu you will find commands to show the Python code and to run it.  When you run a Python program, a console will appear that displays the output.  It also shows if the program is still running or has terminated.").grid(sticky=tk.W)

class ContainerForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="Container").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="A container captures a one-clause statement").grid(sticky=tk.W)

class ModuleForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="Module").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="A module captures an entire Python source file").grid(sticky=tk.W)

class SeqForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="Sequence of statements").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="This is a sequence of {} statements.".format(len(block.rows))).grid(sticky=tk.W)

class ClauseForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True

        # tk.Message(self, width=350, font="Helvetica 16 bold", text=block.title).grid()
        # tk.Message(self, width=350, font="Helvetica 14", text="This is a sequence of statements with a header.").grid(sticky=tk.W)
        pass

    def insertComments(self, row=0, column=0, columnspan=1):
        frame = tk.Frame(self)
        frame.grid(row=row, column=column, columnspan=columnspan)

        tk.Label(frame, text="Inline Comment: ").grid(row=0, column=0)
        self.commentR = tk.Entry(frame, font="-slant italic")
        self.commentR.bind("<Return>", self.keyEnter)
        c = self.block.commentR.get()
        self.commentR.insert(tk.END, c[1:])
        self.commentR.grid(row=0, column=1)

        tk.Label(frame, text="Multiline Comment (displayed above statement): ").grid(row=1, columnspan=2)

        self.commentU = tk.scrolledtext.ScrolledText(frame, width=40, height=6, wrap=tk.WORD, bd=2, highlightbackground="red", highlightcolor="red", highlightthickness=2, font="-slant italic")
        if self.block.commentU != None:
            c = self.block.commentU.get()
            self.commentU.insert(tk.END, c)
        self.commentU.grid(row=2, columnspan=2)

        enter = tk.Button(frame, text="Enter", command=self.cb)
        enter.grid(row=3, column=1)

    def setComments(self):
        cu = self.commentU.get("1.0", tk.END)
        if cu == "\n":
            cu = ""
        self.block.setComment(self.commentR.get(), cu)

class CondClauseForm(ClauseForm):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text=block.title).grid()
        tk.Message(self, width=350, font="Helvetica 14", text="This is a sequence of statements executed conditionally.").grid(sticky=tk.W)
        self.insertComments(row=3)

    def cb(self):
        self.setComments()
        # self.focus_set()

    def keyEnter(self, x):
        self.cb()

class ForClauseForm(ClauseForm):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text=block.title).grid()
        tk.Message(self, width=350, font="Helvetica 14", text="This is a sequence of statements within a for loop").grid(sticky=tk.W)
        self.insertComments(row=3)

    def cb(self):
        self.setComments()
        # self.focus_set()

    def keyEnter(self, x):
        self.cb()

class ExceptClauseForm(ClauseForm):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text=block.title).grid()
        tk.Message(self, width=350, font="Helvetica 14", text="This is a sequence of statements within an except clause of a try statement").grid(sticky=tk.W)
        self.insertComments(row=3)

    def cb(self):
        self.setComments()
        # self.focus_set()

    def keyEnter(self, x):
        self.cb()

class EvalForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="Evaluation Statement").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="This is a statement that evaluates an expression").grid(sticky=tk.W)

class WithClauseForm(ClauseForm):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="With Statement").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="This is a with statement.").grid(sticky=tk.W)
        self.insertComments(row=3)

    def cb(self):
        self.setComments()
        # self.focus_set()

    def keyEnter(self, x):
        self.cb()

class FrameForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="A block to frame other blocks").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="For programming convenience").grid(sticky=tk.W)

class TextForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        self.lineno = tk.Text(self, width=5, height=30, bd=2, relief=tk.SUNKEN, wrap=tk.NONE, tabs=("0.2i", tk.RIGHT))
        self.text = tk.Text(self, width=45, height=30, bd=2, relief=tk.SUNKEN, wrap=tk.NONE)
        self.ysbar = tk.Scrollbar(self)
        self.ysbar["command"] = self.scroller
        self.text["yscrollcommand"] = self.on_scroll
        self.ysbar.grid(row=0, column=2, sticky=((tk.S + tk.N) + tk.W))
        self.lineno.grid(row=0, column=0, sticky=((tk.N + tk.E) + tk.S))
        self.text.grid(row=0, column=1, sticky=(((tk.W + tk.N) + tk.E) + tk.S))
        xsbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        xsbar["command"] = self.text.xview
        self.text["xscrollcommand"] = xsbar.set
        xsbar.grid(row=1, column=1, sticky=((tk.W + tk.E) + tk.N))

    def scroller(self, *args):
        self.text.yview((* args))
        self.lineno.yview((* args))

    def on_scroll(self, *args):
        self.ysbar.set((* args))
        self.scroller("moveto", args[0])

    def settext(self, text):
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", text)
        self.text.mark_set(tk.INSERT, "1.0")
        self.text.focus()
        for i in range(text.count("\n")):
            self.lineno.insert(tk.END, "{}\n".format((i + 1)))

    def gettext(self):
        return self.text.get("1.0", (tk.END + "-1c"))

class RowForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="Select one of the actions below").grid(row=0, columnspan=3)
        tk.Button(self, text="Add a new statement below", command=self.addStmt).grid(row=1, columnspan=3)
        tk.Button(self, text="Insert a new statement above", command=self.insrtStmt).grid(row=2, columnspan=3)
        tk.Button(self, text="Move this statement up", command=self.upStmt).grid(row=3, columnspan=3)
        tk.Button(self, text="Move this statement down", command=self.downStmt).grid(row=4, columnspan=3)
        tk.Button(self, text="Delete this statement", command=self.delStmt).grid(row=5, columnspan=3)
        tk.Message(self, width=350, font="Helvetica 14", text="Keyboard shortcuts: <return> or <enter> adds a new statement below.").grid(row=6, columnspan=3)
        self.bind("<Key>", self.key)
        self.focus_set()

        if not block.isCompound():
            tk.Label(self, text="Inline Comment: ").grid(row=7, column=0)
            self.entry = tk.Entry(self, font="-slant italic")
            self.entry.bind("<Return>", self.keyEnter)
            c = block.commentR.get()
            self.entry.insert(tk.END, c[1:])
            self.entry.grid(row=7, column=1, columnspan=2)

            tk.Label(self, text="Multiline Comment (displayed above statement): ").grid(row=8, columnspan=3)
            self.commentU = tk.scrolledtext.ScrolledText(self, width=40, height=6, wrap=tk.WORD, bd=2, highlightbackground="red", highlightcolor="red", highlightthickness=2, font="-slant italic")
            if block.commentU != None:
                c = block.commentU.get()
                self.commentU.insert(tk.END, c)
            self.commentU.grid(row=9, columnspan=3)

            enter = tk.Button(self, text="Enter", command=self.cb)
            enter.grid(row=10, column=2)

        tk.Message(self, width=350, font="Helvetica 14", text="If you copied or deleted a statement, you can paste it here (see Edit menu).").grid(columnspan=3)

    def cb(self):
        cu = self.commentU.get("1.0", tk.END)
        if cu == "\n":
            cu = ""
        self.block.setComment(self.entry.get(), cu)

    def keyEnter(self, ev):
        self.cb()

    def key(self, ev):
        if ((ev.type != "2") or (len(ev.char) != 1)):    # check if normal KeyPress
            return
        if (ev.char == "\r"):
            self.addStmt()
        elif (ev.char == "\177"):
            self.delStmt()

    def addStmt(self):
        self.block.addStmt()

    def insrtStmt(self):
        self.block.insrtStmt()

    def upStmt(self):
        self.block.upStmt()

    def downStmt(self):
        self.block.downStmt()

    def delStmt(self):
        self.block.cut(False)

class PassForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = False
        self.bind("<Key>", self.key)
        self.focus_set()
        row = 0
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'pass' statement").grid(row=row, columnspan=4)
        row += 1
        tk.Message(self, width=350, font="Helvetica 14", text="A 'pass' statement does nothing.  You may select one of the statements below to replace the current 'pass' statement").grid(row=row, columnspan=4)
        row += 1
        statements = [("assert", self.stmtAssert), ("break", self.stmtBreak), ("class", self.stmtClass), ("continue", self.stmtContinue), ("def", self.stmtDef), ("del", self.stmtDel), ("for", self.stmtFor), ("global", self.stmtGlobal), ("if", self.stmtIf), ("import", self.stmtImport), ("print", self.stmtPrint), ("return", self.stmtReturn), ("try", self.stmtTry), ("while", self.stmtWhile), ("with", self.stmtWith), ("yield", self.stmtYield)]
        ncolumns = 4
        n = len(statements)
        nrows = (((n + ncolumns) - 1) // ncolumns)
        r = 0
        while (r < nrows):
            for c in range(ncolumns):
                i = (r + (c * nrows))
                if (i < n):
                    (name, stmt) = statements[i]
                    tk.Button(self, text=name, width=0, command=stmt).grid(row=row, column=c)
            r += 1
            row += 1
        tk.Button(self, text="assignment", width=0, command=self.stmtAugassign).grid(row=row, column=1, pady=10)
        self.assignop = tk.StringVar(self)
        self.assignop.set("=")
        assignops = tk.OptionMenu(self, self.assignop, "=", "+=", "-=", "*=", "/=", "//=", "%=", "**=")
        assignops.grid(row=row, column=2, sticky=tk.W)
        row += 1
        # tk.Button(self, text="evaluate an expression", width=0, command=self.stmtEval).grid(row=row, columnspan=4, pady=10)
        # row += 1
        tk.Button(self, text="call a function", width=0, command=self.stmtCall).grid(row=row, columnspan=4, pady=10)
        row += 1
        tk.Message(self, width=350, font="Helvetica 14", text="Keyboard shortcuts: '?' inserts an expression, and 'if', 'while', 'for', and 'return' statements can be inserted by typing their first letter.").grid(columnspan=4, pady=10)

    def stmtDef(self):
        self.block.stmtDef()

    def stmtClass(self):
        self.block.stmtClass()

    def stmtAugassign(self):
        self.block.stmtAugassign(self.assignop.get())

    def stmtEval(self):
        self.block.stmtEval()

    def stmtCall(self):
        self.block.stmtCall()

    def stmtIf(self):
        self.block.stmtIf()

    def stmtWhile(self):
        self.block.stmtWhile()

    def stmtWith(self):
        self.block.stmtWith()

    def stmtFor(self):
        self.block.stmtFor()

    def stmtReturn(self):
        if self.block.isWithinDef:
            self.block.stmtReturn()
        else:
            tk.messagebox.showinfo("Syntax Error", "Return statements can only be within function definitions")

    def stmtDel(self):
        self.block.stmtDel()

    def stmtPrint(self):
        self.block.stmtPrint()

    def stmtAssert(self):
        self.block.stmtAssert()

    def stmtTry(self):
        self.block.stmtTry()

    def stmtWith(self):
        self.block.stmtWith()

    def stmtYield(self):
        self.block.stmtYield()

    def stmtBreak(self):
        if self.block.isWithinLoop:
            self.block.stmtBreak()
        else:
            tk.messagebox.showinfo("Syntax Error", "Break statements can only be within loops")

    def stmtContinue(self):
        if self.block.isWithinLoop:
            self.block.stmtContinue()
        else:
            tk.messagebox.showinfo("Syntax Error", "Continue statements can only be within loops")

    def stmtGlobal(self):
        self.block.stmtGlobal()

    def stmtImport(self):
        self.block.stmtImport()

    def key(self, ev):
        if ((ev.type != "2") or (len(ev.char) != 1)):    # check if normal KeyPress
            return
        if (ev.char == "a"):
            self.stmtAssert()
        elif (self.block.isWithinLoop and (ev.char == "b")):
            self.stmtBreak()
        elif (ev.char == "c"):
            self.stmtClass()
        elif (ev.char == "d"):
            self.stmtDef()
        elif (ev.char == "f"):
            self.stmtFor()
        elif (ev.char == "g"):
            self.stmtGlobal()
        elif (ev.char == "i"):
            self.stmtIf()
        elif (ev.char == "p"):
            self.stmtPrint()
        elif (self.block.isWithinDef and (ev.char == "r")):
            self.stmtReturn()
        elif (ev.char == "t"):
            self.stmtTry()
        elif (ev.char == "w"):
            self.stmtWhile()
        elif (self.block.isWithinDef and (ev.char == "y")):
            self.stmtYield()
        elif (ev.char == "="):
            self.stmtAugassign("=")
        elif (ev.char == "?"):
            self.stmtEval()
        elif (ev.char == "("):
            self.stmtCall()
        elif (ev.char == "\177"):
            self.deleteKey(ev)

class ExpressionForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = False
        if (self.block.what != None):
            tk.Message(self, width=350, font="Helvetica 16 bold", text="Expression").grid(row=0, column=0)
            tk.Message(self, width=350, font="Helvetica 14", text="This block wraps an expression.  You can copy or delete it here.").grid(row=1, column=0)
            tk.Button(self, text="Delete this expression", command=self.delExpr).grid(row=2, column=0)
            return
        self.bind("<Key>", self.key)
        row = 0
        tk.Message(self, width=350, font="Helvetica 16 bold", text="Select an expression type").grid(row=row, column=0, columnspan=3)
        row += 1
        tk.Message(self, width=350, font="Helvetica 14", text="Either click on one of the types below or use a keyboard shortcut.  For example, if you type an alphabetic character it will automatically know you intend to enter a name, if you type a digit it will know you intend to enter a number, if you type a '=' it will assume you intend to do an assignment, and so on.").grid(row=row, column=0, columnspan=3)
        row += 1
        tk.Button(self, text="name", command=self.exprName).grid(row=row, sticky=tk.W)
        tk.Button(self, text="x.y", command=self.exprAttr).grid(row=row, column=1, sticky=tk.W)
        tk.Button(self, text="x[y]", command=self.exprIndex).grid(row=row, column=2, sticky=tk.W)
        row += 1
        tk.Button(self, text="x[y:z]", command=self.exprSlice).grid(row=row, column=0, sticky=tk.W)
        tk.Button(self, text="[..., ...]", command=self.exprList).grid(row=row, column=1, sticky=tk.W)
        tk.Button(self, text="(..., ...)", command=self.exprTuple).grid(row=row, column=2, sticky=tk.W)
        row += 1
        if (not block.isWithinStore):
            tk.Button(self, text="number", command=self.exprNumber).grid(row=row, sticky=tk.W)
            tk.Button(self, text="string", command=self.exprString).grid(row=row, column=1, sticky=tk.W)
            tk.Button(self, text="f()", command=self.exprCall).grid(row=row, column=2, sticky=tk.W)
            row += 1
            tk.Button(self, text="False", command=self.exprFalse).grid(row=row, column=0, sticky=tk.W)
            tk.Button(self, text="True", command=self.exprTrue).grid(row=row, column=1, sticky=tk.W)
            tk.Button(self, text="None", command=self.exprNone).grid(row=row, column=2, sticky=tk.W)
            row += 1
            tk.Button(self, text="{...: ...}", command=self.exprDict).grid(row=row, column=0, sticky=tk.W)
            tk.Button(self, text="x if c else y", command=self.exprIfelse).grid(row=row, column=1, sticky=tk.W)
            row += 1
            tk.Label(self, text="").grid(row=row)
            row += 1
            tk.Button(self, text="x <op> y", command=self.exprBinaryop).grid(row=row, sticky=tk.W)
            self.binaryop = tk.StringVar(self)
            self.binaryop.set("+")
            ops = tk.OptionMenu(self, self.binaryop, "+", "-", "*", "/", "//", "%", "**", "==", "!=", "<", "<=", ">", ">=", "and", "or", "in", "not in", "is", "is not")
            ops.grid(row=row, column=1, sticky=tk.W)
            row += 1
            tk.Button(self, text="<op> x", command=self.exprUnaryop).grid(row=row, sticky=tk.W)
            self.unaryop = tk.StringVar(self)
            self.unaryop.set("-")
            ops = tk.OptionMenu(self, self.unaryop, "-", "not")
            ops.grid(row=row, column=1, sticky=tk.W)
            row += 1
        tk.Message(self, width=350, font="Helvetica 14", text="You can also paste in an expression you have copied or deleted (see Edit menu).").grid(row=100, columnspan=3)

    def delExpr(self):
        self.block.cut(False)

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
        self.block.exprSubscript(False)

    def exprSlice(self):
        self.block.exprSubscript(True)

    def exprList(self):
        self.block.exprList()

    def exprTuple(self):
        self.block.exprTuple()

    def exprDict(self):
        self.block.exprDict()

    def exprUnaryop(self):
        self.block.exprUnaryop(self.unaryop.get())

    def exprBinaryop(self):
        self.block.exprBinaryop(self.binaryop.get())

    def exprCall(self):
        self.block.exprCall()

    def exprIfelse(self):
        self.block.exprIfelse()

    def key(self, ev):
        if ((ev.type != "2") or (len(ev.char) != 1)):    # check if normal KeyPress
            return
        self.block.gotKey(ev.char)

class DefClauseForm(ClauseForm):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="Set function information").grid(row=0, columnspan=2)
        tk.Message(self, width=350, font="Helvetica 14", text="A function (aka method) has a name, a list of names of arguments, and a 'body'.  With this form, you can edit the function name and arguments.").grid(row=1, columnspan=2)
        tk.Label(self, text="Method name: ").grid(row=2, sticky=tk.W)
        self.entry = tk.Entry(self)
        self.entry.insert(tk.END, block.mname.get())
        self.entry.bind("<Return>", self.keyEnter)
        self.entry.grid(row=2, column=1)
        self.args = []
        self.ndefaults = 0
        for arg in block.args:
            self.addArg(arg)

        ma = tk.Button(self, text="+ Add argument", command=self.newArg)
        ma.grid(row=100, column=0)
        # enter = tk.Button(self, text="Enter", command=self.cb)
        # enter.grid(row=100, column=1, sticky=tk.E)
        self.ndefaults = len(block.defaults)

        self.insertComments(row=101, columnspan=2)

    def newArg(self):
        self.addArg("")

    def addArg(self, name):
        nargs = len(self.args)
        tk.Label(self, text="Argument {}:".format((nargs + 1))).grid(row=(nargs + 3), sticky=tk.W)
        e = tk.Entry(self)
        e.insert(tk.END, name)
        e.grid(row=(nargs + 3), column=1)
        e.focus()
        self.args.insert(nargs - self.ndefaults, e)

    def cb(self):
        name = self.entry.get()
        if (name in kw.kwlist):
            tk.messagebox.showinfo("Name Error", "'{}' is a Python keyword".format(name))
            return
        if (not name.isidentifier()):
            tk.messagebox.showinfo("Format Error", "'{}' is not a valid function name".format(name))
            return
        args = []
        for arg in self.args:
            a = arg.get()
            if (a in kw.kwlist):
                tk.messagebox.showinfo("Name Error", "'{}' is a Python keyword".format(name))
            if (not a.isidentifier()):
                tk.messagebox.showinfo("Format Error", "'{}' is not a valid argument name".format(a))
                return
            args.append(a)
        self.setComments()
        self.block.defUpdate(name, args)
        # self.focus_set()

    def keyEnter(self, x):
        self.cb()

class ClassForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="Set class information").grid(row=0, columnspan=2)
        tk.Message(self, width=350, font="Helvetica 14", text="A class has a name, a list of bases, and a 'body'.  With this form, you can edit the class name and bases.").grid(row=1, columnspan=2)
        tk.Label(self, text="Class name: ").grid(row=2, sticky=tk.W)
        self.entry = tk.Entry(self)
        self.entry.insert(tk.END, block.cname.get())
        self.entry.bind("<Return>", self.keyEnter)
        self.entry.grid(row=2, column=1)
        enter = tk.Button(self, text="Enter", command=self.cb)
        enter.grid(row=2, column=2, sticky=tk.E)
        ma = tk.Button(self, text="+ Add a new base class", command=self.addBaseClass)
        ma.grid(row=3, column=0, columnspan=2)

    def addBaseClass(self):
        self.block.addBaseClass(None)
        self.block.setBlock(self.block.bases[(- 1)])

    def cb(self):
        name = self.entry.get()
        if (name in kw.kwlist):
            tk.messagebox.showinfo("Name Error", "'{}' is a Python keyword".format(name))
            return
        if (not name.isidentifier()):
            tk.messagebox.showinfo("Format Error", "'{}' is not a valid class name".format(name))
            return
        self.block.classUpdate(name)

    def keyEnter(self, x):
        self.cb()

class IfForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'if' statement").grid(columnspan=2)
        tk.Message(self, width=350, font="Helvetica 14", text="An 'if' statement has an 'if' clause, zero or more 'elif' clauses, and optionally an 'else' clause'.").grid(row=1, columnspan=2)
        if block.hasElse:
            eb = tk.Button(self, text="Remove 'else' clause", command=self.removeElse)
        else:
            eb = tk.Button(self, text="Add 'else' clause", command=self.addElse)
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
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'for' statement").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="A 'for' statement specifies a 'loop variable', a list, and a 'body'.  The body is executed for each entry in the list, with the loop variable set to the value of the entry.").grid(row=1)
        if (block.hasElse):
            eb = tk.Button(self, text="Remove 'else' clause", command=self.removeElse)
        else:
            eb = tk.Button(self, text="Add 'else' clause", command=self.addElse)
        eb.grid(row=2)

    def addElse(self):
        self.block.addElse()

    def removeElse(self):
        self.block.removeElse()

class WhileForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'while' statement").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="A 'while' statement has a 'loop condition' and a 'body'.  The body is executed repeatedly as long as the loop condition holds.").grid(row=1)
        if block.hasElse:
            eb = tk.Button(self, text="Remove 'else' clause", command=self.removeElse)
        else:
            eb = tk.Button(self, text="Add 'else' clause", command=self.addElse)
        eb.grid(row=2)

    def addElse(self):
        self.block.addElse()

    def removeElse(self):
        self.block.removeElse()

class ReturnForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        self.block = block
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'return' statement").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="A 'return' statement' terminates a function and, optionally, causes the function to return a value.").grid(row=1)
        if (block.expr == None):
            rv = tk.Button(self, text="Return a value", command=self.returnValue)
            rv.grid()

    def returnValue(self):
        self.block.returnValue()

class DelForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'del' statement").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="A 'del' statement' can be used to delete one or more targets.").grid(row=1)

class AssertForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'assert' statement").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="An 'assert' statement' checks to see if a condition holds.  If not, it raises an AssertionError exception.").grid(row=1)

class IfelseForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'if else' expression").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="An 'if else' expression is of the form 'x if c else y'.  It evaluates to x if c hold, otherwise to y.").grid(row=1)

class BreakForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'break' statement").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="A 'break' statement' terminates the loop that it is in.").grid(row=1)

class ContinueForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'continue' statement").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="A 'continue statement' jumps to the next iteration of the loop it is in").grid(row=1)

class GlobalForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'global' statement").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="A 'global' statement' lists names of variables that are global in scope.").grid(row=1)

class ImportForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'import' statement").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="An 'import' statement' includes a module.").grid(row=1)

class ListForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'list' expression").grid(columnspan=2)
        tk.Message(self, width=350, font="Helvetica 14", text="A 'list' is simply a sequence of expressions").grid(row=1, columnspan=2)
        ma = tk.Button(self, text="+ Add a new expression to the list", command=self.addEntry)
        ma.grid(row=2, column=0, columnspan=2)

    def addEntry(self):
        self.block.addEntry(None)
        self.block.setBlock(self.block.entries[(- 1)])

class DictForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'dict' expression").grid(columnspan=2)
        tk.Message(self, width=350, font="Helvetica 14", text="A dictionary is a map of keys to values").grid(row=1, columnspan=2)
        ma = tk.Button(self, text="+ Add a new mapping to the dictionary", command=self.addEntry)
        ma.grid(row=2, column=0, columnspan=2)

    def addEntry(self):
        self.block.addEntry(None, None)
        self.block.setBlock(self.block.keys[(- 1)])

class TupleForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'tuple' expression").grid(columnspan=2)
        tk.Message(self, width=350, font="Helvetica 14", text="A 'tuple' is simply a sequence of expressions").grid(row=1, columnspan=2)
        ma = tk.Button(self, text="+ Add a new expression to the tuple", command=self.addEntry)
        ma.grid(row=2, column=0, columnspan=2)

    def addEntry(self):
        self.block.addEntry(None)
        self.block.setBlock(self.block.entries[(- 1)])

class SubscriptForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        if block.isSlice:
            tk.Message(self, width=350, font="Helvetica 16 bold", text="'slice' expression").grid(columnspan=2)
            tk.Message(self, width=350, font="Helvetica 14", text="A slice expression is of the form x[lower:upper] or x[lower:upper:step], where 'x' is a list or a string, 'lower' some expression to index into the list or string, 'upper' some expression that signifies the end of the slice, and 'step' the size of the steps that should be taken.  If 'lower' is absent, 0 is assumed.  If 'upper' is absent, the end of the list or string is assumed.  If 'step' is absent, 1 is assumed").grid(row=1, columnspan=2)
            if (block.lower == None):
                tk.Button(self, text="add lower", command=self.addLower).grid(columnspan=2)
            if (block.upper == None):
                tk.Button(self, text="add upper", command=self.addUpper).grid(columnspan=2)
            if (block.step == None):
                tk.Button(self, text="add step", command=self.addStep).grid(columnspan=2)
        else:
            tk.Message(self, width=350, font="Helvetica 16 bold", text="'index' expression").grid(columnspan=2)
            tk.Message(self, width=350, font="Helvetica 14", text="An index expression is of the form x[y], where x is a list or a string and y some expression to index into the list or string").grid(row=1, columnspan=2)
            tk.Button(self, text="turn index into a 'slice'", command=self.makeSlice).grid(columnspan=2)

    def makeSlice(self):
        self.block.isSlice = True
        self.addUpper()

    def addLower(self):
        self.block.addLower()

    def addUpper(self):
        self.block.addUpper()

    def addStep(self):
        self.block.addStep()

class AttrForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'reference' expression").grid(columnspan=2)
        tk.Message(self, width=350, font="Helvetica 14", text="A reference expression is of the form x.y, where x is an expression that expresses an object and y the name of a field in the object.").grid(row=1, columnspan=2)

class TryForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = False
        self.isStatement = True
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'try' statement").grid(columnspan=2)
        tk.Message(self, width=350, font="Helvetica 14", text="A try statement is used to catch exceptions that may occur during evaluation of a sequence of statements.").grid(row=1, columnspan=2)

class BinaryopForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="binary operation").grid(columnspan=2)
        tk.Message(self, width=350, font="Helvetica 14", text="A binary operation is an operation with two operands.").grid(row=1, columnspan=2)

class ListopForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="List of operations").grid(columnspan=2)
        tk.Message(self, width=350, font="Helvetica 14", text="This is a list of values separated by operators.").grid(row=1, columnspan=2)

class UnaryopForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="unary operation").grid(columnspan=2)
        tk.Message(self, width=350, font="Helvetica 14", text="A unary operation is an operation with a single operand.").grid(row=1, columnspan=2)

class ConstantForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="Constant").grid(columnspan=2)
        tk.Message(self, width=350, font="Helvetica 14", text="Python supports three constants: False, True, and None.").grid(row=1, columnspan=2)

class CallForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="function calll").grid(columnspan=3)
        tk.Message(self, width=350, font="Helvetica 14", text="A function call is of the form f(list of arguments).  Here 'f' can be an expression in its own right.").grid(row=1, columnspan=3)
        ma = tk.Button(self, text="+ Add a new argument", command=self.newArg)
        ma.grid(row=2, column=0, columnspan=3)
        tk.Label(self, text="Add a named argument: ").grid(row=3)
        self.entry = tk.Entry(self, width=8)
        self.entry.bind("<Return>", self.keyEnter)
        self.entry.grid(row=3, column=1)
        enter = tk.Button(self, text="Enter", command=self.cb)
        enter.grid(row=3, column=2)

    def newArg(self):
        self.block.newArg(None)
        self.block.setBlock(self.block.args[(- 1)])

    def cb(self):
        v = self.entry.get()
        if (v in kw.kwlist):
            tk.messagebox.showinfo("Name Error", "'{}' is a Python keyword".format(v))
        elif (not v.isidentifier()):
            tk.messagebox.showinfo("Format Error", "'{}' is not a valid argument name".format(v))
        else:
            self.block.addNamedArg(v)

    def keyEnter(self, ev):
        self.cb()

class AssignForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'assignment'").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="An 'assignment' operation is used to update the variable on the left of assignment operation symbol using the value that is on the right.").grid(row=1)

class AugassignForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="'augmented assignment'").grid()
        tk.Message(self, width=350, font="Helvetica 14", text="An 'augmented assignment' operation is of the form a <op>= b, and is equivalent to a = a <op> b.").grid(row=1)

class StringForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="Set the contents of the string (no need for escaping)").grid(row=0, columnspan=2)
        tk.Label(self, text="String: ").grid(row=1)
        self.entry = tk.Entry(self)
        self.entry.bind("<Return>", self.keyEnter)
        self.entry.insert(tk.END, block.string.get())
        self.entry.grid(row=1, column=1)
        enter = tk.Button(self, text="Enter", command=self.cb)
        enter.grid(row=1, column=2)

    def cb(self):
        self.block.setContents(self.entry.get())
        self.focus_set()

    def keyEnter(self, ev):
        self.cb()

class NameForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="Set the name").grid(row=0, columnspan=2)
        tk.Label(self, text="Name: ").grid(row=1)
        self.entry = tk.Entry(self)
        self.entry.bind("<Return>", self.keyEnter)
        self.entry.insert(tk.END, block.vname.get())
        self.entry.grid(row=1, column=1)
        enter = tk.Button(self, text="Enter", command=self.cb)
        enter.grid(row=1, column=2)

    def cb(self):
        v = self.entry.get()
        if (v in kw.kwlist):
            tk.messagebox.showinfo("Name Error", "'{}' is a Python keyword".format(v))
        elif (not v.isidentifier()):
            tk.messagebox.showinfo("Format Error", "'{}' is not a valid variable name".format(v))
        else:
            self.block.setName(v)

    def keyEnter(self, ev):
        self.cb()

class NumberForm(Form):

    def __init__(self, parent, block):
        super().__init__(parent, block)
        self.isExpression = True
        self.isStatement = False
        tk.Message(self, width=350, font="Helvetica 16 bold", text="Set the number (integer or float)").grid(row=0, columnspan=2)
        tk.Label(self, text="Number: ").grid(row=1)
        self.entry = tk.Entry(self)
        self.entry.bind("<Return>", self.keyEnter)
        self.entry.insert(tk.END, block.value.get())
        self.entry.grid(row=1, column=1)
        enter = tk.Button(self, text="Enter", command=self.cb)
        enter.grid(row=1, column=2)

    def cb(self):
        try:
            float(self.entry.get())
            self.block.setValue(self.entry.get())
            self.focus_set()
        except ValueError:
            tk.messagebox.showinfo("Format Error", "'{}' is not a valid number".format(self.entry.get()))

    def keyEnter(self, ev):
        self.cb()
