from node import *
__all__ = ["nodeEval"]

def Module(body):
    return ModuleNode(BasicClauseNode("module", SeqNode(body)))

def Lambda(lineno, col_offset, args, body):
    (argnames, defaults) = args
    return ExpressionNode(LambdaNode(argnames, defaults, body))

def FunctionDef(lineno, col_offset, name, args, body, decorator_list, returns):
    (argnames, defaults, vararg, kwarg) = args
    return StatementNode(ContainerNode(DefClauseNode(name, argnames, defaults, vararg, kwarg, SeqNode(body))), lineno)

def ClassDef(lineno, col_offset, name, bases, keywords, body, decorator_list):
    return StatementNode(ContainerNode(ClassClauseNode(name, [ExpressionNode(x.what) for x in bases], SeqNode(body))), lineno)

def arguments(args, vararg, kwonlyargs, kw_defaults, kwarg, defaults):
    return (args + kwonlyargs, defaults + kw_defaults, vararg, kwarg)

def args(lineno, col_offset, arg, annotation):
    return arg

def Assign(lineno, col_offset, targets, value):
    return StatementNode(AssignNode(targets, value), lineno)

def AugAssign(lineno, col_offset, target, op, value):
    return StatementNode(AugassignNode(target, value, (op + "=")), lineno)

def Name(lineno, col_offset, id, ctx):
    if (id == "__CAPE_UNINITIALIZED__"):
        return ExpressionNode(None)
    else:
        return ExpressionNode(NameNode(id))

def Subscript(lineno, col_offset, value, slice, ctx):
    return ExpressionNode(SubscriptNode(value, slice))

def Index(value):
    return (False, value, None, None)

def Slice(lower, upper, step):
    return (True, lower, upper, step)

def Num(lineno, col_offset, n):
    return ExpressionNode(NumberNode(n))

def Str(lineno, col_offset, s):
    return ExpressionNode(StringNode(s))

def Bytes(lineno, col_offset, s):
    return ExpressionNode(BytesNode(s))

def For(lineno, col_offset, target, iter, body, orelse):
    if orelse == []:
        return StatementNode(ForNode([ForClauseNode(target, iter, SeqNode(body))], False), lineno)
    else:
        return StatementNode(ForNode([ForClauseNode(target, iter, SeqNode(body)), BasicClauseNode("else", SeqNode(orelse))], True), lineno)

def While(lineno, col_offset, test, body, orelse):
    if orelse == []:
        return StatementNode(WhileNode([CondClauseNode("while", test, SeqNode(body))], False), lineno)
    else:
        return StatementNode(WhileNode([CondClauseNode("while", test, SeqNode(body)), BasicClauseNode("else", SeqNode(orelse))], True), lineno)

def If(lineno, col_offset, test, body, orelse):
    if (orelse == []):
        return StatementNode(IfNode([CondClauseNode("if", test, SeqNode(body))], False), lineno)
    if (len(orelse) == 1):
        row = orelse[0]
        assert isinstance(row, StatementNode)
        stmt = row.what
        if isinstance(stmt, IfNode):
            stmt.clauses[0].type = "elif"
            return StatementNode(IfNode([CondClauseNode("if", test, SeqNode(body))] + stmt.clauses, stmt.hasElse), lineno)
    return StatementNode(IfNode([CondClauseNode("if", test, SeqNode(body)), BasicClauseNode("else", SeqNode(orelse))], True), lineno)

def Try(lineno, col_offset, body, handlers, orelse, finalbody):
    clauses = [BasicClauseNode("try", SeqNode(body))] + handlers
    if orelse != []:
        clauses.append(BasicClauseNode("else", SeqNode(orelse)))
    if finalbody != []:
        clauses.append(BasicClauseNode("finally", SeqNode(finalbody)))
    return StatementNode(TryNode(clauses, orelse != []), lineno)

def ExceptHandler(lineno, col_offset, type, name, body):
    return ExceptClauseNode(type, name, SeqNode(body))

def With(lineno, col_offset, items, body):
    return StatementNode(ContainerNode(WithClauseNode(items, SeqNode(body))), lineno)

def Compare(lineno, col_offset, left, ops, comparators):
    return ExpressionNode(ListopNode(([left] + comparators), ops))

def Yield(lineno, col_offset, value):
    return ExpressionNode(YieldNode(value))

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
    return StatementNode(ReturnNode(value), lineno)

def Delete(lineno, col_offset, targets):
    return StatementNode(DelNode(targets), lineno)

def Assert(lineno, col_offset, test, msg):
    return StatementNode(AssertNode(test, msg), lineno)

def Break(lineno, col_offset):
    return StatementNode(BreakNode(), lineno)

def Continue(lineno, col_offset):
    return StatementNode(ContinueNode(), lineno)

def Pass(lineno, col_offset):
    return StatementNode(PassNode(), lineno)

def Call(lineno, col_offset, func, args, keywords, starargs=None, kwargs=None):
    return ExpressionNode(CallNode(func, args, keywords))

def Load():
    return None

def Store():
    return None

def Del():
    return None

def List(lineno, col_offset, elts, ctx):
    return ExpressionNode(ListNode(elts))

def Set(lineno, col_offset, elts):
    return ExpressionNode(SetNode(elts))

def Tuple(lineno, col_offset, elts, ctx):
    return ExpressionNode(TupleNode(elts))

def Expr(lineno, col_offset, value):
    return StatementNode(EvalNode(value), lineno)

def Expression(body):
    return body

def Interactive(body):
    assert (len(body) == 1)
    return body[0]

def Attribute(lineno, col_offset, value, attr, ctx):
    return ExpressionNode(AttrNode(value, NameNode(attr)))

def arg(lineno, col_offset, arg, annotation):
    return arg

def NameConstant(lineno, col_offset, value):
    return ExpressionNode(ConstantNode(str(value)))

def BinOp(lineno, col_offset, left, op, right):
    return ExpressionNode(BinaryopNode(left, right, op))

def UnaryOp(lineno, col_offset, op, operand):
    return ExpressionNode(UnaryopNode(operand, op))

def Starred(lineno, col_offset, value, ctx):
    return ExpressionNode(UnaryopNode(value, "*"))

def BoolOp(lineno, col_offset, op, values):
    return ExpressionNode(ListopNode(values, ([op] * (len(values) - 1))))

def alias(name, asname):
    return (name, asname)

def keyword(arg, value):
    return (arg, value)

def attrify(components):
    if (len(components) == 1):
        return NameNode(components[0])
    else:
        return AttrNode(attrify(components[:(- 1)]), NameNode(components[(- 1)]))

def Import(lineno, col_offset, names):
    [(name, asname)] = names
    components = name.split(".")
    return StatementNode(ImportNode(attrify(components), (None if (asname == None) else NameNode(asname))), lineno)

def ImportFrom(lineno, col_offset, module, names, level):
    components = module.split(".")
    return StatementNode(ImportfromNode(attrify(components), [(NameNode(name), (None if (asname == None) else NameNode(asname))) for (name, asname) in names]), lineno)

def Global(lineno, col_offset, names):
    return StatementNode(GlobalNode([NameNode(n) for n in names]), lineno)

def Dict(lineno, col_offset, keys, values):
    return ExpressionNode(DictNode(keys, values))

def IfExp(lineno, col_offset, test, body, orelse):
    return ExpressionNode(IfelseNode(test, body, orelse))

def GeneratorExp(lineno, col_offset, elt, generators):
    return ExpressionNode(GenexpNode(elt, generators))

def ListComp(lineno, col_offset, elt, generators):
    return ExpressionNode(ListcompNode(elt, generators))

def SetComp(lineno, col_offset, elt, generators):
    return ExpressionNode(SetcompNode(elt, generators))

def DictComp(lineno, col_offset, key, value, generators):
    return ExpressionNode(DictcompNode(key, value, generators))

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

def BitOr():
    return "|"

def BitAnd():
    return "&"

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

def comprehension(target, iter, ifs, is_async=0):
    return (target, iter, ifs, is_async)

def withitem(context_expr, optional_vars):
    return (context_expr, optional_vars)

def nodeEval(tree):
    return eval(tree)
