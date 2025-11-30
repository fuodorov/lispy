from typing import List, Optional, Any
from .types import Symbol, Exp, _quote, _if, _set, _define, _lambda, _begin
from .env import Env, global_env

class Procedure:
    """A user-defined Scheme procedure."""
    def __init__(self, parms: List[Symbol], exp: Exp, env: Env) -> None:
        self.parms, self.exp, self.env = parms, exp, env

    def __call__(self, *args: Exp) -> Any:
        return eval(self.exp, Env(self.parms, args, self.env))

def eval(x: Exp, env: Optional[Env] = None) -> Any:
    """Evaluate an expression in an environment."""
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
        else:                           # (proc exp*)
            exps = [eval(exp, env) for exp in x]
            proc = exps.pop(0)
            if isinstance(proc, Procedure):
                x = proc.exp
                env = Env(proc.parms, exps, proc.env)
            else:
                return proc(*exps)
