import cmath
import io
import math
import operator as op
import sys
from typing import Any, Callable

from .env import Env
from .evaluator import eval
from .macros import expand
from .parser import read, readchar, to_string
from .repl import load
from .types import EOF_OBJECT, Exp, ListType, Symbol


def callcc(proc: Callable) -> Any:
    """
    Call proc with current continuation; escape only.

    Args:
        proc (Callable): The procedure to call.

    Returns:
        Any: The result of the procedure or the continuation value.

    Raises:
        RuntimeWarning: Used to implement the continuation jump.
    """
    ball = RuntimeWarning("Sorry, can't continue this continuation any longer.")

    def throw(retval: Any) -> None:
        ball.retval = retval
        raise ball
    try:
        return proc(throw)
    except RuntimeWarning as w:
        if w is ball:
            return ball.retval
        else:
            raise w


def is_pair(x: Exp) -> bool:
    """
    Check if x is a pair (non-empty list).

    Args:
        x (Exp): The expression to check.

    Returns:
        bool: True if x is a pair, False otherwise.
    """
    return x != [] and isinstance(x, list)


def cons(x: Any, y: ListType) -> ListType:
    """
    Construct a new list with x as the first element and y as the rest.

    Args:
        x (Any): The first element.
        y (ListType): The rest of the list.

    Returns:
        ListType: The new list.
    """
    return [x] + list(y)


def add_globals(env: Env) -> Env:
    """
    Add some Scheme standard procedures to the environment.

    Args:
        env (Env): The environment to populate.

    Returns:
        Env: The updated environment.
    """
    env.update(vars(math))
    env.update(vars(cmath))
    env.update({
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv, 'not': op.not_,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'equal?': op.eq, 'eq?': op.is_, 'length': len, 'cons': cons,
        'car': lambda x: x[0], 'cdr': lambda x: x[1:], 'append': op.add,
        'list': lambda *x: list(x), 'list?': lambda x: isinstance(x, list),
        'null?': lambda x: x == [], 'symbol?': lambda x: isinstance(x, Symbol),
        'boolean?': lambda x: isinstance(x, bool), 'pair?': is_pair,
        'port?': lambda x: isinstance(x, io.IOBase), 'apply': lambda proc, lst: proc(*lst),
        'eval': lambda x: eval(expand(x)), 'load': lambda fn: load(fn), 'call/cc': callcc,
        'open-input-file': open, 'close-input-port': lambda p: p.file.close(),
        'open-output-file': lambda f: open(f, 'w'), 'close-output-port': lambda p: p.close(),
        'eof-object?': lambda x: x is EOF_OBJECT, 'read-char': readchar,
        'read': read, 'write': lambda x, port=sys.stdout: port.write(to_string(x)),
        'display': lambda x, port=sys.stdout: port.write(x if isinstance(x, str) else to_string(x))
    })
    return env
