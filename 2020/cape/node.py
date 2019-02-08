import io
import keyword

class Node():

    def toBlock(self, frame, block):
        print("toBlock not implemented by {}".format(self))
        return None

    def findLine(self, lineno):
        return None

    def printIndent(self, fd, level):
        for i in range(level):
            print("    ", end="", file=fd)

class PassNode(Node):

    def __init__(self):
        super().__init__()

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "pass"
        self.lineno = line

    def toBlock(self, frame, block):
        return block.newPassBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("pass", file=fd)

class RowNode(Node):

    def __init__(self, what, lineno=0):
        super().__init__()
        self.what = what
        self.lineno = lineno
        self.commentU = ""
        self.commentR = None
        self.index = 0
 
    def merge(self, q):
        self.what.merge(q)

    def toBlock(self, frame, block):
        return block.newRowBlock(frame, self)

    def findLine(self, lineno):
        return self.what.findLine(lineno)

    def print(self, fd, level):
        # first print the comments that are above this row
        f = io.StringIO(self.commentU)
        for line in f:
            self.printIndent(fd, level)
            print("# {}".format(line), end="", file=fd)

        if self.commentR == None:
            self.what.print(fd, level)
        else:
            # print into a string buffer
            f = io.StringIO("")
            self.what.print(f, level)
            s = f.getvalue()
            # insert the comment, if any, after the first line
            if "\n" in s:
                i = s.index("\n")
                s = ((s[:i] + "    # ") + self.commentR) + s[i:]
            print(s, file=fd, end="")

class ClauseNode(Node):
    def __init__(self, body):
        super().__init__()
        self.body = body
        self.commentU = ""
        self.commentR = None
        self.lineno = 0
        self.index = 0

    def findLine(self, lineno):
        assert isinstance(self.body, SeqNode)
        if not isinstance(self, BasicClauseNode) or self.type != "module":
            if (self.lineno >= lineno):
                return ("clause", self, self.lineno)
        return self.body.findLine(lineno)

    def printComment(self, fd, level):
        f = io.StringIO(self.commentU)
        for line in f:
            self.printIndent(fd, level)
            print("# {}".format(line), end="", file=fd)

    def printBody(self, fd, level):
        """
        self.commentR = "{}".format(self.index)
        """

        if self.commentR == None:
            print(":", file=fd)
        else:
            print(":\t# {}".format(self.commentR), file=fd)
        self.body.print(fd, level + 1)

class DefClauseNode(ClauseNode):
    def __init__(self, name, args, defaults, vararg, kwarg, body):
        super().__init__(body)
        self.name = name
        self.args = args
        self.defaults = defaults
        self.vararg = vararg
        self.kwarg = kwarg

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "def"
        self.lineno = line
        for d in self.defaults:
            d.merge(q)
        self.body.merge(q)

    def toBlock(self, frame, block):
        return block.newDefClauseBlock(frame, self)

    def print(self, fd, level):
        self.printComment(fd, level)
        self.printIndent(fd, level)
        print("def {}(".format(self.name), end="", file=fd)
        first = True
        nargs = len(self.args)
        ndefaults = len(self.defaults)
        delta = nargs - ndefaults
        for i in range(delta):
            if first:
                first = False
            else:
                print(", ", end="", file=fd)
            print(self.args[i], end="", file=fd)
        if self.vararg != None:
            if first:
                first = False
            else:
                print(", ", end="", file=fd)
            print("*{}".format(self.vararg), end="", file=fd)
        for i in range(delta, nargs):
            if first:
                first = False
            else:
                print(", ", end="", file=fd)
            print(self.args[i], end="", file=fd)
            print("=", end="", file=fd)
            self.defaults[i - delta].print(fd, 0)
        if self.kwarg != None:
            if not first:
                print(", ", end="", file=fd)
            print("**{}".format(self.kwarg), end="", file=fd)
        print(")", end="", file=fd)
        self.printBody(fd, level)

class LambdaNode(Node):

    def __init__(self, args, defaults, body):
        super().__init__()
        self.args = args
        self.defaults = defaults
        self.body = body

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "lambda"
        self.lineno = line
        for d in self.defaults:
            d.merge(q)
        self.body.merge(q)

    def toBlock(self, frame, block):
        return block.newLambdaBlock(frame, self)

    def print(self, fd, level):
        print("(lambda ", end="", file=fd)
        d = (len(self.args) - len(self.defaults))
        for i in range(len(self.args)):
            if (i != 0):
                print(", ", end="", file=fd)
            print(self.args[i], end="", file=fd)
            if (i >= d):
                print("=", end="", file=fd)
                self.defaults[(i - d)].print(fd, 0)
        print(": ", end="", file=fd)
        self.body.print(fd, 0)
        print(")", end="", file=fd)

class ClassClauseNode(ClauseNode):

    def __init__(self, name, bases, body):
        super().__init__(body)
        self.name = name
        self.bases = bases

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "class"
        self.lineno = line
        self.body.merge(q)

    def toBlock(self, frame, block):
        return block.newClassClauseBlock(frame, self)

    def print(self, fd, level):
        self.printComment(fd, level)
        self.printIndent(fd, level)
        print("class {}(".format(self.name), end="", file=fd)
        for i in range(len(self.bases)):
            if (i != 0):
                print(", ", end="", file=fd)
            self.bases[i].print(fd, 0)
        print(")", end="", file=fd)
        self.printBody(fd, level)

class BasicClauseNode(ClauseNode):
    def __init__(self, type, body):
        super().__init__(body)
        self.type = type

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == self.type
        self.lineno = line
        self.body.merge(q)

    def toBlock(self, frame, block):
        return block.newBasicClauseBlock(frame, self)

    def print(self, fd, level):
        if self.type == "module":
            self.body.print(fd, level)
        else:
            self.printComment(fd, level)
            self.printIndent(fd, level)
            print("{}".format(self.type), end="", file=fd)
            self.printBody(fd, level)

class CondClauseNode(ClauseNode):
    def __init__(self, type, cond, body):
        super().__init__(body)
        self.type = type
        self.cond = cond

    def toBlock(self, frame, block):
        return block.newCondClauseBlock(frame, self)

    def merge(self, q):
        (kw, line, col) = q.get()
        # print("cc", kw, self.type, line)
        assert kw == self.type
        self.lineno = line
        self.cond.merge(q)
        self.body.merge(q)

    def print(self, fd, level):
        self.printComment(fd, level)
        self.printIndent(fd, level)
        print("{} ".format(self.type), end="", file=fd)
        self.cond.print(fd, 0)
        self.printBody(fd, level)

class CompoundNode(Node):
    def __init__(self, clauses):
        super().__init__()
        self.clauses = clauses

    def merge(self, q):
        for c in self.clauses:
            c.merge(q)

    def findLine(self, lineno):
        for c in self.clauses:
            loc = c.findLine(lineno)
            if (loc != None):
                return loc
        return None

    def print(self, fd, level):
        for c in self.clauses:
            c.print(fd, level)

class ModuleNode(CompoundNode):

    def __init__(self, body):
        super().__init__([body])

    def toBlock(self, frame, block):
        return block.newModuleBlock(frame, self)

class ContainerNode(CompoundNode):

    def __init__(self, body):
        super().__init__([body])

    def toBlock(self, frame, block):
        return block.newContainerBlock(frame, self)

class IfNode(CompoundNode):

    def __init__(self, clauses, hasElse):
        super().__init__(clauses)
        self.hasElse = hasElse

    def toBlock(self, frame, block):
        return block.newIfBlock(frame, self)

class TryNode(CompoundNode):

    def __init__(self, clauses, hasElse):
        super().__init__(clauses)
        self.hasElse = hasElse

    def toBlock(self, frame, block):
        return block.newTryBlock(frame, self)

class ExceptClauseNode(ClauseNode):
    def __init__(self, type, name, body):
        super().__init__(body)
        self.type = type
        self.name = name

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "except"
        self.lineno = line
        if self.type != None and self.name != None:
            (kw2, line2, col2) = q.get()
            assert kw2 == "as"
        self.body.merge(q)

    def toBlock(self, frame, block):
        return block.newExceptClauseBlock(frame, self)

    def print(self, fd, level):
        self.printComment(fd, level)
        self.printIndent(fd, level)
        if (self.type == None):
            print("except", end="", file=fd)
        else:
            print("except ", end="", file=fd)
            self.type.print(fd, 0)
            if (self.name != None):
                print(" as ", end="", file=fd)
                self.name.print(fd, 0)
        self.printBody(fd, level)

class WithClauseNode(ClauseNode):

    def __init__(self, items, body):
        super().__init__(body)
        self.items = items

    def toBlock(self, frame, block):
        return block.newWithClauseBlock(frame, self)

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "with"
        self.lineno = line
        for (expr, var) in self.items:
            expr.merge(q)
            if var != None:
                (kw2, line2, col2) = q.get()
                assert kw2 == "as"
        self.body.merge(q)

    def print(self, fd, level):
        self.printComment(fd, level)
        self.printIndent(fd, level)
        print("with ", end="", file=fd)
        first = True
        for (expr, var) in self.items:
            if first:
                first = False
            else:
                print(", ", end="", file=fd)
            expr.print(fd, 0)
            if (var != None):
                print(" as ", end="", file=fd)
                var.print(fd, 0)
        self.printBody(fd, level)

class WhileNode(CompoundNode):

    def __init__(self, clauses, hasElse):
        super().__init__(clauses)
        self.hasElse = hasElse

    def toBlock(self, frame, block):
        return block.newWhileBlock(frame, self)

class ForNode(CompoundNode):

    def __init__(self, clauses, hasElse):
        super().__init__(clauses)
        self.hasElse = hasElse

    def toBlock(self, frame, block):
        return block.newForBlock(frame, self)

class ForClauseNode(ClauseNode):

    def __init__(self, target, expr, body):
        super().__init__(body)
        self.target = target
        self.expr = expr

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "for"
        self.lineno = line
        self.target.merge(q)
        (kw2, line2, col2) = q.get()
        assert kw2 == "in"
        self.expr.merge(q)
        self.body.merge(q)

    def toBlock(self, frame, block):
        return block.newForClauseBlock(frame, self)

    def print(self, fd, level):
        self.printComment(fd, level)
        self.printIndent(fd, level)
        print("for ", end="", file=fd)
        self.target.print(fd, 0)
        print(" in ", end="", file=fd)
        self.expr.print(fd, 0)
        self.printBody(fd, level)

class ReturnNode(Node):

    def __init__(self, what):
        super().__init__()
        self.what = what

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "return"
        self.lineno = line
        if self.what != None:
            self.what.merge(q)

    def toBlock(self, frame, block):
        return block.newReturnBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        if (self.what == None):
            print("return", file=fd)
        else:
            print("return ", end="", file=fd)
            self.what.print(fd, 0)
            print("", file=fd)

class AssertNode(Node):

    def __init__(self, test, msg):
        super().__init__()
        self.test = test
        self.msg = msg

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "assert"
        self.lineno = line
        self.test.merge(q)

    def toBlock(self, frame, block):
        return block.newAssertBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("assert ", end="", file=fd)
        self.test.print(fd, 0)
        if (self.msg != None):
            print(", ", end="", file=fd)
            self.msg.print(fd, 0)
        print("", file=fd)

class BreakNode(Node):

    def __init__(self):
        super().__init__()

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "break"
        self.lineno = line

    def toBlock(self, frame, block):
        return block.newBreakBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("break", file=fd)

class ContinueNode(Node):

    def __init__(self):
        super().__init__()

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "continue"
        self.lineno = line

    def toBlock(self, frame, block):
        return block.newContinueBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("continue", file=fd)

class ImportNode(Node):

    def __init__(self, name, asname):
        super().__init__()
        self.name = name
        self.asname = asname

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "import"
        self.lineno = line
        if self.asname != None:
            (kw2, line2, col2) = q.get()
            assert kw2 == "as"

    def toBlock(self, frame, block):
        return block.newImportBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("import ", end="", file=fd)
        self.name.print(fd, 0)
        if (self.asname != None):
            print(" as ", end="", file=fd)
            self.asname.print(fd, 0)
        print("", file=fd)

class ImportfromNode(Node):

    def __init__(self, module, names):
        super().__init__()
        self.module = module
        self.names = names

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "from"
        self.lineno = line
        (kw2, line2, col2) = q.get()
        assert kw2 == "import"

    def toBlock(self, frame, block):
        return block.newImportfromBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("from ", end="", file=fd)
        self.module.print(fd, 0)
        print(" import ", end="", file=fd)
        first = True
        for (name, asname) in self.names:
            if first:
                first = False
            else:
                print(", ", end="", file=fd)
            name.print(fd, 0)
            if (asname != None):
                print(" as ", end="", file=fd)
                asname.print(fd, 0)
        print("", file=fd)

class GlobalNode(Node):

    def __init__(self, names):
        super().__init__()
        self.names = names

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "global"
        self.lineno = line

    def toBlock(self, frame, block):
        return block.newGlobalBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("global ", end="", file=fd)
        for i in range(len(self.names)):
            if (i > 0):
                print(", ", end="", file=fd)
            self.names[i].print(fd, 0)
        print("", file=fd)

class DelNode(Node):

    def __init__(self, targets):
        super().__init__()
        self.targets = targets

    def merge(self, q):
        (kw, line, col) = q.get()
        assert kw == "del"
        self.lineno = line
        for t in self.targets:
            t.merge(q)

    def toBlock(self, frame, block):
        return block.newDelBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("del ", end="", file=fd)
        for i in range(len(self.targets)):
            if (i > 0):
                print(", ", end="", file=fd)
            self.targets[i].print(fd, 0)
        print("", file=fd)

class IfelseNode(Node):

    def __init__(self, cond, ifTrue, ifFalse):
        super().__init__()
        self.cond = cond
        self.ifTrue = ifTrue
        self.ifFalse = ifFalse

    def merge(self, q):
        self.ifTrue.merge(q)
        (kw, line, col) = q.get()
        assert kw == "if"
        self.cond.merge(q)
        (kw2, line2, col2) = q.get()
        assert kw2 == "else"
        self.ifFalse.merge(q)

    def toBlock(self, frame, block):
        return block.newIfelseBlock(frame, self)

    def print(self, fd, level):
        print("(", end="", file=fd)
        self.ifTrue.print(fd, 0)
        print(" if ", end="", file=fd)
        self.cond.print(fd, 0)
        print(" else ", end="", file=fd)
        self.ifFalse.print(fd, 0)
        print(")", end="", file=fd)

class AssignNode(Node):

    def __init__(self, targets, value):
        super().__init__()
        self.targets = targets
        self.value = value

    def merge(self, q):
        for t in self.targets:
            t.merge(q)
        self.value.merge(q)

    def toBlock(self, frame, block):
        return block.newAssignBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        for t in self.targets:
            t.print(fd, 0)
            print(" = ", end="", file=fd)
        self.value.print(fd, 0)
        print("", file=fd)

class AugassignNode(Node):

    def __init__(self, left, right, op):
        super().__init__()
        self.left = left
        self.right = right
        self.op = op

    def merge(self, q):
        self.left.merge(q)
        self.right.merge(q)

    def toBlock(self, frame, block):
        return block.newAugassignBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        self.left.print(fd, 0)
        print(" {} ".format(self.op), end="", file=fd)
        self.right.print(fd, 0)
        print("", file=fd)

class BinaryopNode(Node):

    def __init__(self, left, right, op):
        super().__init__()
        self.left = left
        self.right = right
        self.op = op

    def merge(self, q):
        self.left.merge(q)
        if keyword.iskeyword(self.op):
            (kw, line, col) = q.get()
            assert kw == self.op
            self.lineno = line
        self.right.merge(q)

    def toBlock(self, frame, block):
        return block.newBinaryopBlock(frame, self)

    def print(self, fd, level):
        print("(", end="", file=fd)
        self.left.print(fd, 0)
        print(" {} ".format(self.op), end="", file=fd)
        self.right.print(fd, 0)
        print(")", end="", file=fd)
# n values separated by n-1 operators

class ListopNode(Node):

    def __init__(self, values, ops):
        super().__init__()
        self.values = values
        self.ops = ops

    def merge(self, q):
        i = 0
        n = len(self.ops)
        for i in range(n):
            self.values[i].merge(q)
            if keyword.iskeyword(self.ops[i]):
                (kw, line, col) = q.get()
                assert kw == self.ops[i]
        self.values[n].merge(q)

    def toBlock(self, frame, block):
        return block.newListopBlock(frame, self)

    def print(self, fd, level):
        print("(", end="", file=fd)
        i = 0
        n = len(self.ops)
        for i in range(n):
            self.values[i].print(fd, 0)
            print(" {} ".format(self.ops[i]), end="", file=fd)
        self.values[n].print(fd, 0)
        print(")", end="", file=fd)

class UnaryopNode(Node):

    def __init__(self, right, op):
        super().__init__()
        self.right = right
        self.op = op

    def merge(self, q):
        if keyword.iskeyword(self.op):
            (kw, line, col) = q.get()
            assert kw == self.op
            self.lineno = line
        self.right.merge(q)

    def toBlock(self, frame, block):
        return block.newUnaryopBlock(frame, self)

    def print(self, fd, level):
        print("({} ".format(self.op), end="", file=fd)
        self.right.print(fd, 0)
        print(")", end="", file=fd)

class SubscriptNode(Node):

    def __init__(self, array, slice):
        super().__init__()
        self.array = array
        self.slice = slice

    def merge(self, q):
        self.array.merge(q)
        (isSlice, lower, upper, step) = self.slice
        if lower != None:
            lower.merge(q)
        if upper != None:
            upper.merge(q)
        if step != None:
            step.merge(q)

    def toBlock(self, frame, block):
        return block.newSubscriptBlock(frame, self)

    def print(self, fd, level):
        self.array.print(fd, 0)
        (isSlice, lower, upper, step) = self.slice
        print("[", end="", file=fd)
        if (lower != None):
            lower.print(fd, 0)
        if isSlice:
            print(":", end="", file=fd)
            if (upper != None):
                upper.print(fd, 0)
            if (step != None):
                print(":", end="", file=fd)
                step.print(fd, 0)
        print("]", end="", file=fd)

class CallNode(Node):

    def __init__(self, func, args, keywords):
        super().__init__()
        self.func = func
        self.args = args
        self.keywords = keywords

    def merge(self, q):
        self.func.merge(q)
        for arg in self.args:
            arg.merge(q)
        for (arg, val) in self.keywords:
            val.merge(q)

    def toBlock(self, frame, block):
        return block.newCallBlock(frame, self)

    def print(self, fd, level):
        self.func.print(fd, 0)
        print("(", end="", file=fd)
        first = True
        for arg in self.args:
            if first:
                first = False
            else:
                print(", ", end="", file=fd)
            arg.print(fd, 0)
        for (arg, val) in self.keywords:
            if first:
                first = False
            else:
                print(", ", end="", file=fd)
            if arg == None:
                print("**", end="", file=fd)
            else:
                print("{}=".format(arg), end="", file=fd)
            val.print(fd, 0)
        print(")", end="", file=fd)

class ListNode(Node):

    def __init__(self, entries):
        super().__init__()
        self.entries = entries

    def merge(self, q):
        for e in self.entries:
            e.merge(q)

    def toBlock(self, frame, block):
        return block.newListBlock(frame, self)

    def print(self, fd, level):
        print("[", end="", file=fd)
        for i in range(len(self.entries)):
            if (i != 0):
                print(", ", end="", file=fd)
            self.entries[i].print(fd, 0)
        print("]", end="", file=fd)

class ListcompNode(Node):

    def __init__(self, elt, generators):
        super().__init__()
        self.elt = elt
        self.generators = generators

    def merge(self, q):
        self.elt.merge(q)
        for (target, iter, ifs, is_async) in self.generators:
            (kw, line, col) = q.get()
            assert kw == "for"
            target.merge(q)
            (kw2, line2, col2) = q.get()
            assert kw2 == "in"
            iter.merge(q)
            for i in ifs:
                (kw3, line3, col3) = q.get()
                assert kw2 == "if"
                i.merge(q)

    def toBlock(self, frame, block):
        return block.newListcompBlock(frame, self)

    def print(self, fd, level):
        print("[", end="", file=fd)
        self.elt.print(fd, 0)
        for (target, iter, ifs, is_async) in self.generators:
            print(" for ", end="", file=fd)
            target.print(fd, 0)
            print(" in ", end="", file=fd)
            iter.print(fd, 0)
            for i in ifs:
                print(" if ", end="", file=fd)
                i.print(fd, 0)
        print("]", end="", file=fd)

class DictNode(Node):

    def __init__(self, keys, values):
        super().__init__()
        self.keys = keys
        self.values = values

    def merge(self, q):
        for i in range(len(self.keys)):
            self.keys[i].merge(q)
            self.values[i].merge(q)

    def toBlock(self, frame, block):
        return block.newDictBlock(frame, self)

    def print(self, fd, level):
        print("{", end="", file=fd)
        for i in range(len(self.keys)):
            if (i != 0):
                print(", ", end="", file=fd)
            self.keys[i].print(fd, 0)
            print(": ", end="", file=fd)
            self.values[i].print(fd, 0)
        print("}", end="", file=fd)

class TupleNode(Node):

    def __init__(self, entries):
        super().__init__()
        self.entries = entries

    def merge(self, q):
        for e in self.entries:
            e.merge(q)

    def toBlock(self, frame, block):
        return block.newTupleBlock(frame, self)

    def print(self, fd, level):
        print("(", end="", file=fd)
        n = len(self.entries)
        for i in range(n):
            if (i != 0):
                print(", ", end="", file=fd)
            self.entries[i].print(fd, 0)
        if (n == 1):
            print(",", end="", file=fd)
        print(")", end="", file=fd)

class AttrNode(Node):

    def __init__(self, array, ref):
        super().__init__()
        self.array = array
        self.ref = ref

    def merge(self, q):
        self.array.merge(q)
        self.ref.merge(q)

    def toBlock(self, frame, block):
        return block.newAttrBlock(frame, self)

    def print(self, fd, level):
        self.array.print(fd, 0)
        print(".", end="", file=fd)
        self.ref.print(fd, 0)

class EvalNode(Node):

    def __init__(self, what):
        super().__init__()
        self.what = what

    def merge(self, q):
        self.what.merge(q)

    def toBlock(self, frame, block):
        return block.newEvalBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        self.what.print(fd, 0)
        print("", file=fd)

class NumberNode(Node):

    def __init__(self, what):
        super().__init__()
        self.what = what

    def merge(self, q):
        pass

    def toBlock(self, frame, block):
        return block.newNumberBlock(frame, self)

    def print(self, fd, level):
        print(self.what, end="", file=fd)

class ConstantNode(Node):

    def __init__(self, what):
        super().__init__()
        self.what = what

    def merge(self, q):
        (kw, line, col) = q.get()
        # print("const", kw, self.what, line)
        assert kw == self.what
        self.lineno = line

    def toBlock(self, frame, block):
        return block.newConstantBlock(frame, self)

    def print(self, fd, level):
        print(self.what, end="", file=fd)

class NameNode(Node):

    def __init__(self, what):
        super().__init__()
        self.what = what

    def merge(self, q):
        pass

    def toBlock(self, frame, block):
        return block.newNameBlock(frame, self)

    def print(self, fd, level):
        print(self.what, end="", file=fd)

class StringNode(Node):

    def __init__(self, what):
        super().__init__()
        self.what = what

    def merge(self, q):
        pass

    def toBlock(self, frame, block):
        return block.newStringBlock(frame, self)

    # like repr, but uses triple quotes when possible
    def mrepr(self, s):
        if s.count("\n") == 0:
            return repr(s)
        fd = io.StringIO(s)
        lines = s.split("\n")
        print('"""', end="", file=fd)
        for line in lines[:-1]:
            print(repr(line)[1:-1], file=fd)
        print(repr(lines[-1])[1:-1], end="", file=fd)
        print('"""', end="", file=fd)
        return fd.getvalue()

    def print(self, fd, level):
        print(self.mrepr(self.what), end="", file=fd)

class BytesNode(Node):

    def __init__(self, what):
        super().__init__()
        self.what = what

    def merge(self, q):
        pass

    def toBlock(self, frame, block):
        return block.newBytesBlock(frame, self)

    def print(self, fd, level):
        print(self.what, end="", file=fd)

class ExpressionNode(Node):

    def __init__(self, what):
        super().__init__()
        self.what = what

    def merge(self, q):
        self.what.merge(q)

    def toBlock(self, frame, block):
        return block.newExpressionBlock(frame, self)

    def print(self, fd, level):
        self.what.print(fd, 0)

class SeqNode(Node):
    def __init__(self, rows):
        super().__init__()
        self.rows = rows

    def merge(self, q):
        for r in self.rows:
            r.merge(q)

    def toBlock(self, frame, block):
        return block.newSeqBlock(frame, self)

    def findLine(self, lineno):
        for i in range(len(self.rows)):
            assert isinstance(self.rows[i], RowNode)
            if not isinstance(self.rows[i].what, CompoundNode) and self.rows[i].lineno >= lineno:
                return ("row", self, i)
            r = self.rows[i].findLine(lineno)
            if (r != None):
                return r
        return None

    def print(self, fd, level):
        for r in self.rows:
            r.print(fd, level)
