Architecture and Internals
==========================

The interpreter is built on a modular principle, where each part is responsible for its own stage of code processing. The main work loop is the **REPL** (Read-Eval-Print Loop), implemented in ``repl.py``.

1. Parsing (Read)
-----------------
The ``parser.py`` module is responsible for converting the source text of the program into a data structure understandable by the interpreter (Abstract Syntax Tree, AST).

*   **Tokenization**: First, the string is split into tokens (parentheses, symbols, numbers, strings).
*   **AST Construction**: Tokens are converted into nested Python lists. For example, ``(define x 10)`` becomes ``['define', 'x', 10]``. Atoms (numbers, strings) are converted to their corresponding Python types.

2. Environment
--------------
The ``env.py`` module implements the ``Env`` class, which represents the variable scope.

*   **Structure**: It is a dictionary (``dict``) storing "variable name" - "value" pairs.
*   **Nesting**: Each environment has a reference to its parent (``outer``). When looking up a variable, the interpreter first looks in the current environment, and if not found, goes up the parent chain to the global environment.
*   **Closures**: When a lambda function is created, it "remembers" the environment in which it was created. This allows functions to access variables that were visible at the time of their definition, even if the call happens elsewhere.

3. Macros (Expand)
------------------
Before evaluation, the code goes through a macro expansion stage, implemented in ``macros.py``.

*   **Expand**: The ``expand`` function recursively traverses the AST. If it encounters a macro call (defined via ``define-macro``), it calls the macro transformer function, which returns new code.
*   **Built-in Macros**: Constructs like ``let``, ``and``, ``or`` are implemented as macros that expand into basic forms (``lambda``, ``if``). This simplifies the language core.

4. Evaluation (Eval)
--------------------
The heart of the interpreter is the ``evaluator.py`` module.

*   **Dispatching**: Instead of a long ``if/elif`` chain for handling special forms (``if``, ``define``, ``lambda``, etc.), a dispatch table ``SPECIAL_FORMS`` is used. This is a dictionary where keys are form symbols and values are handler functions. This makes the code cleaner and extensible.
*   **Standard Functions**: If the first element of the list is not a special form, it is considered a function call. Arguments are evaluated, and the corresponding procedure (from ``primitives.py`` or user-defined) is called.

5. Tail Call Optimization (TCO)
-------------------------------
Python has a recursion depth limit, which hinders writing in a functional style. This project implements full TCO support.

*   **Mechanism**: When a function calls another function in a "tail position" (i.e., it is the last action), instead of creating a new Python stack frame, we raise a special exception or return a ``TailCall`` object containing the new function and arguments.
*   **Loop**: In ``evaluator.py``, there is an infinite ``while True`` loop. It catches ``TailCall`` objects and simply updates the current expression and environment, continuing evaluation at the same stack level. This allows infinite recursion (e.g., ``(loop)``) without memory overflow.

6. Error Handling
-----------------
An exception system similar to Python's is implemented, but inside Lisp.

*   **Error Classes**: Error types (``LispyError``, ``SyntaxError``, etc.) are defined in ``errors.py``.
*   **Try/Raise**: The ``try`` special form allows catching errors. If a ``raise`` occurs inside a ``try`` block, control is passed to the handler (catch), which receives the error object.

7. Dynamic Binding
------------------
In addition to lexical (static) binding, dynamic binding is implemented via ``dynamic-let``.

*   This allows temporarily overriding the value of a global variable only for the duration of a specific code block. After exiting the block, the old value is restored. This is useful for configurations and context variables.

8. Lazy Evaluation
------------------
Primitives for delayed evaluation are implemented.

*   **Promise**: A special data type storing an unevaluated expression and (after the first evaluation) its result.
*   **Delay**: The ``(delay exp)`` macro wraps an expression into a ``Promise``.
*   **Force**: The ``(force promise)`` function evaluates the ``Promise`` value on the first access and returns the cached result on subsequent ones (memoization).

9. Currying
-----------
The ``curry`` function allows transforming a function of N arguments into a chain of N functions of one argument.

*   This is useful for partial application of functions and creating new functions based on existing ones.
*   Supported only for user-defined procedures (not for built-in primitives with variable number of arguments).

10. Type System
---------------
A basic runtime type checking system is implemented.

*   **Syntax**: Types are specified via ``::``.
    *   Definitions: ``(define x :: int 10)``
    *   Arguments: ``(lambda (x :: int) ...)``
*   **Supported Types**: ``int``, ``float``, ``str``, ``bool``, ``list``.
*   **Check**: If the passed value does not match the specified type, a ``TypeMismatchError`` exception is thrown.

11. Python Interoperability
---------------------------
Lispy allows using the power of the Python ecosystem directly.

*   **py-import**: Imports a Python module.
*   **py-getattr**: Gets an attribute of an object (function, variable, class).
*   **py-eval**: Evaluates a Python code string and returns the result.
*   **py-exec**: Executes a Python code string (for side effects).
