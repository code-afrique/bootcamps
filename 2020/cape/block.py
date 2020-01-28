import tkinter as tk
import tkinter.messagebox
import io
from form import *
from node import *
import ast
import pmod

class Block(tk.Frame):
    def __init__(self, parent, shared, *args, borderwidth=0, **kwargs):
        super().__init__(parent, (* args), borderwidth=borderwidth, relief=tk.SUNKEN, **kwargs)
        self.parent = parent
        self.shared = shared
        self.isTop = False
        self.isWithinDef = (False if (parent == None) else parent.isWithinDef)
        self.isWithinLoop = (False if (parent == None) else parent.isWithinLoop)
        self.isWithinStore = (False if (parent == None) else parent.isWithinStore)    # lvalue

    def find(self, s):
        self.shared.search_string = (() if (s == '') else s)
        r = self.contains(self.shared.search_string)
        if ((self.shared.search_string != ()) and (not r)):
            tk.messagebox.showinfo('Find', "Did not locate any instances of '{}'".format(self.shared.search_string))

    # logical or of all arguments)
    def orl(self, *args):
        for a in args:
            if a:
                return True
        return False

    def markFound(self, r):
        return r

    def contains(self, s):
        return False

    # get the width and height of a multiline comment
    def bb(self, comment):
        width = height = 0
        f = io.StringIO(comment)
        for line in f:
            n = (len(line) - 1)
            if (n > width):
                width = n
            height += 1
        return (width, height)

    def scrollUpdate(self):
        self.shared.scrollUpdate()

    def setForm(self, f):
        self.shared.setForm(f)

    def genForm(self):
        print('no genForm {}'.format(self))

    def setBlock(self, b):
        self.shared.setBlock(b)

    def needsSaving(self):
        # This assertion helps find places where we accidentally invoke
        # needsSaving() when we don't need to
        assert (not self.shared.trap)
        self.shared.saved = False
        # save for undo purposes
        self.shared.save()

    def cut(self, doCopy):
        if doCopy:
            self.copy()
        if isinstance(self, StatementBlock):
            self.delStmt()
        elif isinstance(self.parent, StatementBlock):
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
        f = io.StringIO('')
        self.shared.exprBuffer.print(f, 0)
        code = f.getvalue()
        self.clipboard_append(code)

    def paste(self):
        tk.messagebox.showinfo('Paste Error', 'paste only allowed into uninitialized expression or rows')

    def undo(self):
        self.shared.undo()

    def delExpr(self):
        self.copyExpr()
        self.parent.delExpr()
        print('expression deleted')

    def commentize(self, s):
        r = ''
        for c in s.split('\n'):
            r += (('# ' + c) + '\n')
        return r[:-1]

    def uncommentize(self, s):
        r = ''
        for c in s.split('\n'):
            if ((len(c) > 0) and (c[0] == '#')):
                c = c[1:]
                if ((len(c) > 0) and (c[0] == ' ')):
                    c = c[1:]
            r += (c + '\n')
        return r[:-1]

    def newModuleBlock(self, parent, node):
        return ModuleBlock(parent, self.shared, node)

    def newPassBlock(self, parent, node):
        return PassBlock(parent, self.shared, node)

    def newDefBlock(self, parent, node):
        return DefBlock(parent, self.shared, node)

    def newLambdaBlock(self, parent, node):
        return LambdaBlock(parent, self.shared, node)

    def newClassBlock(self, parent, node):
        return ClassBlock(parent, self.shared, node)

    def newBasicClauseBlock(self, parent, node):
        return BasicClauseBlock(parent, self.shared, node)

    def newCondClauseBlock(self, parent, node):
        return CondClauseBlock(parent, self.shared, node)

    def newForClauseBlock(self, parent, node):
        return ForClauseBlock(parent, self.shared, node)

    def newExceptClauseBlock(self, parent, node):
        return ExceptClauseBlock(parent, self.shared, node)

    def newIfBlock(self, parent, node):
        return IfBlock(parent, self.shared, node)

    def newTryBlock(self, parent, node):
        return TryBlock(parent, self.shared, node)

    def newWithBlock(self, parent, node):
        return WithBlock(parent, self.shared, node)

    def newWhileBlock(self, parent, node):
        return WhileBlock(parent, self.shared, node)

    def newForBlock(self, parent, node):
        return ForBlock(parent, self.shared, node)

    def newReturnBlock(self, parent, node):
        return ReturnBlock(parent, self.shared, node)

    def newYieldBlock(self, parent, node):
        return YieldBlock(parent, self.shared, node)

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

    def newSetBlock(self, parent, node):
        return SetBlock(parent, self.shared, node)

    def newGenexpBlock(self, parent, node):
        return GenexpBlock(parent, self.shared, node)

    def newListcompBlock(self, parent, node):
        return ListcompBlock(parent, self.shared, node)

    def newSetcompBlock(self, parent, node):
        return SetcompBlock(parent, self.shared, node)

    def newDictcompBlock(self, parent, node):
        return DictcompBlock(parent, self.shared, node)

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

    def newStatementBlock(self, parent, what):
        return StatementBlock(parent, self.shared, what)

    def newExpressionBlock(self, parent, what):
        return ExpressionBlock(parent, self.shared, what)

    def newSeqBlock(self, parent, rows):
        return SeqBlock(parent, self.shared, rows)

class FrameBlock(Block):

    def __init__(self, parent, shared):
        super().__init__(parent, shared)

    def genForm(self):
        f = FrameForm(self.shared.confarea, self)
        self.setForm(f)

# A tree block is laid out as follows:
#  +-------+--------+
#  |  box  | header |
#  +-------+--------+
#  |       | frame  |
#  +-------+--------+
#
# The "box" is a button for minimizing compound statements
# The "header" contains a select button followed by type-specific stuff
# The "frame" is only for compound statements; contains a list of child blocks
#
# There are three kinds of boxes:
#    + box: for compound statements that are minimized
#    - box: for compound statements that are maximized
#    | box: for non-compound statements
#
# There are two kinds of selects:
#    selected/unselected
#
class TreeBlock(Block):
    def __init__(self, parent, shared):
        super().__init__(parent, shared)

        self.header = FrameBlock(self, shared)

        self.selected = False
        self.selectButton = tk.Label(self.header, image=shared.radiooff, fg='red', width=0)
        self.selectButton.bind("<Button-1>", self.selectcb)
        self.selectButton.bind("<Shift-Button-1>", self.shiftcb)
        self.selectButton.image = shared.radiooff
        self.selectButton.grid(row=0, column=0, sticky=tk.W)

        # the header is next to the "box"
        self.header.grid(row=0, column=1, sticky=tk.W)

    def boxcb(self):
        print("boxcb")

    def selectcb(self, ev):
        print("select", self, ev)
        if self.selected:
            self.selected = False
            self.selectButton.configure(image=self.shared.radiooff)
            self.selectButton.image = self.shared.radiooff
        else:
            self.selected = True
            self.selectButton.configure(image=self.shared.radioon)
            self.selectButton.image = self.shared.radioon

    def shiftcb(self, ev):
        print("shift cb", ev)

    def genForm(self):
        f = FrameForm(self.shared.confarea, self)
        self.setForm(f)

# A basic block does not have a body
class BasicBlock(TreeBlock):
    def __init__(self, parent, shared):
        super().__init__(parent, shared)

        self.boxImage = shared.leafbox
        self.boxButton = tk.Button(self, image=shared.leafbox, fg='red', width=0, command=self.boxcb)
        self.boxButton.image = self.boxImage
        self.boxButton.grid(row=0, column=0, sticky=tk.W)

    def contains(self, s):
        return self.markFound(False)

# A compound block has a body containing a list of child blocks
class CompoundBlock(TreeBlock):
    def __init__(self, parent, shared):
        super().__init__(parent, shared)
        self.body = []

        self.boxImage = shared.minusbox
        self.boxButton = tk.Button(self, image=shared.minusbox, fg='red', width=0, command=self.boxcb)
        self.boxButton.image = self.boxImage
        self.boxButton.grid(row=0, column=0, sticky=tk.W)

        self.decorator_list = []
        self.minimized = False

        self.frame = FrameBlock(self, shared)
        self.gridUpdate()

    def boxcb(self):
        self.minmax()

    def contains(self, s):
        r = False
        for c in self.body:
            if c.contains(s):
                r = True
        return self.markFound(r)

    def gridUpdate(self):
        for row in range(len(self.body)):
            self.body[row].row = row
            self.body[row].grid(row=row, column=0, sticky=tk.W)
        self.frame.grid(row=1, column=1, columnspan=2, sticky=tk.W)

    def minmax(self):
        if self.minimized:
            if (self.body == None):
                self.body = self.body_node.toBlock(self, self)
            self.frame.grid(row=(1 + len(self.decorator_list)), column=1, columnspan=2, sticky=tk.W)
            if (self.shared.search_string != None):
                self.body.contains(self.shared.search_string)
            self.update()
            self.minimized = False
            self.boxButton.configure(image=self.shared.minusbox)
            self.boxButton.image = self.shared.minusbox
        else:
            if self.body != None:
                self.frame.grid_forget()
            self.minimized = True
            self.boxButton.configure(image=self.shared.plusbox)
            self.boxButton.image = self.shared.plusbox
        self.scrollUpdate()

class PassBlock(BasicBlock):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.rowblk = parent
        assert isinstance(self.rowblk, StatementBlock)
        self.button = tk.Button(self.header, text='pass', fg='red', width=0, command=self.cb)
        self.button.grid(row=0, column=1, sticky=tk.W)

    def contains(self, s):
        r = (s == 'pass')
        return self.markFound(r)

    def genForm(self):
        f = PassForm(self.shared.confarea, self)
        self.setForm(f)

    def cb(self):
        self.setBlock(self)

    def paste(self):
        self.parent.paste()

    def stmtPut(self, n):
        assert(self.rowblk.what == self)
        self.rowblk.what.grid_forget()
        self.rowblk.what = n.toBlock(self.parent, self.parent)
        self.rowblk.what.grid()
        self.needsSaving()

    def stmtAugassign(self, op):
        if (op == '='):
            self.stmtPut(AssignNode([ExpressionNode(None)], ExpressionNode(None)))
            self.setBlock(self.rowblk.what.targets[0])
        else:
            self.stmtPut(AugassignNode(ExpressionNode(None), ExpressionNode(None), op))
            self.setBlock(self.rowblk.what.left)

    def stmtEval(self):
        self.stmtPut(EvalNode(ExpressionNode(None)))
        self.setBlock(self.rowblk.what.expr)

    def stmtIf(self):
        self.stmtPut(IfNode([CondClauseNode('if', None, None, False)], False))
        self.setBlock(self.rowblk.what.body[0].cond)

    def stmtWhile(self):
        self.stmtPut(WhileNode([CondClauseNode('while', None, None, False)], False))
        self.setBlock(self.rowblk.what.body[0].cond)

    def stmtFor(self):
        self.stmtPut(ForNode([ForClauseNode(ExpressionNode(None), ExpressionNode(None), None, False)], False))
        self.setBlock(self.rowblk.what.body[0].target)

    def stmtDef(self):
        self.stmtPut(DefNode('', [], [], None, None, None, False, []))
        self.setBlock(self.rowblk.what.body[0])
        self.shared.curForm.entry.focus()

    def stmtClass(self):
        self.stmtPut(ClassNode('', [], None, False, []))
        self.setBlock(self.rowblk.what.body[0])
        self.shared.curForm.entry.focus()

    def stmtWith(self):
        self.stmtPut(WithNode([(ExpressionNode(None), None)], None, False))
        self.setBlock(self.rowblk.what.body[0])

    def stmtReturn(self):
        self.stmtPut(ReturnNode(None))
        self.setBlock(self.rowblk.what)

    def stmtDel(self):
        self.stmtPut(DelNode([ExpressionNode(None)]))
        self.setBlock(self.rowblk.what.targets[0])
        self.needsSaving()

    def stmtCall(self):
        self.stmtPut(EvalNode(ExpressionNode(CallNode(ExpressionNode(None), [], []))))
        self.setBlock(self.rowblk.what.expr.what.func)

    # self.shared.curForm.entry.focus()
    def stmtPrint(self):
        self.stmtPut(EvalNode(ExpressionNode(CallNode(ExpressionNode(NameNode('print')), [ExpressionNode(None)], []))))
        self.setBlock(self.rowblk.what.expr.what.args[0])

    def stmtAssert(self):
        self.stmtPut(AssertNode(None, None))
        self.setBlock(self.rowblk.what.test)

    def stmtBreak(self):
        self.stmtPut(BreakNode())
        self.setBlock(self.rowblk.what)

    def stmtContinue(self):
        self.stmtPut(ContinueNode())
        self.setBlock(self.rowblk.what)

    def stmtGlobal(self):
        self.stmtPut(GlobalNode([ExpressionNode(None)]))
        self.setBlock(self.rowblk.what.vars[0])

    def stmtImport(self):
        self.stmtPut(ImportNode(ExpressionNode(None), None))
        self.setBlock(self.rowblk.what.module)

    def toNode(self):
        return PassNode()

class ModuleBlock(CompoundBlock):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        button = tk.Button(self.header, text='module', fg='red', width=0, command=self.cb)
        button.grid(row=0, column=1, sticky=tk.W)
        if (node == None):
            self.body = [StatementNode(PassNode()).toBlock(self.frame, self)]
        else:
            self.body = [c.toBlock(self.frame, self) for c in node.body]
        self.gridUpdate()

    def genForm(self):
        self.setForm(ModuleForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return ModuleNode([c.toNode() for c in self.body])

# Every statement in a sequence is wrapped by a StatementBlock
class StatementBlock(Block):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.row = None
        self.commentR = tk.StringVar()
        self.commentU = tk.StringVar()
        self.commentButton = tk.Frame(self)
        # tk.Button(self.commentButton, textvariable=self.commentU, fg='brown', command=self.listcmd, font='-slant italic', justify=tk.LEFT).grid()
        if (node == None):
            self.what = PassBlock(frame, self.shared, None)
        else:
            # if ((node.commentU != None) and (node.commentU != '')):
            #    self.setCommentU(node.commentU[:-1])
            self.what = node.what.toBlock(self, self)
            if ((node.commentR != None) and (node.commentR != '')):
                # self.commentR.set(("# " + node.commentR))
                self.commentR.set(self.commentize(node.commentR))
        self.what.grid(row=1, column=0, sticky=tk.W)
        # tk.Button(self, textvariable=self.commentR, fg='brown', command=self.listcmd, font='-slant italic').grid(row=1, column=1, sticky=(tk.N + tk.W))
        self.grid(row=0, column=0, sticky=tk.W)

    def markFound(self, r):
        print("StatementBlock markFound", r)
        return r

    def contains(self, s):
        r = self.what.contains(s)
        return self.markFound(r)

    def isCompound(self):
        return isinstance(self.what, CompoundBlock)

    def setComment(self, commentR, commentU):
        if (commentR == ''):
            self.commentR.set('')
        else:
            # self.commentR.set(("# " + commentR))
            self.commentR.set(self.commentize(commentR))
        self.setCommentU(commentU)
        self.needsSaving()

    def setCommentU(self, comment):
        comment = ('' if (comment == None) else comment)
        if (comment == ''):
            self.commentU.set('')
            self.commentButton.grid_forget()
        else:
            self.commentU.set(self.commentize(comment))
            self.commentButton.grid(row=0, columnspan=2, sticky=tk.W)

    def genForm(self):
        self.setForm(StatementForm(self.shared.confarea, self))

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
        self.parent.delStatement(self.row)
        print('statement deleted')
        self.needsSaving()

    def paste(self):
        code = self.clipboard_get()
        try:
            n = self.shared.parse(code, mode='single')
            assert isinstance(n, StatementNode)
            if (not isinstance(self.what, PassBlock)):
                tk.messagebox.showinfo('Paste Error', 'can only overwrite pass statements')
            else:
                self.what.grid_forget()
                self.what = n.what.toBlock(self.header, self)
                self.what.grid(row=1, column=0, sticky=tk.W)
                self.setBlock(self.what)
                self.needsSaving()
        except SyntaxError:
            tk.messagebox.showinfo('Paste Error', 'not a Python statement')
            print("invalid Python statement: '{}'".format(code))

    def listcmd(self):
        self.setBlock(self)

    def toNode(self):
        r = StatementNode(self.what.toNode(), 0)
        cu = self.uncommentize(self.commentU.get())
        r.commentU = (None if (cu == '') else (cu + '\n'))
        if self.shared.keeping:
            if isinstance(self.what, ClauseBlock):
                r.commentR = None
            else:
                r.index = self.shared.keep(self)
                r.commentR = '{}'.format(r.index)
        else:
            c = self.commentR.get()
            if (c != ''):
                assert (c[0:2] == '# ')
                # r.commentR = c[2:]
                r.commentR = self.uncommentize(c)
        return r

class AssignBlock(BasicBlock):
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
        column = 5
        for t in self.targets:
            t.grid(row=0, column=column)
            column += 1
            tk.Button(self, text='=', fg='purple', command=self.cb).grid(row=0, column=column)
            column += 1
        self.value.grid(row=0, column=column)

    def contains(self, s):
        r = self.value.contains(s)
        for t in self.targets:
            if t.contains(s):
                r = True
        return self.markFound(r)

    def goRight(self):
        return self.targets[0]

    def genForm(self):
        self.setForm(AssignForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return AssignNode([t.toNode() for t in self.targets], self.value.toNode())

class ExpressionBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared, borderwidth=1)
        self.button = tk.Button(self, text='?', width=0, command=self.cb)
        if ((node == None) or (node.what == None)):
            self.what = None
            self.button.grid()
        else:
            assert isinstance(node, ExpressionNode)
            self.what = node.what.toBlock(self, self)
            self.what.grid()

    def contains(self, s):
        r = ((self.what != None) and self.what.contains(s))
        return self.markFound(r)

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
        self.setValue(StringNode(''))
        self.shared.curForm.string.focus()

    def exprName(self, v):
        self.setValue(NameNode(v))
        self.shared.curForm.entry.focus()

    def exprSubscript(self, isSlice):
        self.setValue(SubscriptNode(None, (isSlice, (None if isSlice else ExpressionNode(None)), None, None)))
        self.setBlock(self.what.array)

    def exprAttr(self):
        self.setValue(AttrNode(ExpressionNode(None), NameNode('')))
        self.setBlock(self.what.array)

    def exprList(self):
        self.setValue(ListNode([]))

    def exprTuple(self):
        self.setValue(TupleNode([]))

    def exprSet(self):
        self.setValue(SetNode([ExpressionNode(None)]))

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

    def exprYield(self):
        self.setValue(YieldNode(None))

    def exprYieldExpr(self):
        self.setValue(YieldNode(ExpressionNode(None)))

    def gotKey(self, c):
        if isinstance(self.what, NameBlock):
            self.what.vname.set((self.what.vname.get() + c))
        elif c.isidentifier():
            self.exprName(c)
        elif (c == '.'):
            self.exprAttr()
        elif (c == ']'):
            self.exprSubscript()
        elif (c == '\x7f'):
            self.delExpr()
        elif (not self.isWithinStore):
            if isinstance(self.what, NumberBlock):
                self.what.value.set((self.what.value.get() + c))
            elif isinstance(self.what, StringBlock):
                self.what.string.set((self.what.string.get() + c))
            elif c.isdigit():
                self.exprNumber(c)
            elif ((c == '"') or (c == "'")):
                self.exprString()
            elif (c == '('):
                self.exprCall()
            elif (c == '['):
                self.exprList()
            elif (c == ','):
                self.exprTuple()
            elif (c == '='):
                self.exprBinaryop('==')
            elif (c == '!'):
                self.exprBinaryop('!=')
            elif (c in '+-*/%<>'):
                self.exprBinaryop(c)
            elif (c == '&'):
                self.exprBinaryop('and')
            elif (c == '|'):
                self.exprBinaryop('or')
            elif (c == '~'):
                self.exprUnaryop('not')
            else:
                print('key event {}'.format(c))
        else:
            print('limited expressions left of assignment operator'.format(c))

    def paste(self):
        try:
            code = self.clipboard_get()
            # tree = pparse.pparse(code, mode="eval")
            mod = ast.parse(code, mode='eval')
            tree = ast.dump(mod, include_attributes=True)
            n = pmod.nodeEval(tree)
            assert isinstance(n, ExpressionNode)
            self.setValue(n.what)
        except SyntaxError:
            tk.messagebox.showinfo('Paste Error', 'not a Python expression')
            print("invalid Python expression: '{}'".format(code))

    def toNode(self):
        if (self.what == None):
            if (not self.shared.cvtError):
                self.setBlock(self)
                tk.messagebox.showinfo('Convert Error', 'Fix uninitialized expression')
                self.shared.cvtError = True
            return ExpressionNode(None)
        return ExpressionNode(self.what.toNode())

class NameBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.vname = tk.StringVar()
        self.btn = tk.Button(self, textvariable=self.vname, fg='blue', width=0, command=self.cb)
        self.vname.set(node.what)
        self.btn.grid(row=0, column=0)

    def contains(self, s):
        r = (self.vname.get() == s)
        return self.markFound(r)

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
                tk.messagebox.showinfo('Convert Error', 'Fix bad variable name')
                self.shared.cvtError = True
        return NameNode(v)

class ListBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        tk.Button(self, text='[', width=0, command=self.cb).grid(row=0, column=0)
        self.eol = tk.Button(self, text=']', width=0, command=self.cb)
        self.entries = []
        if (node != None):
            for e in node.entries:
                self.addEntry(e)
        self.gridUpdate()

    def contains(self, s):
        r = False
        for e in self.entries:
            if e.contains(s):
                r = True
        return self.markFound(r)

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

    def gridUpdate(self):
        for i in range(len(self.entries)):
            if (i != 0):
                tk.Button(self, text=',', width=0, command=self.cb).grid(row=0, column=((2 * i) + 1))
            self.entries[i].grid(row=0, column=((2 * i) + 2))
        self.eol.grid(row=0, column=((2 * len(self.entries)) + 2))

    def toNode(self):
        return ListNode([entry.toNode() for entry in self.entries])

class CallBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        if (node == None):
            self.func = ExpressionBlock(self, shared, None)
        else:
            self.func = ExpressionBlock(self, shared, node.func)
        self.func.grid(row=0, column=0)
        tk.Button(self, text='(', width=0, command=self.cb).grid(row=0, column=1)
        self.eol = tk.Button(self, text=')', width=0, command=self.cb)
        self.args = []
        self.keywords = []
        if (node != None):
            for arg in node.args:
                self.addArg(arg)
            for kw in node.keywords:
                self.addKeyword(kw)
        self.gridUpdate()

    def contains(self, s):
        r = self.orl(self.func.contains(s), (s in self.args))
        for (k, v) in self.keywords:
            if ((k == s) or v.contains(s)):
                r = True
        return self.markFound(r)

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
        self.setBlock(self.args[-1])
        self.needsSaving()

    def addNamedArg(self, name):
        self.addKeyword((name, None))
        self.gridUpdate()
        (k, v) = self.keywords[-1]
        self.setBlock(v)
        self.needsSaving()

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
                tk.Button(self, text=',', width=0, command=self.cb).grid(row=0, column=column)
                column += 1
            arg.grid(row=0, column=column)
            column += 1
        for (k, v) in self.keywords:
            if first:
                first = False
            else:
                tk.Button(self, text=',', width=0, command=self.cb).grid(row=0, column=column)
                column += 1
            if (k == None):
                tk.Button(self, text='**', width=0, command=self.cb).grid(row=0, column=column)
                column += 1
            else:
                tk.Button(self, text=k, width=0, command=self.cb).grid(row=0, column=column)
                column += 1
                tk.Button(self, text='=', width=0, command=self.cb).grid(row=0, column=column)
                column += 1
            v.grid(row=0, column=column)
            column += 1
        self.eol.grid(row=0, column=column)

    def toNode(self):
        return CallNode(self.func.toNode(), [arg.toNode() for arg in self.args], [(k, v.toNode()) for (k, v) in self.keywords])

class StringBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.string = tk.StringVar()
        tk.Button(self, text='"', command=self.cb).grid(row=0, column=0)
        self.btn = tk.Button(self, textvariable=self.string, fg='green', width=0, command=self.cb, justify=tk.LEFT)
        self.string.set(node.what)
        self.btn.grid(row=0, column=1)
        tk.Button(self, text='"', command=self.cb).grid(row=0, column=2)

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

class WhileBlock(CompoundBlock):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        button = tk.Button(self.header, text='while', fg='red', width=0, command=self.cb)
        button.grid(row=0, column=1, sticky=tk.W)

        self.isWithinLoop = True
        if (node == None):
            self.body = [CondClauseBlock(self.frame, shared, CondClauseNode('while', None, None, False))]
            self.isWithinLoop = False
            self.hasElse = False
        else:
            self.body = [node.body[0].toBlock(self.frame, self)]
            self.isWithinLoop = False
            if node.hasElse:
                self.body.append(node.body[1].toBlock(self.frame, self))
            self.hasElse = node.hasElse
        self.gridUpdate()

    def genForm(self):
        self.setForm(WhileForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def addElse(self):
        if (not self.hasElse):
            clause = BasicClauseBlock(self, self.shared, BasicClauseNode('else', None, False))
            self.body.append(clause)
            self.gridUpdate()
            self.setBlock(clause.body.rows[0].what)
            self.hasElse = True
            self.needsSaving()

    def removeElse(self):
        if self.hasElse:
            self.body[-1].grid_forget()
            del self.body[-1]
            self.setBlock(self)
            self.hasElse = False
            self.needsSaving()

    def gridUpdate(self):
        super().gridUpdate()
        for i in range(len(self.body)):
            self.body[i].grid(row=i, sticky=tk.W)
        self.scrollUpdate()

    def toNode(self):
        print("CC ", self.body)
        return WhileNode([c.toNode() for c in self.body], self.hasElse)

# An 'cond' clause consists of a condition and a body.  It's used for 'if', 'elif', and 'while'
# body.
class CondClauseBlock(CompoundBlock):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        if (node.cond == None):
            node.cond = ExpressionNode(None)
        self.cond = node.cond.toBlock(self.header, self)
        self.cond.grid(row=0, column=1, sticky=tk.W)
        self.type = node.type

        if node == None:
            node = StatementNode(PassNode())
        self.body = [c.toBlock(self.frame, self) for c in node.body]

    def contains(self, s):
        r = self.orl((s == self.type), self.cond.contains(s), super().contains(s))
        return self.markFound(r)

    def genForm(self):
        self.setForm(CondClauseForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        assert len(self.body) > 0
        return CondClauseNode(self.type, self.cond.toNode(),
                [c.toNode() for c in self.body], self.minimized)

class ListopBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.values = [ExpressionBlock(self, shared, v) for v in node.values]
        self.ops = node.ops
        n = len(node.ops)
        for i in range(n):
            self.values[i].grid(row=0, column=(2 * i))
            op = tk.Button(self, text=node.ops[i], fg='purple', width=0, command=self.cb)
            op.grid(row=0, column=((2 * i) + 1))
        self.values[n].grid(row=0, column=(2 * n))

    def contains(self, s):
        r = False
        for v in self.values:
            if v.contains(s):
                r = True
        return self.markFound(r)

    def genForm(self):
        self.setForm(ListopForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return ListopNode([v.toNode() for v in self.values], self.ops)

class NumberBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.value = tk.StringVar()
        self.value.set(node.what)
        self.btn = tk.Button(self, textvariable=self.value, fg='blue', width=0, command=self.cb)
        self.btn.grid(row=0, column=0)

    def contains(self, s):
        r = (self.value.get() == s)
        return self.markFound(r)

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
                tk.messagebox.showinfo('Convert Error', 'Fix bad number')
                self.shared.cvtError = True
        return NumberNode(v)

class EvalBlock(BasicBlock):
    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        if (node == None):
            self.expr = ExpressionBlock(self.header, shared, None)
        else:
            self.expr = ExpressionBlock(self.header, shared, node.what)
        self.expr.grid(row=0, column=1, sticky=tk.W)

    def contains(self, s):
        r = self.expr.contains(s)
        return self.markFound(r)

    def genForm(self):
        self.setForm(EvalForm(self.shared.confarea, self))

    def goRight(self):
        return self.expr

    def toNode(self):
        return EvalNode(self.expr.toNode())

class BinaryopBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.left = ExpressionBlock(self, shared, node.left)
        self.middle = tk.Button(self, text=node.op, fg='purple', width=0, command=self.cb)
        self.right = ExpressionBlock(self, shared, node.right)
        self.op = node.op
        self.left.grid(row=0, column=0)
        self.middle.grid(row=0, column=1)
        self.right.grid(row=0, column=2)

    def contains(self, s):
        r = self.orl((self.op == s), self.left.contains(s), self.right.contains(s))
        return self.markFound(r)

    def genForm(self):
        self.setForm(BinaryopForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return BinaryopNode(self.left.toNode(), self.right.toNode(), self.op)

class AttrBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.isWithinStore = False
        if (node == None):
            self.array = ExpressionBlock(self, shared, None)
        else:
            self.array = node.array.toBlock(self, self)
        self.array.grid(row=0, column=0)
        tk.Button(self, text='.', command=self.cb).grid(row=0, column=1)
        if (node == None):
            self.ref = NameBlock(self, shared, NameNode(''))
        else:
            self.ref = node.ref.toBlock(self, self)
        self.ref.grid(row=0, column=2)

    def contains(self, s):
        r = self.orl(self.array.contains(s), self.ref.contains(s))
        return self.markFound(r)

    def cb(self):
        self.setBlock(self)

    def genForm(self):
        self.setForm(AttrForm(self.shared.confarea, self))

    def toNode(self):
        return AttrNode(self.array.toNode(), self.ref.toNode())

class DefBlock(CompoundBlock):

    def __init__(self, parent, shared, node):
        parent.isWithinDef = True
        super().__init__(parent, shared)
        self.mname = tk.StringVar()
        self.mname.set(node.name)
        self.args = node.args
        self.defaults = node.defaults
        self.vararg = node.vararg
        self.kwarg = node.kwarg
        self.decorator_list = node.decorator_list
        self.setHeader()

        if (node == None):
            self.body = [StatementNode(PassNode()).toBlock(self.frame, self)]
        else:
            self.body = [c.toBlock(self.frame, self) for c in node.body]
        self.gridUpdate()

    def contains(self, s):
        r = self.orl((s == 'def'), (self.mname.get() == s), (s in self.args), (self.vararg == s), (self.kwarg == s), super().contains(s))
        for d in self.defaults:
            if d.contains(s):
                r = True
        return self.markFound(r)

    def setHeader(self):
        btn = tk.Button(self.header, text='def', fg='red', width=0, command=self.cb)
        btn.grid(row=0, column=1)
        self.name = tk.Button(self.header, textvariable=self.mname, fg='blue', command=self.cb)
        self.name.grid(row=0, column=2)
        tk.Button(self.header, text='(', command=self.cb).grid(row=0, column=3)
        column = 4
        first = True
        nargs = len(self.args)
        ndefaults = len(self.defaults)
        delta = (nargs - ndefaults)
        for i in range(delta):
            if first:
                first = False
            else:
                tk.Button(self.header, text=',', command=self.cb).grid(row=0, column=column)
                column += 1
            tk.Button(self.header, text=self.args[i], fg='blue', command=self.cb).grid(row=0, column=column)
            column += 1
        if (self.vararg != None):
            if (not first):
                tk.Button(self.header, text=',', command=self.cb).grid(row=0, column=column)
                column += 1
            tk.Button(self.header, text=('*' + self.vararg), fg='blue', command=self.cb).grid(row=0, column=column)
            column += 1
        for i in range(delta, nargs):
            if first:
                first = False
            else:
                tk.Button(self.header, text=',', command=self.cb).grid(row=0, column=column)
                column += 1
            tk.Button(self.header, text=self.args[i], fg='blue', command=self.cb).grid(row=0, column=column)
            column += 1
            tk.Button(self.header, text='=', command=self.cb).grid(row=0, column=column)
            column += 1
            self.defaults[(i - delta)].toBlock(self.header, self).grid(row=0, column=column)
            column += 1
        if (self.kwarg != None):
            if (not first):
                tk.Button(self.header, text=',', command=self.cb).grid(row=0, column=column)
                column += 1
            tk.Button(self.header, text=('**' + self.kwarg), fg='blue', command=self.cb).grid(row=0, column=column)
            column += 1
        tk.Button(self.header, text=')', command=self.cb).grid(row=0, column=column)

    # TODO.  This function may be obsolete
    def addArg(self, name):
        self.args.insert(len(self.defaults), name)
        self.setHeader()

    def genForm(self):
        f = DefClauseForm(self.shared.confarea, self)
        self.setForm(f)

    def cb(self):
        self.setBlock(self)

    def incArg(self, name, type):
        if (type == 'normal'):
            pos = (len(self.args) - len(self.defaults))
            self.args.insert(pos, name)
        elif (type == 'keyword'):
            self.args.append(name)
            self.defaults.append(ExpressionNode(None))
        elif (type == '*vararg'):
            self.vararg = name
        else:
            assert (type == '**vararg')
            self.kwarg = name
        self.setHeader()
        self.needsSaving()

    def defUpdate(self, mname):
        self.mname.set(mname)
        self.setHeader()
        self.needsSaving()

    def toNode(self):
        v = self.mname.get()
        if (not v.isidentifier()):
            if (not self.shared.cvtError):
                self.setBlock(self)
                tk.messagebox.showinfo('Convert Error', 'Fix bad function name')
                self.shared.cvtError = True
        return DefNode(v, self.args, self.defaults, self.vararg, self.kwarg, [c.toNode() for c in self.body], self.minimized, self.decorator_list)

class SubscriptBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.isWithinStore = False
        self.array = ExpressionBlock(self, shared, node.array)
        self.array.grid(row=0, column=0)
        tk.Button(self, text='[', command=self.cb).grid(row=0, column=1)
        self.colon1 = tk.Button(self, text=':', command=self.cb)
        self.colon2 = tk.Button(self, text=':', command=self.cb)
        self.eol = tk.Button(self, text=']', command=self.cb)
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

    def contains(self, s):
        r = False
        if self.array.contains(s):
            r = True
        if ((self.lower != None) and self.lower.contains(s)):
            r = True
        if ((self.upper != None) and self.upper.contains(s)):
            r = True
        if ((self.step != None) and self.step.contains(s)):
            r = True
        return self.markFound(r)

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

class ForBlock(CompoundBlock):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        button = tk.Button(self.header, text='for', fg='red', width=0, command=self.cb)
        button.grid(row=0, column=1, sticky=tk.W)
        self.isWithinLoop = True
        if (node == None):
            self.body = [ForClauseBlock(self.frame, shared, ForClauseNode(None, None, None, False))]
            self.isWithinLoop = False
            self.hasElse = False
        else:
            self.body = [node.body[0].toBlock(self.frame, self)]
            self.isWithinLoop = False
            if node.hasElse:
                self.body.append(node.body[1].toBlock(self.frame, self))
            self.hasElse = node.hasElse
        self.gridUpdate()

    def genForm(self):
        self.setForm(ForForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def addElse(self):
        if (not self.hasElse):
            clause = BasicClauseBlock(self, self.shared, BasicClauseNode('else', None, False))
            self.body.append(clause)
            self.gridUpdate()
            self.setBlock(clause.body.rows[0].what)
            self.hasElse = True
            self.needsSaving()

    def removeElse(self):
        if self.hasElse:
            self.body[-1].grid_forget()
            del self.body[-1]
            self.setBlock(self)
            self.hasElse = False
            self.needsSaving()

    def gridUpdate(self):
        super().gridUpdate()
        for i in range(len(self.body)):
            self.body[i].grid(row=i, sticky=tk.W)
        self.scrollUpdate()

    def toNode(self):
        return ForNode([c.toNode() for c in self.body], self.hasElse)

class ForClauseBlock(CompoundBlock):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.header.isWithinStore = True
        if (node.target == None):
            self.target = ExpressionBlock(self.header, shared, None)
        else:
            self.target = node.target.toBlock(self.header, self)
        self.header.isWithinStore = False
        if (node.expr == None):
            self.expr = ExpressionBlock(self.header, shared, None)
        else:
            self.expr = ExpressionBlock(self.header, shared, node.expr)
        self.target.grid(row=0, column=1)
        tk.Button(self.header, text='in', fg='red', command=self.cb).grid(row=0, column=2)
        self.expr.grid(row=0, column=3)
        self.header.grid()

        if node == None:
            self.body = [StatementNode(PassNode()).toBlock(self.frame, self)]
        else:
            self.body = [c.toBlock(self.frame, self) for c in node.body]

    def contains(self, s):
        r = self.orl((s == 'for'), self.target.contains(s), self.expr.contains(s), super().contains(s))
        return self.markFound(r)

    def genForm(self):
        self.setForm(ForClauseForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return ForClauseNode(self.target.toNode(), self.expr.toNode(), [c.toNode() for c in self.body], self.minimized)

class ReturnBlock(BasicBlock):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        tk.Button(self.header, text='return', fg='red', command=self.cb).grid(row=0, column=1)
        if ((node == None) or (node.what == None)):
            self.expr = None
        else:
            self.expr = ExpressionBlock(self.header, shared, node.what)
            self.expr.grid(row=0, column=2)

    def contains(self, s):
        r = self.orl((s == 'return'), ((self.expr != None) and self.expr.contains(s)))
        return self.markFound(r)

    def genForm(self):
        self.setForm(ReturnForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def returnValue(self):
        self.expr = ExpressionBlock(self, self.shared, None)
        self.expr.grid(row=0, column=1)
        self.setBlock(self.expr)

    def toNode(self):
        return ReturnNode((None if (self.expr == None) else self.expr.toNode()))

class IfBlock(CompoundBlock):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        button = tk.Button(self.header, text='if', fg='red', width=0, command=self.cb)
        button.grid(row=0, column=1, sticky=tk.W)
        if (node == None):
            self.body = [CondClauseBlock(self.frame, shared, CondClauseNode('if', None, None, False))]
            self.hasElse = False
        else:
            self.body = [n.toBlock(self.frame, self) for n in node.body]
            self.hasElse = node.hasElse
        self.gridUpdate()

    def genForm(self):
        self.setForm(IfForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def insertElif(self):
        clause = CondClauseBlock(self.frame, self.shared, CondClauseNode('elif', None, None, False))
        n = len(self.body)
        self.body.insert(((n - 1) if self.hasElse else n), clause)
        self.gridUpdate()
        self.setBlock(clause.body.rows[0].what)
        self.needsSaving()

    def addElse(self):
        if (not self.hasElse):
            clause = BasicClauseBlock(self.frame, self.shared, BasicClauseNode('else', None, False))
            self.body.append(clause)
            self.gridUpdate()
            self.setBlock(clause.body.rows[0].what)
            self.hasElse = True
            self.needsSaving()

    def removeElse(self):
        if self.hasElse:
            self.frame[-1].grid_forget()
            del self.body[-1]
            self.setBlock(self)
            self.hasElse = False
            self.needsSaving()

    def gridUpdate(self):
        super().gridUpdate()
        for i in range(len(self.body)):
            self.body[i].grid(row=i, sticky=tk.W)
        self.scrollUpdate()

    def toNode(self):
        return IfNode([c.toNode() for c in self.body], self.hasElse)

class ConstantBlock(Block):

    def __init__(self, parent, shared, node):
        super().__init__(parent, shared)
        self.value = tk.StringVar()
        self.value.set(node.what)
        self.btn = tk.Button(self, textvariable=self.value, fg='purple', width=0, command=self.cb)
        self.btn.grid(row=0, column=0)

    def contains(self, s):
        r = (self.value.get() == s)
        return self.markFound(r)

    def genForm(self):
        self.setForm(ConstantForm(self.shared.confarea, self))

    def cb(self):
        self.setBlock(self)

    def toNode(self):
        return ConstantNode(self.value.get())
