import io

class Node():
    def toBlock(self, frame):
        return None

    def findRow(self, lineno):
        return None

    def printIndent(self, fd, level):
        for i in range(level):
            print("    ", end="", file=fd)

class PassNode(Node):
    def __init__(self):
        super().__init__()

    def toBlock(self, frame, block):
        return block.newPassBlock(frame, self, block)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("pass", file=fd)

class EmptyNode(Node):
    def __init__(self):
        super().__init__()

    def toBlock(self, frame, block):
        return block.newEmptyBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("", file=fd)

class RowNode(Node):
    def __init__(self, what, lineno):
        super().__init__()
        self.what = what
        self.lineno = lineno
        self.comment = None

    def findRow(self, lineno):
        return self.what.findRow(lineno)

    def print(self, fd, level):
        # first print into a string buffer
        f = io.StringIO("")
        self.what.print(f, level)
        s = f.getvalue()

        # insert the comment, if any, after the first line
        if '\n' in s and self.comment != None:
            i = s.index('\n')
            s = s[:i] + ('' if isinstance(self.what, EmptyNode) else '\t') + self.comment + s[i:]

        print(s, file=fd, end="")

class DefNode(Node):
    def __init__(self, name, args, body, minimized):
        super().__init__()
        self.name = name
        self.args = args
        self.body = body
        self.minimized = minimized

    def toBlock(self, frame, block):
        return block.newDefBlock(frame, self)

    def findRow(self, lineno):
        return self.body.findRow(lineno)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("def {}(".format(self.name), end="", file=fd)
        for i in range(len(self.args)):
            if i != 0:
                print(", ", end="", file=fd)
            print(self.args[i], end="", file=fd)
        print("):", file=fd)
        self.body.print(fd, level + 1)

class ClassNode(Node):
    def __init__(self, name, bases, body, minimized):
        super().__init__()
        self.name = name
        self.bases = bases
        self.body = body
        self.minimized = minimized

    def toBlock(self, frame, block):
        return block.newClassBlock(frame, self)

    def findRow(self, lineno):
        return self.body.findRow(lineno)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("class {}(".format(self.name), end="", file=fd)
        for i in range(len(self.bases)):
            if i != 0:
                print(", ", end="", file=fd)
            self.bases[i].print(fd, 0)
        print("):", file=fd)
        self.body.print(fd, level + 1)

class IfNode(Node):
    def __init__(self, conds, bodies, minimizeds):
        super().__init__()
        self.conds = conds
        self.bodies = bodies
        self.minimizeds = minimizeds

    def toBlock(self, frame, block):
        return block.newIfBlock(frame, self)

    def findRow(self, lineno):
        for b in self.bodies:
            loc = b.findRow(lineno)
            if loc != None:
                return loc
        return None

    def print(self, fd, level):
        for i in range(len(self.bodies)):
            self.printIndent(fd, level)
            if i == 0:
                print("if ", end="", file=fd)
                self.conds[i].print(fd, 0)
                print(":", file=fd)
            elif i < len(self.conds):
                print("elif ", end="", file=fd)
                self.conds[i].print(fd, 0)
                print(":", file=fd)
            else:
                print("else:", file=fd)
            self.bodies[i].print(fd, level + 1)

class TryNode(Node):
    def __init__(self, body, handlers, orelse, finalbody):
        super().__init__()
        self.body = body
        self.handlers = handlers
        self.orelse = orelse
        self.finalbody = finalbody

    def toBlock(self, frame, block):
        return block.newTryBlock(frame, self)

    def findRow(self, lineno):
        loc = self.body.findRow(lineno)
        if loc != None:
            return loc
        for type, name, body in self.handers:
            loc = body.findRow(lineno)
            if loc != None:
                return loc
        loc = self.orelse.findRow(lineno)
        if loc != None:
            return loc
        loc = self.finalbody.findRow(lineno)
        if loc != None:
            return loc
        return None

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("try:", file=fd)
        self.body.print(fd, level + 1)
        for type, name, body in self.handlers:
            self.printIndent(fd, level)
            if type == None:
                print("except:", file=fd)
            else:
                print("except ", end="", file=fd)
                type.print(fd, 0)
                if name != None:
                    print(" as ", end="", file=fd)
                    name.print(fd, 0)
                print(":", file=fd)
            body.print(fd, level + 1)
        if self.orelse != None:
            print("else:", file=fd)
            self.orelse.print(fd, level + 1)
        if self.finalbody != None:
            print("finally:", file=fd)
            self.finalbody.print(fd, level + 1)

class WhileNode(Node):
    def __init__(self, cond, body, orelse, minimized, minimized2):
        super().__init__()
        self.cond = cond
        self.body = body
        self.orelse = orelse
        self.minimized = minimized
        self.minimized2 = minimized2

    def toBlock(self, frame, block):
        return block.newWhileBlock(frame, self)

    def findRow(self, lineno):
        loc = self.body.findRow(lineno)
        if loc == None and self.orelse != None:
            loc = self.orelse.findRow(lineno)
        return loc

    def print(self, fd, level):
        print("WHILE {}".format(level))
        self.printIndent(fd, level)
        print("while ", end="", file=fd)
        self.cond.print(fd, 0)
        print(":", file=fd)
        self.body.print(fd, level + 1)
        if self.orelse != None:
            self.printIndent(fd, level)
            print("else:", file=fd)
            self.orelse.print(fd, level + 1)

class ForNode(Node):
    def __init__(self, var, expr, body, orelse, minimized, minimized2):
        super().__init__()
        self.var = var
        self.expr = expr
        self.body = body
        self.orelse = orelse
        self.minimized = minimized
        self.minimized2 = minimized2

    def toBlock(self, frame, block):
        return block.newForBlock(frame, self)

    def findRow(self, lineno):
        loc = self.body.findRow(lineno)
        if loc == None and self.orelse != None:
            loc = self.orelse.findRow(lineno)
        return loc

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("for ", end="", file=fd)
        self.var.print(fd, 0)
        print(" in ", end="", file=fd)
        self.expr.print(fd, 0)
        print(":", file=fd)
        self.body.print(fd, level + 1)
        if self.orelse != None:
            self.printIndent(fd, level)
            print("else:", file=fd)
            self.orelse.print(fd, level + 1)

class ReturnNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, block):
        return block.newReturnBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("return ", end="", file=fd)
        self.what.print(fd, 0)
        print("", file=fd)

class AssertNode(Node):
    def __init__(self, test, msg):
        super().__init__()
        self.test = test
        self.msg = msg

    def toBlock(self, frame, block):
        return block.newAssertBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("assert ", end="", file=fd)
        self.test.print(fd, 0)
        if self.msg != None:
            print(", ", end="", file=fd)
            self.msg.print(fd, 0)
        print("", file=fd)

class BreakNode(Node):
    def __init__(self):
        super().__init__()

    def toBlock(self, frame, block):
        return block.newBreakBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("break", file=fd)

class ContinueNode(Node):
    def __init__(self):
        super().__init__()

    def toBlock(self, frame, block):
        return block.newContinueBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("continue", file=fd)

class ImportNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, block):
        return block.newImportBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("import ", end="", file=fd)
        self.what.print(fd, 0)
        print("", file=fd)

class GlobalNode(Node):
    def __init__(self, names):
        super().__init__()
        self.names = names

    def toBlock(self, frame, block):
        return block.newGlobalBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("global ", end="", file=fd)
        for i in range(len(self.names)):
            if i > 0:
                print(", ", end="", file=fd)
            self.names[i].print(fd, 0)
        print("", file=fd)

class DelNode(Node):
    def __init__(self, targets):
        super().__init__()
        self.targets = targets

    def toBlock(self, frame, block):
        return block.newDelBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("del ", end="", file=fd)
        for i in range(len(self.targets)):
            if i > 0:
                print(", ", end="", file=fd)
            self.targets[i].print(fd, 0)
        print("", file=fd)

class IfelseNode(Node):
    def __init__(self, cond, ifTrue, ifFalse):
        super().__init__()
        self.cond = cond
        self.ifTrue = ifTrue
        self.ifFalse = ifFalse

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

    def toBlock(self, frame, block):
        return block.newBinaryopBlock(frame, self)

    def print(self, fd, level):
        print("(", end="", file=fd)
        self.left.print(fd, 0)
        print(" {} ".format(self.op), end="", file=fd)
        self.right.print(fd, 0)
        print(")", end="", file=fd)

class UnaryopNode(Node):
    def __init__(self, right, op):
        super().__init__()
        self.right = right
        self.op = op

    def toBlock(self, frame, block):
        return block.newUnaryopBlock(frame, self)

    def print(self, fd, level):
        print(self.op, end="", file=fd)
        print("(", end="", file=fd)
        self.right.print(fd, 0)
        print(")", end="", file=fd)

class SubscriptNode(Node):
    def __init__(self, array, slice):
        super().__init__()
        self.array = array
        self.slice = slice

    def toBlock(self, frame, block):
        return block.newSubscriptBlock(frame, self)

    def print(self, fd, level):
        self.array.print(fd, 0)
        isSlice, lower, upper, step = self.slice
        print("[", end="", file=fd)
        if lower != None:
            lower.print(fd, 0)
        if isSlice:
            print(":", end="", file=fd)
            if upper != None:
                upper.print(fd, 0)
            if step != None:
                print(":", end="", file=fd)
                step.print(fd, 0)
        print("]", end="", file=fd)

class CallNode(Node):
    def __init__(self, func, args, keywords):
        super().__init__()
        self.func = func
        self.args = args
        self.keywords = keywords

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
            print("{}=".format(arg), end="", file=fd)
            val.print(fd, 0)
        print(")", end="", file=fd)

class ListNode(Node):
    def __init__(self, entries):
        super().__init__()
        self.entries = entries

    def toBlock(self, frame, block):
        return block.newListBlock(frame, self)

    def print(self, fd, level):
        print("[", end="", file=fd)
        for i in range(len(self.entries)):
            if i != 0:
                print(", ", end="", file=fd)
            self.entries[i].print(fd, 0)
        print("]", end="", file=fd)

class DictNode(Node):
    def __init__(self, keys, values):
        super().__init__()
        self.keys = keys
        self.values = values

    def toBlock(self, frame, block):
        return block.newDictBlock(frame, self)

    def print(self, fd, level):
        print("{", end="", file=fd)
        for i in range(len(self.keys)):
            if i != 0:
                print(", ", end="", file=fd)
            self.keys[i].print(fd, 0)
            print(": ", end="", file=fd)
            self.values[i].print(fd, 0)
        print("}", end="", file=fd)

class TupleNode(Node):
    def __init__(self, entries):
        super().__init__()
        self.entries = entries

    def toBlock(self, frame, block):
        return block.newTupleBlock(frame, self)

    def print(self, fd, level):
        print("(", end="", file=fd)
        n = len(self.entries)
        for i in range(n):
            if i != 0:
                print(", ", end="", file=fd)
            self.entries[i].print(fd, 0)
        if n == 1:
            print(",", end="", file=fd)
        print(")", end="", file=fd)

class AttrNode(Node):
    def __init__(self, array, ref):
        super().__init__()
        self.array = array
        self.ref = ref

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

    def toBlock(self, frame, block):
        return block.newNumberBlock(frame, self)

    def print(self, fd, level):
        print(self.what, end="", file=fd)

class ConstantNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, block):
        return block.newConstantBlock(frame, self)

    def print(self, fd, level):
        print(self.what, end="", file=fd)

class NameNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, block):
        return block.newNameBlock(frame, self)

    def print(self, fd, level):
        print(self.what, end="", file=fd)

class StringNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, block):
        return block.newStringBlock(frame, self)

    def print(self, fd, level):
        print('"', end="", file=fd)
        for c in self.what:
            if c == '\\':
                print('\\\\', end="", file=fd)
            elif c == '"':
                print('\\"', end="", file=fd)
            elif c == '\n':
                print('\\n', end="", file=fd)
            else:
                print(c, end="", file=fd)
        print('"', end="", file=fd)

class ExpressionNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, block):
        return block.newExpressionBlock(frame, self.what)

    def print(self, fd, level):
        # if self.init:
            self.what.print(fd, 0)
        # else:
        #   print("?", end="", file=fd)

class SeqNode(Node):
    def __init__(self, rows):
        super().__init__()
        self.rows = rows

    def toBlock(self, frame, block):
        return block.newSeqBlock(frame, self)

    def findRow(self, lineno):
        for i in range(len(self.rows)):
            if self.rows[i].lineno >= lineno:
                return (self, i)
            r = self.rows[i].findRow(lineno)
            if r != None:
                return r
        return None

    def print(self, fd, level):
        for r in self.rows:
            r.print(fd, level)
