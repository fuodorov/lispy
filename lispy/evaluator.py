from typing import Any, List, Optional

from .env import Env, global_env
from .types import Exp, Symbol, _begin, _define, _if, _lambda, _quote, _set, _try


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
        self.parms, self.exp, self.env = parms, exp, env

    def __call__(self, *args: Exp) -> Any:
        """
        Call the procedure with the given arguments.

        Args:
            *args (Exp): The arguments to pass to the procedure.

        Returns:
            Any: The result of evaluating the procedure body.
        """
        return eval(self.exp, Env(self.parms, args, self.env))


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
        if op is _quote:                # (quote exp)
            return x[1]
        elif op is _if:                 # (if test conseq alt)
            (_, test, conseq, alt) = x
            x = (conseq if eval(test, env) else alt)
        elif op is _set:                # (set! var exp)
            (_, var, exp) = x
            env.find(var)[var] = eval(exp, env)
            return None
        elif op is _define:             # (define var exp)
            (_, var, exp) = x
            env[var] = eval(exp, env)
            return None
        elif op is _lambda:             # (lambda (var*) exp)
            (_, vars, exp) = x
            return Procedure(vars, exp, env)
        elif op is _begin:              # (begin exp+)
            for exp in x[1:-1]:
                eval(exp, env)
            x = x[-1]
        elif op is _try:                # (try exp handler)
            (_, exp, handler) = x
            try:
                return eval(exp, env)
            except Exception as e:
                proc = eval(handler, env)
                if isinstance(proc, Procedure):
                    x = proc.exp
                    env = Env(proc.parms, [e], proc.env)
                else:
                    return proc(e)
        else:                           # (proc exp*)
            exps = [eval(exp, env) for exp in x]
            proc = exps.pop(0)
            if isinstance(proc, Procedure):
                x = proc.exp
                env = Env(proc.parms, exps, proc.env)
            else:
                return proc(*exps)
