import keyword as kw
import tkinter as tk

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
        tk.Message(self, width=350, font='Helvetica 16 bold', text="Select one of the actions below").grid(row=0, columnspan=3)
        tk.Button(self, text="Add a new statement below",
                        command=self.addStmt).grid(row=1, columnspan=3)
        tk.Button(self, text="Insert a new statement above",
                        command=self.insrtStmt).grid(row=2, columnspan=3)
        tk.Button(self, text="Move this statement up",
                        command=self.upStmt).grid(row=3, columnspan=3)
        tk.Button(self, text="Move this statement down",
                        command=self.downStmt).grid(row=4, columnspan=3)
        tk.Button(self, text="copy",
                        command=self.copyStmt).grid(row=5)
        tk.Button(self, text="delete",
                        command=self.delStmt).grid(row=5, column=1)

        tk.Message(self, width=350, font='Helvetica 14', text="Keyboard shortcuts: <return> or <enter> adds a new statement below, while '<ctrl>c' copies the statement, and '<delete>' deletes the statement.").grid(row=6, columnspan=3)

        self.bind("<Key>", self.key)
        self.focus_set()

        tk.Label(self, text="Comment: ").grid(row=7)
        self.entry = tk.Entry(self)
        self.entry.bind('<Return>', self.keyEnter)
        c = self.block.comment.get()
        if len(c) > 0 and c[0] == '#':
            c = c[1:]
        self.entry.insert(tk.END, c)
        self.entry.grid(row=7, column=1)
        enter = tk.Button(self, text="Enter", command=self.cb)
        enter.grid(row=7, column=2)

    def cb(self):
        self.block.setComment(self.entry.get())

    def keyEnter(self, ev):
        self.cb()

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

        tk.Button(self, text="assignment", width=0, command=self.stmtAugassign).grid(row=row)
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
            tk.Button(self, text="continue statement", width=0, command=self.stmtContinue).grid(row=row)
            row += 1
        if self.block.isWithinDef:
            tk.Button(self, text="return statement", width=0, command=self.stmtReturn).grid()
        tk.Button(self, text="global statement", width=0, command=self.stmtGlobal).grid()
        tk.Button(self, text="import statement", width=0, command=self.stmtImport).grid()
        tk.Button(self, text="empty line", width=0, command=self.stmtEmpty).grid()
        tk.Message(self, width=350, font='Helvetica 14', text="If you copied or deleted a statement, you can paste it by clicking on the following button:").grid(columnspan=2)
        tk.Button(self, text="paste", width=0, command=self.stmtPaste).grid()
        tk.Message(self, width=350, font='Helvetica 14', text="Keyboard shortcuts: '?' inserts an expression, '<ctrl>v' pastes a statement, and 'if', 'while', 'for', and 'return' statements can be inserted by typing their first letter.").grid(columnspan=2)

    def stmtEmpty(self):
        self.block.stmtEmpty()

    def stmtDef(self):
        self.block.stmtDef()

    def stmtAugassign(self):
        self.block.stmtAugassign(self.assignop.get())

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

    def stmtContinue(self):
        self.block.stmtContinue()

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
        elif ev.char == 'c':
            self.stmtClass()
        elif ev.char == '=':
            self.stmtAugassign('=')
        elif ev.char == '?':
            self.stmtEval()
        elif ev.char == '\r':
            self.stmtEmpty()

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
            tk.Button(frame, text="number", command=self.exprNumber).grid(row=row, sticky=tk.W)
            tk.Button(frame, text="string", command=self.exprString).grid(row=row, column=1, sticky=tk.W)
            row += 1
            tk.Button(frame, text="False", command=self.exprFalse).grid(row=row, column=0, sticky=tk.W)
            tk.Button(frame, text="True", command=self.exprTrue).grid(row=row, column=1, sticky=tk.W)
            tk.Button(frame, text="None", command=self.exprNone).grid(row=row, column=2, sticky=tk.W)
            row += 1
            tk.Button(frame, text="[...]", command=self.exprList).grid(row=row, sticky=tk.W)
            tk.Button(frame, text="(...)", command=self.exprTuple).grid(row=row, column=1, sticky=tk.W)
            row += 1
            tk.Button(frame, text="f()", command=self.exprFunc).grid(row=row, column=0, sticky=tk.W)
            tk.Button(frame, text="x[y:z]", command=self.exprSlice).grid(row=row, column=1, sticky=tk.W)
            row += 1

            tk.Label(frame, text="").grid(row=row)
            row += 1

            tk.Button(frame, text="x <op> y", command=self.exprBinaryop).grid(row=row, sticky=tk.W)
            self.binaryop = tk.StringVar(self)
            self.binaryop.set("+")
            ops = tk.OptionMenu(frame, self.binaryop,
                "+", "-", "*", "/", "//", "%", "**",
                "==", "!=", "<", "<=", ">", ">=",
                "and", "or", "in", "not in", "is", "is not")
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
        self.block.exprSubscript(False)

    def exprSlice(self):
        self.block.exprSubscript(True)

    def exprList(self):
        self.block.exprList()

    def exprTuple(self):
        self.block.exprTuple()

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
            self.block.exprSubscript()
        elif not self.lvalue:
            if ev.char.isdigit():
                self.block.exprNumber(ev.char)
            elif ev.char == '"' or ev.char == "'":
                self.block.exprString()
            elif ev.char == '(':
                self.block.exprFunc()
            elif ev.char == '[':
                self.block.exprList()
            elif ev.char == '=':
                self.block.exprBinaryop("==")
            elif ev.char == '!':
                self.block.exprBinaryop("!=")
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
        if name in kw.kwlist:
            tk.messagebox.showinfo("Name Error", "'{}' is a Python keyword".format(name))
            return
        if not name.isidentifier():
            tk.messagebox.showinfo("Format Error", "'{}' is not a valid method name".format(name))
            return

        args = [ ]
        for arg in self.args:
            a = arg.get()
            if a in kw.kwlist:
                tk.messagebox.showinfo("Name Error", "'{}' is a Python keyword".format(name))
            if not a.isidentifier():
                tk.messagebox.showinfo("Format Error", "'{}' is not a valid argument name".format(a))
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
        if name in kw.kwlist:
            tk.messagebox.showinfo("Name Error", "'{}' is a Python keyword".format(name))
            return
        if not name.isidentifier():
            tk.messagebox.showinfo("Format Error", "'{}' is not a valid method name".format(name))
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

class ContinueForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)
        self.isExpression = False
        self.isStatement = True
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'continue' statement").grid()
        tk.Message(self, width=350, font='Helvetica 14', text="A 'continue statement' jumps to the next iteration of the loop it is in").grid(row=1)

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

class TupleForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'tuple' expression").grid(columnspan=2)
        tk.Message(self, width=350, font='Helvetica 14', text="A 'tuple' is simply a sequence of expressions").grid(row=1,columnspan=2)
        ma = tk.Button(self, text="+ Add a new expression to the tuple", command=self.addEntry)
        ma.grid(row=2, column=0, columnspan=2)
        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=3, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=3, column=1)

    def addEntry(self):
        self.block.addEntry(None)
        self.block.setBlock(self.block.entries[-1])

class SubscriptForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block

        if block.isSlice:
            tk.Message(self, width=350, font='Helvetica 16 bold', text="'slice' expression").grid(columnspan=2)
            tk.Message(self, width=350, font='Helvetica 14', text="A slice expression is of the form x[lower:upper] or x[lower:upper:step], where 'x' is a list or a string, 'lower' some expression to index into the list or string, 'upper' some expression that signifies the end of the slice, and 'step' the size of the steps that should be taken.  If 'lower' is absent, 0 is assumed.  If 'upper' is absent, the end of the list or string is assumed.  If 'step' is absent, 1 is assumed").grid(row=1,columnspan=2)
            if block.lower == None:
                tk.Button(self, text="add lower", command=self.addLower).grid(columnspan=2)
            if block.upper == None:
                tk.Button(self, text="add upper", command=self.addUpper).grid(columnspan=2)
            if block.step == None:
                tk.Button(self, text="add step", command=self.addStep).grid(columnspan=2)

        else:
            tk.Message(self, width=350, font='Helvetica 16 bold', text="'index' expression").grid(columnspan=2)
            tk.Message(self, width=350, font='Helvetica 14', text="An index expression is of the form x[y], where x is a list or a string and y some expression to index into the list or string").grid(row=1,columnspan=2)
            tk.Button(self, text="turn index into a 'slice'", command=self.makeSlice).grid(columnspan=2)

        copy = tk.Button(self, text="copy", command=self.copy)
        copy.grid(row=100, column=0)
        delb = tk.Button(self, text="delete", command=self.delete)
        delb.grid(row=100, column=1)

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

class AugassignForm(Form):
    def __init__(self, parent, block):
        super().__init__(parent)
        self.isExpression = True
        self.isStatement = False
        self.parent = parent
        self.block = block
        tk.Message(self, width=350, font='Helvetica 16 bold', text="'augmented assignment'").grid()
        tk.Message(self, width=350, font='Helvetica 14', text="An 'augmented assignment' operation is of the form a <op>= b, and is equivalent to a = a <op> b.").grid(row=1)

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
        if v in kw.kwlist:
            tk.messagebox.showinfo("Name Error", "'{}' is a Python keyword".format(v))
        elif not v.isidentifier():
            tk.messagebox.showinfo("Format Error", "'{}' is not a valid variable name".format(v))
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
            tk.messagebox.showinfo("Format Error", "'{}' is not a valid number".format(self.entry.get()))

    def keyEnter(self, ev):
        self.cb()