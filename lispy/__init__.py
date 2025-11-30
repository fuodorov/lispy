from .types import Symbol, EOF_OBJECT, Exp, Atom
from .parser import InPort, to_string, read
from .env import global_env, Env
from .evaluator import eval, Procedure
from .repl import repl, parse, load
from .primitives import add_globals

# Initialize globals
add_globals(global_env)

# Initialize standard macros
eval(parse("""(begin
(define-macro and (lambda args 
   (if (null? args) #t
       (if (= (length args) 1) (car args)
           `(if ,(car args) (and ,@(cdr args)) #f)))))
)"""))
