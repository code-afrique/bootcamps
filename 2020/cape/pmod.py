from node import *
__all__ = ["nodeEval"]

def Module(body, **va):
    return ModuleNode(body)

def Lambda(args, body, **va):
    (argnames, defaults, vararg, kwarg) = args
    return ExpressionNode(LambdaNode(argnames, defaults, vararg, kwarg, body))

def FunctionDef(lineno, name, args, body, decorator_list, **va):
    (argnames, defaults, vararg, kwarg) = args
    return StatementNode(DefNode(name, argnames, defaults, vararg, kwarg, body, True, decorator_list), lineno)

def ClassDef(lineno, name, bases, body, decorator_list, **va):
    return StatementNode(ClassNode(name, [ExpressionNode(x.what) for x in bases], body, True, decorator_list), lineno)

def arguments(args, vararg, kwonlyargs, kw_defaults, kwarg, defaults, **va):
    return (args + kwonlyargs, defaults + kw_defaults, vararg, kwarg)

def args(arg, **va):
    return arg

def Assign(lineno, targets, value, **va):
    return StatementNode(AssignNode(targets, value), lineno)

def AugAssign(lineno, target, op, value, **va):
    return StatementNode(AugassignNode(target, value, (op + "=")), lineno)

def Name(id, **va):
    if (id == "__CAPE_UNINITIALIZED__"):
        return ExpressionNode(None)
    else:
        return ExpressionNode(NameNode(id))

def Subscript(value, slice, **va):
    return ExpressionNode(SubscriptNode(value, slice))

def Index(value, **va):
    return (False, value, None, None)

def Slice(lower, upper, step, **va):
    return (True, lower, upper, step)

def Num(n, **va):
    return ExpressionNode(NumberNode(n))

def Str(s, **va):
    return ExpressionNode(StringNode(s))

def Bytes(s, **va):
    return ExpressionNode(BytesNode(s))

def For(lineno, target, iter, body, orelse, **va):
    if orelse == []:
        return StatementNode(ForNode([ForClauseNode(target, iter, body, False)], False), lineno)
    else:
        return StatementNode(ForNode([ForClauseNode(target, iter, body, False), BasicClauseNode("else", orelse, False)], True), lineno)

def While(lineno, test, body, orelse, **va):
    if orelse == []:
        return StatementNode(WhileNode([CondClauseNode("while", test, body, False)], False), lineno)
    else:
        return StatementNode(WhileNode([CondClauseNode("while", test, body, False), BasicClauseNode("else", orelse, False)], True), lineno)

def If(lineno, test, body, orelse, **va):
    if (orelse == []):
        return StatementNode(IfNode([CondClauseNode("if", test, body, False)], False), lineno)
    if (len(orelse) == 1):
        row = orelse[0]
        assert isinstance(row, StatementNode)
        stmt = row.what
        if isinstance(stmt, IfNode):
            stmt.clauses[0].type = "elif"
            return StatementNode(IfNode([CondClauseNode("if", test, body, False)] + stmt.clauses, stmt.hasElse), lineno)
    return StatementNode(IfNode([CondClauseNode("if", test, body, False), BasicClauseNode("else", orelse, False)], True), lineno)

def Try(lineno, body, handlers, orelse, finalbody, **va):
    clauses = [BasicClauseNode("try", body, False)] + handlers
    if orelse != []:
        clauses.append(BasicClauseNode("else", orelse, False))
    if finalbody != []:
        clauses.append(BasicClauseNode("finally", finalbody, False))
    return StatementNode(TryNode(clauses, orelse != []), lineno)

def ExceptHandler(type, name, body, **va):
    return ExceptClauseNode(type, name, body, False)

def With(lineno, items, body, **va):
    return StatementNode(WithNode(items, body, False), lineno)

def Compare(left, ops, comparators, **va):
    return ExpressionNode(ListopNode(([left] + comparators), ops))

def Yield(value, **va):
    return ExpressionNode(YieldNode(value))

def Is(**va):
    return "is"

def IsNot(**va):
    return "is not"

def Eq(**va):
    return "=="

def NotEq(**va):
    return "!="

def Lt(**va):
    return "<"

def LtE(**va):
    return "<="

def Gt(**va):
    return ">"

def GtE(**va):
    return ">="

def Return(lineno, value, **va):
    return StatementNode(ReturnNode(value), lineno)

def Delete(lineno, targets, **va):
    return StatementNode(DelNode(targets), lineno)

def Assert(lineno, test, msg, **va):
    return StatementNode(AssertNode(test, msg), lineno)

def Break(lineno, **va):
    return StatementNode(BreakNode(), lineno)

def Continue(lineno, **va):
    return StatementNode(ContinueNode(), lineno)

def Pass(lineno, **va):
    return StatementNode(PassNode(), lineno)

def Call(func, args, keywords, **va):
    return ExpressionNode(CallNode(func, args, keywords))

def Load(**va):
    return None

def Store(**va):
    return None

def Del(**va):
    return None

def List(elts, **va):
    return ExpressionNode(ListNode(elts))

def Set(elts, **va):
    return ExpressionNode(SetNode(elts))

def Tuple(elts, **va):
    return ExpressionNode(TupleNode(elts))

def Expr(lineno, value, **va):
    return StatementNode(EvalNode(value), lineno)

def Expression(body, **va):
    return body

def Interactive(body, **va):
    assert (len(body) == 1)
    return body[0]

def Attribute(value, attr, **va):
    return ExpressionNode(AttrNode(value, NameNode(attr)))

def arg(arg, **va):
    return arg

def NameConstant(value, **va):
    return ExpressionNode(ConstantNode(str(value)))

def Constant(value, **va):
    t = type(value)
    if t == str:
        return ExpressionNode(StringNode(value))
    if t == int or t == float:
        return ExpressionNode(NumberNode(value))
    if t == bytes:
        return ExpressionNode(BytesNode(value))
    return ExpressionNode(ConstantNode(str(value)))

def BinOp(left, op, right, **va):
    return ExpressionNode(BinaryopNode(left, right, op))

def UnaryOp(op, operand, **va):
    return ExpressionNode(UnaryopNode(operand, op))

def Starred(value, **va):
    return ExpressionNode(UnaryopNode(value, "*"))

def BoolOp(op, values, **va):
    return ExpressionNode(ListopNode(values, ([op] * (len(values) - 1))))

def alias(name, asname, **va):
    return (name, asname)

def keyword(arg, value, **va):
    return (arg, value)

def attrify(components):
    if (len(components) == 1):
        return NameNode(components[0])
    else:
        return AttrNode(attrify(components[:(- 1)]), NameNode(components[(- 1)]))

def Import(lineno, names, **va):
    [(name, asname)] = names
    components = name.split(".")
    return StatementNode(ImportNode(attrify(components), (None if (asname == None) else NameNode(asname))), lineno)

def ImportFrom(lineno, module, names, **va):
    components = module.split(".")
    return StatementNode(ImportfromNode(attrify(components), [(NameNode(name), (None if (asname == None) else NameNode(asname))) for (name, asname) in names]), lineno)

def Global(lineno, names, **va):
    return StatementNode(GlobalNode([NameNode(n) for n in names]), lineno)

def Dict(keys, values, **va):
    return ExpressionNode(DictNode(keys, values))

def IfExp(test, body, orelse, **va):
    return ExpressionNode(IfelseNode(test, body, orelse))

def GeneratorExp(elt, generators, **va):
    return ExpressionNode(GenexpNode(elt, generators))

def ListComp(elt, generators, **va):
    return ExpressionNode(ListcompNode(elt, generators))

def SetComp(elt, generators, **va):
    return ExpressionNode(SetcompNode(elt, generators))

def DictComp(key, value, generators, **va):
    return ExpressionNode(DictcompNode(key, value, generators))

def Add(**va):
    return "+"

def Sub(**va):
    return "-"

def Div(**va):
    return "/"

def FloorDiv(**va):
    return "//"

def Mod(**va):
    return "%"

def Mult(**va):
    return "*"

def Pow(**va):
    return "**"

def BitOr(**va):
    return "|"

def BitAnd(**va):
    return "&"

def USub(**va):
    return "-"

def Not(**va):
    return "not"

def Or(**va):
    return "or"

def And(**va):
    return "and"

def In(**va):
    return "in"

def NotIn(**va):
    return "not in"

def comprehension(target, iter, ifs, is_async=0, **va):
    return (target, iter, ifs, is_async)

def withitem(context_expr, optional_vars, **va):
    return (context_expr, optional_vars)

def nodeEval(tree):
    return eval(tree)
