"""
Macro expansion module.

This module handles the expansion of macros and special forms before evaluation.
It includes the `expand` function and handlers for various special forms.
"""
from .constants import TYPE_ANNOTATION_CHAR
from .errors import SchemeSyntaxError
from .evaluator import eval
from .messages import (
    ERR_CANT_SPLICE,
    ERR_DEFINE_MACRO_TOPLEVEL,
    ERR_DEFINE_SYMBOL,
    ERR_ILLEGAL_BINDING,
    ERR_ILLEGAL_LAMBDA,
    ERR_MACRO_PROCEDURE,
    ERR_SET_SYMBOL,
    ERR_WRONG_LENGTH,
)
from .parser import to_string
from .types import (
    Exp,
    Symbol,
    _append,
    _begin,
    _cons,
    _define,
    _definemacro,
    _delay,
    _dynamic_let,
    _if,
    _lambda,
    _let,
    _make_promise,
    _quasiquote,
    _quote,
    _set,
    _try,
    _unquote,
    _unquotesplicing,
)


def is_pair(x: Exp) -> bool:
    """
    Check if x is a pair (non-empty list).

    Args:
        x (Exp): The expression to check.

    Returns:
        bool: True if x is a pair, False otherwise.
    """
    return x != [] and isinstance(x, list)


def require(x: Exp, predicate: bool, msg: str = ERR_WRONG_LENGTH) -> None:
    """
    Signal a syntax error if predicate is false.

    Args:
        x (Exp): The expression causing the error.
        predicate (bool): The condition that must be true.
        msg (str): The error message. Defaults to "wrong length".

    Raises:
        SchemeSyntaxError: If predicate is False.
    """
    if not predicate:
        raise SchemeSyntaxError(to_string(x) + ': ' + msg)


def expand_quote(x: Exp, toplevel: bool) -> Exp:
    """
    Expand a quote expression.

    Args:
        x (Exp): The expression.
        toplevel (bool): Whether it's at the top level.

    Returns:
        Exp: The expanded expression.
    """
    require(x, len(x) == 2)
    return x


def expand_if(x: Exp, toplevel: bool) -> Exp:
    """
    Expand an if expression.

    Args:
        x (Exp): The expression.
        toplevel (bool): Whether it's at the top level.

    Returns:
        Exp: The expanded expression.
    """
    if len(x) == 3:
        x = x + [None]
    require(x, len(x) == 4)
    return list(map(expand, x))


def expand_set(x: Exp, toplevel: bool) -> Exp:
    """
    Expand a set! expression.

    Args:
        x (Exp): The expression.
        toplevel (bool): Whether it's at the top level.

    Returns:
        Exp: The expanded expression.
    """
    require(x, len(x) == 3)
    var = x[1]
    require(x, isinstance(var, Symbol), ERR_SET_SYMBOL)
    return [_set, var, expand(x[2])]


def expand_define(x: Exp, toplevel: bool) -> Exp:
    """
    Expand a define expression.

    Args:
        x (Exp): The expression.
        toplevel (bool): Whether it's at the top level.

    Returns:
        Exp: The expanded expression.
    """
    require(x, len(x) >= 3)
    _def, v, body = x[0], x[1], x[2:]
    if isinstance(v, list) and v:
        f, args = v[0], v[1:]
        return expand([_def, f, [_lambda, args] + body], toplevel)
    else:
        if len(x) == 5 and x[2] == TYPE_ANNOTATION_CHAR:
            # Typed definition: (define var :: type exp)
            require(x, isinstance(v, Symbol), ERR_DEFINE_SYMBOL)
            exp = expand(x[4])
            return [_define, v, TYPE_ANNOTATION_CHAR, x[3], exp]

        require(x, len(x) == 3)
        require(x, isinstance(v, Symbol), ERR_DEFINE_SYMBOL)
        exp = expand(x[2])
        if _def is _definemacro:
            require(x, toplevel, ERR_DEFINE_MACRO_TOPLEVEL)
            proc = eval(exp)
            require(x, callable(proc), ERR_MACRO_PROCEDURE)
            macro_table[v] = proc
            return None
        return [_define, v, exp]


def expand_begin(x: Exp, toplevel: bool) -> Exp:
    """
    Expand a begin expression.

    Args:
        x (Exp): The expression.
        toplevel (bool): Whether it's at the top level.

    Returns:
        Exp: The expanded expression.
    """
    if len(x) == 1:
        return None
    else:
        return [expand(xi, toplevel) for xi in x]


def expand_lambda(x: Exp, toplevel: bool) -> Exp:
    """
    Expand a lambda expression.

    Args:
        x (Exp): The expression.
        toplevel (bool): Whether it's at the top level.

    Returns:
        Exp: The expanded expression.
    """
    require(x, len(x) >= 3)
    vars, body = x[1], x[2:]
    require(x, (isinstance(vars, list) and all(isinstance(v, Symbol) for v in vars))
            or isinstance(vars, Symbol), ERR_ILLEGAL_LAMBDA)
    exp = body[0] if len(body) == 1 else [_begin] + body
    return [_lambda, vars, expand(exp)]


def expand_quasiquote_macro(x: Exp, toplevel: bool) -> Exp:
    """
    Expand a quasiquote expression.

    Args:
        x (Exp): The expression.
        toplevel (bool): Whether it's at the top level.

    Returns:
        Exp: The expanded expression.
    """
    require(x, len(x) == 2)
    return expand_quasiquote(x[1])


def expand_try(x: Exp, toplevel: bool) -> Exp:
    """
    Expand a try expression.

    Args:
        x (Exp): The expression.
        toplevel (bool): Whether it's at the top level.

    Returns:
        Exp: The expanded expression.
    """
    require(x, len(x) == 3)
    return [_try, expand(x[1], toplevel), expand(x[2], toplevel)]


def expand_dynamic_let(x: Exp, toplevel: bool) -> Exp:
    """
    Expand a dynamic-let expression.

    Args:
        x (Exp): The expression.
        toplevel (bool): Whether it's at the top level.

    Returns:
        Exp: The expanded expression.
    """
    require(x, len(x) >= 3)
    bindings, body = x[1], x[2:]
    require(x, all(isinstance(b, list) and len(b) == 2 and isinstance(b[0], Symbol)
                   for b in bindings), ERR_ILLEGAL_BINDING)
    expanded_bindings = [[b[0], expand(b[1], toplevel)] for b in bindings]
    expanded_body = [expand(e, toplevel) for e in body]
    return [_dynamic_let, expanded_bindings] + expanded_body


SPECIAL_FORMS = {
    _quote: expand_quote,
    _if: expand_if,
    _set: expand_set,
    _define: expand_define,
    _definemacro: expand_define,
    _begin: expand_begin,
    _lambda: expand_lambda,
    _quasiquote: expand_quasiquote_macro,
    _try: expand_try,
    _dynamic_let: expand_dynamic_let,
}


def expand(x: Exp, toplevel: bool = False) -> Exp:
    """
    Walk tree of x, making optimizations/fixes, and signaling SchemeSyntaxError.

    This function handles macro expansion and syntax checking for special forms.

    Args:
        x (Exp): The expression to expand.
        toplevel (bool): Whether this is a top-level expression (relevant for define-macro).

    Returns:
        Exp: The expanded expression.

    Raises:
        SchemeSyntaxError: If the syntax is invalid.
    """
    require(x, x != [])                 # () => Error
    if not isinstance(x, list):         # constant => unchanged
        return x

    op = x[0]
    if isinstance(op, Symbol) and op in SPECIAL_FORMS:
        return SPECIAL_FORMS[op](x, toplevel)
    elif isinstance(op, Symbol) and op in macro_table:
        return expand(macro_table[op](*x[1:]), toplevel)  # (m arg...)
    else:                               # => macroexpand if m isa macro
        return list(map(expand, x))     # (f arg...) => expand each


def expand_quasiquote(x: Exp) -> Exp:
    """
    Expand quasiquote expressions.

    Expands `` `x => 'x``, `` `,x => x``, and `` `(,@x y) => (append x y)``.

    Args:
        x (Exp): The quasiquoted expression.

    Returns:
        Exp: The expanded expression using cons, append, and quote.
    """
    if not is_pair(x):
        return [_quote, x]
    require(x, x[0] is not _unquotesplicing, ERR_CANT_SPLICE)
    if x[0] is _unquote:
        require(x, len(x) == 2)
        return x[1]
    elif is_pair(x[0]) and x[0][0] is _unquotesplicing:
        require(x[0], len(x[0]) == 2)
        return [_append, x[0][1], expand_quasiquote(x[1:])]
    else:
        return [_cons, expand_quasiquote(x[0]), expand_quasiquote(x[1:])]


def let(*args: Exp) -> Exp:
    """
    Expand a `let` expression into a lambda application.

    (let ((v1 e1) ...) body...) => ((lambda (v1 ...) body...) e1 ...)

    Args:
        *args (Exp): The arguments to the let macro (bindings and body).

    Returns:
        Exp: The expanded expression.
    """
    args = list(args)
    x = [_let] + args
    require(x, len(args) > 1)
    bindings, body = args[0], args[1:]
    require(x, all(isinstance(b, list) and len(b) == 2 and isinstance(b[0], Symbol)
                   for b in bindings), ERR_ILLEGAL_BINDING)
    if not bindings:
        vars, vals = [], []
    else:
        vars, vals = zip(*bindings)
    return [[_lambda, list(vars)] + list(map(expand, body))] + list(map(expand, vals))


def delay(exp: Exp) -> Exp:
    """
    Expand a delay expression.

    (delay exp) -> (make-promise (lambda () exp))

    Args:
        exp (Exp): The expression to delay.

    Returns:
        Exp: The expanded expression.
    """
    return [_make_promise, [_lambda, [], exp]]


macro_table = {_let: let, _delay: delay}
