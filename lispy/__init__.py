from .env import Env, global_env  # noqa: F401
from .evaluator import Procedure, eval  # noqa: F401
from .parser import InPort, read, to_string  # noqa: F401
from .primitives import add_globals
from .repl import load, parse, repl  # noqa: F401
from .types import EOF_OBJECT, Atom, Exp, Symbol  # noqa: F401

# Initialize globals
add_globals(global_env)

# Initialize standard macros
eval(parse("""(begin
(define-macro and (lambda args
   (if (null? args) #t
       (if (= (length args) 1) (car args)
           `(if ,(car args) (and ,@(cdr args)) #f)))))
)"""))
