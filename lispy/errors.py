class LispyError(Exception):
    """
    Base class for all Lispy exceptions.
    """
    pass


class ParseError(LispyError):
    """
    Raised when the parser encounters an error (e.g. unexpected EOF, unexpected parenthesis).
    """
    pass


class SchemeSyntaxError(LispyError):
    """
    Raised when a macro or special form has invalid syntax (e.g. wrong number of arguments to 'if').
    """
    pass


class SymbolNotFoundError(LispyError, LookupError):
    """
    Raised when a symbol is not found in the environment.
    """
    pass


class ArgumentError(LispyError, TypeError):
    """
    Raised when function arguments don't match parameters.
    """
    pass
