"""
Lispy: A simple Lisp interpreter in Python.

This package provides a complete Lisp interpreter with support for:
- Basic Scheme primitives
- Macros (define-macro)
- Tail call optimization (via Python's stack, limited)
- REPL
- File loading

Usage:
    >>> import lispy
    >>> lispy.repl()
"""
from .env import Env, global_env  # noqa: F401
from .evaluator import Procedure, eval  # noqa: F401
from .parser import InPort, read, to_string  # noqa: F401
from .primitives import add_globals
from .repl import load, parse, repl  # noqa: F401
from .types import EOF_OBJECT, Atom, Exp, Symbol  # noqa: F401

# Initialize the global environment with standard procedures
add_globals(global_env)

# Define 'and' macro in the global environment
eval(parse("""(begin
(define-macro and (lambda args
   (if (null? args) #t
       (if (= (length args) 1) (car args)
           `(if ,(car args) (and ,@(cdr args)) #f)))))
)"""))

# Define 'or' macro in the global environment
eval(parse("""(begin
(define-macro or (lambda args
   (if (null? args) #f
       (if (= (length args) 1) (car args)
           `(let ((__or_temp__ ,(car args)))
              (if __or_temp__ __or_temp__ (or ,@(cdr args))))))))
)"""))
