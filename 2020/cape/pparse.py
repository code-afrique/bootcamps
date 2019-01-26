from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# The following code essentially borrowed from https://github.com/asottile/astpretty

import ast
import contextlib

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

def pparse(code):
    return pformat(ast.parse(code))
