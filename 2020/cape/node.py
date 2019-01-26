class Node():
    def toBlock(self, frame):
        return None

    def findRow(self, lineno):
        return None

class PassNode(Node):
    def __init__(self):
        super().__init__()

    def toBlock(self, frame, level, block):
        return block.newPassBlock(frame, self, level, block)

class EmptyNode(Node):
    def __init__(self):
        super().__init__()

    def toBlock(self, frame, level, block):
        return block.newEmptyBlock(frame, self, level)

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
        return block.newDefBlock(frame, self, level)

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
        return block.newClassBlock(frame, self, level)

    def findRow(self, lineno):
        return self.body.findRow(lineno)

class IfNode(Node):
    def __init__(self, conds, bodies, minimizeds):
        super().__init__()
        self.conds = conds
        self.bodies = bodies
        self.minimizeds = minimizeds

    def toBlock(self, frame, level, block):
        return block.newIfBlock(frame, self, level)

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
        return block.newWhileBlock(frame, self, level)

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
        return block.newForBlock(frame, self, level)

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
        return block.newReturnBlock(frame, self, level)

class BreakNode(Node):
    def __init__(self):
        super().__init__()

    def toBlock(self, frame, level, block):
        return block.newBreakBlock(frame, self, level)

class ContinueNode(Node):
    def __init__(self):
        super().__init__()

    def toBlock(self, frame, level, block):
        return block.newContinueBlock(frame, self, level)

class ImportNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return block.newImportBlock(frame, self, level)

class GlobalNode(Node):
    def __init__(self, names):
        super().__init__()
        self.names = names

    def toBlock(self, frame, level, block):
        return block.newGlobalBlock(frame, self, level)

class AssignNode(Node):
    def __init__(self, targets, value):
        super().__init__()
        self.targets = targets
        self.value = value

    def toBlock(self, frame, level, block):
        return block.newAssignBlock(frame, self, level)

class AugassignNode(Node):
    def __init__(self, left, right, op):
        super().__init__()
        self.left = left
        self.right = right
        self.op = op

    def toBlock(self, frame, level, block):
        return block.newAugassignBlock(frame, self, level, self.op)

class BinaryopNode(Node):
    def __init__(self, left, right, op):
        super().__init__()
        self.left = left
        self.right = right
        self.op = op

    def toBlock(self, frame, level, block):
        return block.newBinaryopBlock(frame, self, self.op)

class UnaryopNode(Node):
    def __init__(self, right, op):
        super().__init__()
        self.right = right
        self.op = op

    def toBlock(self, frame, level, block):
        return block.newUnaryopBlock(frame, self, self.op)

class SubscriptNode(Node):
    def __init__(self, array, slice):
        super().__init__()
        self.array = array
        self.slice = slice

    def toBlock(self, frame, level, block):
        isSlice, lower, upper, step = self.slice
        return block.newSubscriptBlock(frame, self, isSlice)

class FuncNode(Node):
    def __init__(self, func, args):
        super().__init__()
        self.func = func
        self.args = args

    def toBlock(self, frame, level, block):
        return block.newFuncBlock(frame, self)

class ListNode(Node):
    def __init__(self, entries):
        super().__init__()
        self.entries = entries

    def toBlock(self, frame, level, block):
        return block.newListBlock(frame, self)

class TupleNode(Node):
    def __init__(self, entries):
        super().__init__()
        self.entries = entries

    def toBlock(self, frame, level, block):
        return block.newTupleBlock(frame, self)

class AttrNode(Node):
    def __init__(self, array, ref):
        super().__init__()
        self.array = array
        self.ref = ref

    def toBlock(self, frame, level, block):
        return block.newAttrBlock(frame, self)

class EvalNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return block.newEvalBlock(frame, self, level)

class NumberNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return block.newNumberBlock(frame, self.what)

class ConstantNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return block.newConstantBlock(frame, self.what)

class NameNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return block.newNameBlock(frame, self.what)

class StringNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return block.newStringBlock(frame, self.what)

class ExpressionNode(Node):
    def __init__(self, what):
        super().__init__()
        self.what = what

    def toBlock(self, frame, level, block):
        return block.newExpressionBlock(frame, self.what, False)

class SeqNode(Node):
    def __init__(self, rows):
        super().__init__()
        self.rows = rows

    def toBlock(self, frame, level, block):
        return block.newSeqBlock(frame, self.rows, level)

    def findRow(self, lineno):
        for i in range(len(self.rows)):
            if self.rows[i].lineno >= lineno:
                return (self, i)
            r = self.rows[i].findRow(lineno)
            if r != None:
                return r
        return None
