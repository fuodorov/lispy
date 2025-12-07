"""
Evaluator module for Lispy.

This module contains the core evaluation logic, including the `eval` function
and handlers for special forms. It implements Tail Call Optimization (TCO)
using the `TailCall` class.
"""
from typing import Any, List, Optional

from .constants import TYPE_ANNOTATION_CHAR
from .env import Env, global_env
from .errors import TypeMismatchError
from .messages import ERR_TYPE_MISMATCH
from .type_checker import check_type
from .types import (
    Exp,
    Symbol,
    _begin,
    _define,
    _dynamic_let,
    _if,
    _lambda,
    _quote,
    _set,
    _try,
)


class Procedure:
    """
    A user-defined Scheme procedure.

    Attributes:
        parms (List[Symbol]): The parameter names.
        exp (Exp): The body of the procedure.
        env (Env): The environment in which the procedure was defined (closure).
    """
    def __init__(self, parms: List[Symbol], exp: Exp, env: Env) -> None:
        """
        Initialize the Procedure.

        Args:
            parms (List[Symbol]): Parameter names.
            exp (Exp): Procedure body expression.
            env (Env): Definition environment.
        """
        self.types = {}
        self.parms = []

        if isinstance(parms, list):
            i = 0
            while i < len(parms):
                p = parms[i]
                self.parms.append(p)
                if i + 2 < len(parms) and parms[i + 1] == TYPE_ANNOTATION_CHAR:
                    self.types[p] = parms[i + 2]
                    i += 3
                else:
                    i += 1
        else:
            self.parms = parms

        self.exp, self.env = exp, env

    def check_types(self, args: List[Any]) -> None:
        """
        Check argument types against annotations.
        """
        if isinstance(self.parms, list):
            for i, p in enumerate(self.parms):
                if p in self.types and i < len(args):
                    val = args[i]
                    type_sym = self.types[p]
                    if not check_type(val, type_sym):
                        raise TypeMismatchError(ERR_TYPE_MISMATCH)

    def __call__(self, *args: Exp) -> Any:
        """
        Call the procedure with the given arguments.

        Args:
            *args (Exp): The arguments to pass to the procedure.

        Returns:
            Any: The result of evaluating the procedure body.
        """
        return eval(self.exp, Env(self.parms, args, self.env))


class TailCall:
    """
    Represents a tail call to be executed by the evaluator loop.
    """
    def __init__(self, x: Exp, env: Env) -> None:
        """
        Initialize the TailCall.

        Args:
            x (Exp): The expression to evaluate.
            env (Env): The environment to evaluate in.
        """
        self.x = x
        self.env = env


def eval_quote(x: Exp, env: Env) -> Any:
    """
    Evaluate a quote expression.

    Args:
        x (Exp): The expression (quote exp).
        env (Env): The environment (unused).

    Returns:
        Any: The quoted expression.
    """
    return x[1]


def eval_if(x: Exp, env: Env) -> Any:
    """
    Evaluate an if expression.

    Args:
        x (Exp): The expression (if test conseq alt).
        env (Env): The environment.

    Returns:
        Any: The result of the consequent or alternative, wrapped in TailCall.
    """
    (_, test, conseq, alt) = x
    if eval(test, env):
        return TailCall(conseq, env)
    else:
        return TailCall(alt, env)


def eval_set(x: Exp, env: Env) -> Any:
    """
    Evaluate a set! expression.

    Args:
        x (Exp): The expression (set! var exp).
        env (Env): The environment.

    Returns:
        Any: None.
    """
    (_, var, exp) = x
    env.find(var)[var] = eval(exp, env)
    return None


def eval_define(x: Exp, env: Env) -> Any:
    """
    Evaluate a define expression.

    Args:
        x (Exp): The expression (define var exp).
        env (Env): The environment.

    Returns:
        Any: None.
    """
    if len(x) == 5 and x[2] == TYPE_ANNOTATION_CHAR:
        (_, var, _, type_sym, exp) = x
        val = eval(exp, env)
        if not check_type(val, type_sym):
            raise TypeMismatchError(ERR_TYPE_MISMATCH)
        env[var] = val
    else:
        (_, var, exp) = x
        env[var] = eval(exp, env)
    return None


def eval_lambda(x: Exp, env: Env) -> Any:
    """
    Evaluate a lambda expression.

    Args:
        x (Exp): The expression (lambda vars body).
        env (Env): The environment.

    Returns:
        Procedure: The created procedure.
    """
    (_, vars, exp) = x
    return Procedure(vars, exp, env)


def eval_begin(x: Exp, env: Env) -> Any:
    """
    Evaluate a begin expression.

    Args:
        x (Exp): The expression (begin exp...).
        env (Env): The environment.

    Returns:
        Any: The result of the last expression, wrapped in TailCall.
    """
    for exp in x[1:-1]:
        eval(exp, env)
    return TailCall(x[-1], env)


def eval_try(x: Exp, env: Env) -> Any:
    """
    Evaluate a try expression.

    Args:
        x (Exp): The expression (try exp handler).
        env (Env): The environment.

    Returns:
        Any: The result of the expression or the handler.
    """
    (_, exp, handler) = x
    try:
        return eval(exp, env)
    except Exception as e:
        proc = eval(handler, env)
        if isinstance(proc, Procedure):
            return TailCall(proc.exp, Env(proc.parms, [e], proc.env))
        else:
            return proc(e)


def eval_dynamic_let(x: Exp, env: Env) -> Any:
    """
    Evaluate a dynamic-let expression.

    Args:
        x (Exp): The expression (dynamic-let ((var val)...) body...).
        env (Env): The environment.

    Returns:
        Any: The result of the body evaluation.
    """
    (_, bindings, *body) = x
    vars_list = [b[0] for b in bindings]
    exps = [b[1] for b in bindings]
    vals = [eval(e, env) for e in exps]

    old_vals = []
    # Save old values
    for v in vars_list:
        target_env = env.find(v)
        old_vals.append((target_env, v, target_env[v]))

    # Apply new values
    for i, v in enumerate(vars_list):
        target_env = env.find(v)
        target_env[v] = vals[i]

    try:
        result = None
        for expr in body:
            result = eval(expr, env)
        return result
    finally:
        # Restore old values
        for target_env, v, old_val in old_vals:
            target_env[v] = old_val


SPECIAL_FORMS = {
    _quote: eval_quote,
    _if: eval_if,
    _set: eval_set,
    _define: eval_define,
    _lambda: eval_lambda,
    _begin: eval_begin,
    _try: eval_try,
    _dynamic_let: eval_dynamic_let,
}


def eval(x: Exp, env: Optional[Env] = None) -> Any:
    """
    Evaluate an expression in an environment.

    This is the core evaluation loop. It handles variable lookups, constant literals,
    special forms (quote, if, set!, define, lambda, begin), and procedure calls.
    It implements Tail Call Optimization (TCO) by using a loop for tail calls.

    Args:
        x (Exp): The expression to evaluate.
        env (Optional[Env]): The environment to evaluate in. Defaults to global_env.

    Returns:
        Any: The result of the evaluation.
    """
    if env is None:
        env = global_env

    while True:
        if isinstance(x, Symbol):       # variable reference
            return env.find(x)[x]
        elif not isinstance(x, list):   # constant literal
            return x

        op = x[0]
        if isinstance(op, Symbol) and op in SPECIAL_FORMS:
            res = SPECIAL_FORMS[op](x, env)
            if isinstance(res, TailCall):
                x, env = res.x, res.env
                continue
            return res
        else:                           # (proc exp*)
            exps = [eval(exp, env) for exp in x]
            proc = exps.pop(0)
            if isinstance(proc, Procedure):
                proc.check_types(exps)
                x = proc.exp
                env = Env(proc.parms, exps, proc.env)
            else:
                return proc(*exps)
