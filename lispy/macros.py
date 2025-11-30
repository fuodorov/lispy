from .evaluator import eval
from .parser import to_string
from .types import (
    Exp,
    Symbol,
    _append,
    _begin,
    _cons,
    _define,
    _definemacro,
    _if,
    _lambda,
    _let,
    _quasiquote,
    _quote,
    _set,
    _unquote,
    _unquotesplicing,
)


# Helper for is_pair since it was in primitives but needed here for expand_quasiquote
def is_pair(x: Exp) -> bool:
    return x != [] and isinstance(x, list)


def require(x: Exp, predicate: bool, msg: str = "wrong length") -> None:
    """
    Signal a syntax error if predicate is false.

    Args:
        x (Exp): The expression causing the error.
        predicate (bool): The condition that must be true.
        msg (str): The error message. Defaults to "wrong length".

    Raises:
        SyntaxError: If predicate is False.
    """
    if not predicate:
        raise SyntaxError(to_string(x) + ': ' + msg)


def expand(x: Exp, toplevel: bool = False) -> Exp:
    """
    Walk tree of x, making optimizations/fixes, and signaling SyntaxError.

    This function handles macro expansion and syntax checking for special forms.

    Args:
        x (Exp): The expression to expand.
        toplevel (bool): Whether this is a top-level expression (relevant for define-macro).

    Returns:
        Exp: The expanded expression.

    Raises:
        SyntaxError: If the syntax is invalid.
    """
    require(x, x != [])                 # () => Error
    if not isinstance(x, list):         # constant => unchanged
        return x

    op = x[0]
    if op is _quote:                    # (quote exp)
        require(x, len(x) == 2)
        return x
    elif op is _if:
        if len(x) == 3:
            x = x + [None]              # (if t c) => (if t c None)
        require(x, len(x) == 4)
        return list(map(expand, x))
    elif op is _set:
        require(x, len(x) == 3)
        var = x[1]                      # (set! non-var exp) => Error
        require(x, isinstance(var, Symbol), "can set! only a symbol")
        return [_set, var, expand(x[2])]
    elif op is _define or op is _definemacro:
        require(x, len(x) >= 3)
        _def, v, body = x[0], x[1], x[2:]
        if isinstance(v, list) and v:   # (define (f args) body)
            f, args = v[0], v[1:]       # => (define f (lambda (args) body))
            return expand([_def, f, [_lambda, args] + body])
        else:
            require(x, len(x) == 3)     # (define non-var/list exp) => Error
            require(x, isinstance(v, Symbol), "can define only a symbol")
            exp = expand(x[2])
            if _def is _definemacro:
                require(x, toplevel, "define-macro only allowed at top level")
                proc = eval(exp)
                require(x, callable(proc), "macro must be a procedure")
                macro_table[v] = proc   # (define-macro v proc)
                return None             # => None; add v:proc to macro_table
            return [_define, v, exp]
    elif op is _begin:
        if len(x) == 1:
            return None                 # (begin) => None
        else:
            return [expand(xi, toplevel) for xi in x]
    elif op is _lambda:                 # (lambda (x) e1 e2)
        require(x, len(x) >= 3)         # => (lambda (x) (begin e1 e2))
        vars, body = x[1], x[2:]
        require(x, (isinstance(vars, list) and all(isinstance(v, Symbol) for v in vars))
                or isinstance(vars, Symbol), "illegal lambda argument list")
        exp = body[0] if len(body) == 1 else [_begin] + body
        return [_lambda, vars, expand(exp)]
    elif op is _quasiquote:             # `x => expand_quasiquote(x)
        require(x, len(x) == 2)
        return expand_quasiquote(x[1])
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
    require(x, x[0] is not _unquotesplicing, "can't splice here")
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
                   for b in bindings), "illegal binding list")
    vars, vals = zip(*bindings)
    return [[_lambda, list(vars)] + list(map(expand, body))] + list(map(expand, vals))


macro_table = {_let: let}
