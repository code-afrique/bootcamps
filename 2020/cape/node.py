import io

class Node():

    def toBlock(self, frame, block):
        print("toBlock not implemented by {}".format(self))
        return None

    def findRow(self, lineno):
        return None

    def printIndent(self, fd, level):
        for i in range(level):
            print("    ", end="", file=fd)

class ModuleNode():

    def __init__(self, body):
        super().__init__()
        self.body = body

    def findRow(self, lineno):
        return self.body.findRow(lineno)

    def toBlock(self, frame, block):
        return block.newModuleBlock(frame, self)

    def print(self, fd, level):
        self.body.print(fd, level)

class PassNode(Node):

    def __init__(self):
        super().__init__()

    def toBlock(self, frame, block):
        return block.newPassBlock(frame, self)

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

    def __init__(self, what, lineno=0):
        super().__init__()
        self.what = what
        self.lineno = lineno
        self.comment = None

    def toBlock(self, frame, block):
        return block.newRowBlock(frame, self)

    def findRow(self, lineno):
        return self.what.findRow(lineno)

    def print(self, fd, level):
        # first print into a string buffer
        f = io.StringIO("")
        self.what.print(f, level)
        s = f.getvalue()
        # insert the comment, if any, after the first line
        if (("\n" in s) and (self.comment != None)):
            i = s.index("\n")
            s = (((s[:i] + ("#" if isinstance(self.what, EmptyNode) else "    #")) + self.comment) + s[i:])
        print(s, file=fd, end="")

class ClauseNode(Node):
    def __init__(self, body):
        super().__init__()
        self.body = body

    def findRow(self, lineno):
        return self.body.findRow(lineno)

class DefClauseNode(ClauseNode):
    def __init__(self, name, args, defaults, body):
        super().__init__(body)
        self.name = name
        self.args = args
        self.defaults = defaults

    def toBlock(self, frame, block):
        return block.newDefClauseBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("def {}(".format(self.name), end="", file=fd)
        d = (len(self.args) - len(self.defaults))
        for i in range(len(self.args)):
            if (i != 0):
                print(", ", end="", file=fd)
            print(self.args[i], end="", file=fd)
            if (i >= d):
                print("=", end="", file=fd)
                self.defaults[(i - d)].print(fd, 0)
        print("):", file=fd)
        self.body.print(fd, (level + 1))

class LambdaNode(Node):

    def __init__(self, args, defaults, body):
        super().__init__()
        self.args = args
        self.defaults = defaults
        self.body = body

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

    def toBlock(self, frame, block):
        return block.newClassClauseBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("class {}(".format(self.name), end="", file=fd)
        for i in range(len(self.bases)):
            if (i != 0):
                print(", ", end="", file=fd)
            self.bases[i].print(fd, 0)
        print("):", file=fd)
        self.body.print(fd, (level + 1))

class BasicClauseNode(ClauseNode):
    def __init__(self, type, body):
        super().__init__(body)
        self.type = type

    def toBlock(self, frame, block):
        return block.newBasicClauseBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("{}:".format(self.type), file=fd)
        self.body.print(fd, (level + 1))

class CondClauseNode(ClauseNode):
    def __init__(self, type, cond, body):
        super().__init__(body)
        self.type = type
        self.cond = cond

    def toBlock(self, frame, block):
        return block.newCondClauseBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("{} ".format(self.type), end="", file=fd)
        self.cond.print(fd, 0)
        print(":", file=fd)
        self.body.print(fd, (level + 1))

class CompoundNode(Node):
    def __init__(self, clauses):
        super().__init__()
        self.clauses = clauses

    def findRow(self, lineno):
        for c in self.clauses:
            loc = c.findRow(lineno)
            if (loc != None):
                return loc
        return None

    def print(self, fd, level):
        for c in self.clauses:
            c.print(fd, level)

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

    def toBlock(self, frame, block):
        return block.newExceptClauseBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        if (self.type == None):
            print("except:", file=fd)
        else:
            print("except ", end="", file=fd)
            self.type.print(fd, 0)
            if (self.name != None):
                print(" as ", end="", file=fd)
                self.name.print(fd, 0)
            print(":", file=fd)
        self.body.print(fd, (level + 1))

class WithClauseNode(ClauseNode):

    def __init__(self, items, body):
        super().__init__(body)
        self.items = items

    def toBlock(self, frame, block):
        return block.newWithClauseBlock(frame, self)

    def print(self, fd, level):
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
        print(":", file=fd)
        self.body.print(fd, (level + 1))

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

    def toBlock(self, frame, block):
        return block.newForClauseBlock(frame, self)

    def print(self, fd, level):
        self.printIndent(fd, level)
        print("for ", end="", file=fd)
        self.target.print(fd, 0)
        print(" in ", end="", file=fd)
        self.expr.print(fd, 0)
        print(":", file=fd)
        self.body.print(fd, (level + 1))

class ReturnNode(Node):

    def __init__(self, what):
        super().__init__()
        self.what = what

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

    def __init__(self, name, asname):
        super().__init__()
        self.name = name
        self.asname = asname

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
# n values separated by n-1 operators

class ListopNode(Node):

    def __init__(self, values, ops):
        super().__init__()
        self.values = values
        self.ops = ops

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
            if (i != 0):
                print(", ", end="", file=fd)
            self.entries[i].print(fd, 0)
        print("]", end="", file=fd)

class ListcompNode(Node):

    def __init__(self, elt, generators):
        super().__init__()
        self.elt = elt
        self.generators = generators

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
        print("\"", end="", file=fd)
        for c in self.what:
            if (c == "\\"):
                print("\\\\", end="", file=fd)
            elif (c == "\""):
                print("\\\"", end="", file=fd)
            elif (c == "\n"):
                print("\\n", end="", file=fd)
            elif (c == "\r"):
                print("\\r", end="", file=fd)
            else:
                print(c, end="", file=fd)
        print("\"", end="", file=fd)

class BytesNode(Node):

    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, block):
        return block.newBytesBlock(frame, self)

    def print(self, fd, level):
        print(self.what, end="", file=fd)

class ExpressionNode(Node):

    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, block):
        return block.newExpressionBlock(frame, self)

    def print(self, fd, level):
        self.what.print(fd, 0)

class SeqNode(Node):

    def __init__(self, rows):
        super().__init__()
        self.rows = rows

    def toBlock(self, frame, block):
        return block.newSeqBlock(frame, self)

    def findRow(self, lineno):
        for i in range(len(self.rows)):
            if (self.rows[i].lineno >= lineno):
                return (self, i)
            r = self.rows[i].findRow(lineno)
            if (r != None):
                return r
        return None

    def print(self, fd, level):
        for r in self.rows:
            r.print(fd, level)
