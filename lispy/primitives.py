"""
Standard library primitives.

This module defines the standard Scheme procedures available in the global
environment, such as arithmetic operations, list manipulation, and I/O.
"""
import cmath
import functools
import importlib
import io
import math
import operator as op
import sys
from typing import Any, Callable

from .constants import FILE_WRITE_MODE
from .env import Env
from .errors import ArgumentError, Continuation, UserError
from .evaluator import Procedure
from .evaluator import eval as lispy_eval
from .macros import expand
from .messages import ERR_CURRY_USER_PROC, ERR_CURRY_VARIADIC
from .parser import read, readchar, to_string
from .repl import load
from .types import EOF_OBJECT, Exp, ListType, Promise, Symbol


def callcc(proc: Callable) -> Any:
    """
    Call proc with current continuation; escape only.

    Args:
        proc (Callable): The procedure to call.

    Returns:
        Any: The result of the procedure or the continuation value.

    Raises:
        Continuation: Used to implement the continuation jump.
    """
    ball = Continuation()

    def throw(retval: Any) -> None:
        """
        Throw the continuation.

        Args:
            retval (Any): The value to return to the continuation point.
        """
        ball.retval = retval
        raise ball
    try:
        return proc(throw)
    except Continuation as w:
        if w is ball:
            return ball.retval
        else:
            raise w


def make_promise(proc: Callable) -> Promise:
    """
    Create a new Promise.

    Args:
        proc (Callable): The thunk (procedure with no arguments) to delay.

    Returns:
        Promise: The created promise.
    """
    return Promise(proc)


def force(obj: Any) -> Any:
    """
    Force the evaluation of a promise.

    Args:
        obj (Any): The object to force.

    Returns:
        Any: The result of the promise evaluation, or the object itself if not a promise.
    """
    while isinstance(obj, Promise):
        if not obj.computed:
            obj.memo = obj.proc()
            obj.computed = True
        obj = obj.memo
    return obj


def curry(proc: Any) -> Any:
    """
    Return a curried version of the procedure.

    Args:
        proc (Any): The procedure to curry.

    Returns:
        Any: A new procedure that accepts arguments incrementally.
    """
    if not isinstance(proc, Procedure):
        raise ArgumentError(ERR_CURRY_USER_PROC.format(proc))

    if not isinstance(proc.parms, list):
        raise ArgumentError(ERR_CURRY_VARIADIC)

    arity = len(proc.parms)

    def curried(*args):
        if len(args) >= arity:
            return proc(*args)
        return lambda *more: curried(*(args + more))

    return curried


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


def raise_error(x: Any) -> None:
    """
    Raise an exception.

    Args:
        x (Any): The exception object or message to raise.

    Raises:
        Exception: The provided exception or a new Exception with the message.
    """
    if isinstance(x, Exception):
        raise x
    else:
        raise UserError(to_string(x))


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
        '+': lambda *x: sum(x),
        '-': lambda x, *y: x - sum(y) if y else -x,
        '*': lambda *x: functools.reduce(op.mul, x, 1),
        '/': lambda x, *y: functools.reduce(op.truediv, y, x) if y else 1 / x,
        'string-append': lambda *x: "".join(map(str, x)),
        'not': op.not_,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'equal?': op.eq, 'eq?': op.is_, 'length': len, 'cons': cons,
        'car': lambda x: x[0], 'cdr': lambda x: x[1:],
        'append': lambda *x: functools.reduce(op.add, x, []),
        'list': lambda *x: list(x), 'list?': lambda x: isinstance(x, list),
        'null?': lambda x: x == [], 'symbol?': lambda x: isinstance(x, Symbol),
        'boolean?': lambda x: isinstance(x, bool), 'pair?': is_pair,
        'port?': lambda x: isinstance(x, io.IOBase), 'apply': lambda proc, lst: proc(*lst),
        'eval': lambda x: lispy_eval(expand(x)), 'load': lambda fn: load(fn), 'call/cc': callcc,
        'force': force, 'make-promise': make_promise, 'curry': curry,
        'open-input-file': open, 'close-input-port': lambda p: p.file.close(),
        'open-output-file': lambda f: open(f, FILE_WRITE_MODE), 'close-output-port': lambda p: p.close(),
        'eof-object?': lambda x: x is EOF_OBJECT, 'read-char': readchar,
        'read': read, 'write': lambda x, port=sys.stdout: port.write(to_string(x)),
        'display': lambda x, port=sys.stdout: port.write(x if isinstance(x, str) else to_string(x)),
        'raise': raise_error,
        'str': str,
        'py-import': importlib.import_module,
        'py-getattr': getattr,
        'py-eval': lambda x: eval(x),
        'py-exec': lambda x: exec(x),
    })
    return env
