"""
Parser module.

This module handles the tokenization and parsing of Scheme source code into
Abstract Syntax Trees (ASTs).
"""
import re
from functools import singledispatch
from typing import Any, Optional, TextIO

from .constants import (
    COMMENT_CHAR,
    COMPLEX_IMAG_CHAR_PYTHON,
    COMPLEX_IMAG_CHAR_SCHEME,
    FALSE_LITERAL,
    LPAREN,
    READ_CHUNK_SIZE,
    RPAREN,
    STRING_QUOTE,
    TOKENIZER_REGEX,
    TRUE_LITERAL,
)
from .errors import ParseError
from .types import EOF_OBJECT, QUOTES, Atom, Exp, Symbol, get_symbol


class InPort:
    """
    An input port. Retains a line of chars.

    Attributes:
        file (TextIO): The file object to read from.
        line (str): The current line buffer.
    """
    tokenizer = TOKENIZER_REGEX

    def __init__(self, file: TextIO) -> None:
        """
        Initialize the InPort.

        Args:
            file (TextIO): The file-like object to read from.
        """
        self.file = file
        self.line = ''

    def next_token(self) -> Optional[str]:
        """
        Return the next token, reading new text into line buffer if needed.

        Returns:
            Optional[str]: The next token string, or EOF_OBJECT if end of file.
        """
        while True:
            if self.line == '':
                self.line = self.file.readline()
            if self.line == '':
                return EOF_OBJECT
            token, self.line = re.match(InPort.tokenizer, self.line).groups()
            if token != '' and not token.startswith(COMMENT_CHAR):
                return token


def readchar(inport: InPort) -> str:
    """
    Read the next character from an input port.

    Args:
        inport (InPort): The input port to read from.

    Returns:
        str: The next character, or EOF_OBJECT.
    """
    if inport.line != '':
        ch, inport.line = inport.line[0], inport.line[1:]
        return ch
    else:
        return inport.file.read(READ_CHUNK_SIZE) or EOF_OBJECT


def read(inport: InPort) -> Exp:
    """
    Read a Scheme expression from an input port.

    Args:
        inport (InPort): The input port to read from.

    Returns:
        Exp: The parsed Scheme expression (Atom or List).

    Raises:
        ParseError: If the syntax is invalid (e.g., unexpected EOF or parenthesis).
    """
    def read_ahead(token: str) -> Exp:
        """
        Helper function to read ahead recursively.

        Args:
            token (str): The current token.

        Returns:
            Exp: The parsed expression.
        """
        if LPAREN == token:
            L = []
            while True:
                token = inport.next_token()
                if token == RPAREN:
                    return L
                else:
                    L.append(read_ahead(token))
        elif RPAREN == token:
            raise ParseError('unexpected )')
        elif token in QUOTES:
            return [QUOTES[token], read(inport)]
        elif token is EOF_OBJECT:
            raise ParseError('unexpected EOF in list')
        else:
            return atom(token)

    token1 = inport.next_token()
    return EOF_OBJECT if token1 is EOF_OBJECT else read_ahead(token1)


def atom(token: str) -> Atom:
    """
    Convert a token into an Atom.

    Numbers become numbers; #t and #f are booleans; "..." string; otherwise Symbol.

    Args:
        token (str): The token string to convert.

    Returns:
        Atom: The corresponding atomic value (int, float, complex, str, bool, or Symbol).
    """
    if token == TRUE_LITERAL:
        return True
    elif token == FALSE_LITERAL:
        return False
    elif token.startswith(STRING_QUOTE):
        return token[1:-1].encode('utf-8').decode('unicode_escape')

    for converter in [int, float, lambda t: complex(t.replace(COMPLEX_IMAG_CHAR_SCHEME, COMPLEX_IMAG_CHAR_PYTHON, 1))]:
        try:
            return converter(token)
        except ValueError:
            continue

    return get_symbol(token)


@singledispatch
def to_string(x: Any) -> str:
    """
    Convert a Python object back into a Lisp-readable string.

    Args:
        x (Any): The expression to convert.

    Returns:
        str: The string representation of the expression.
    """
    return str(x)


@to_string.register
def _(x: bool) -> str:
    return TRUE_LITERAL if x else FALSE_LITERAL


@to_string.register
def _(x: Symbol) -> str:
    return x


@to_string.register
def _(x: str) -> str:
    return '"%s"' % x.encode('unicode_escape').decode('utf-8').replace('"', r'\"')


@to_string.register
def _(x: list) -> str:
    return LPAREN + ' '.join(map(to_string, x)) + RPAREN


@to_string.register
def _(x: complex) -> str:
    return str(x).replace(COMPLEX_IMAG_CHAR_PYTHON, COMPLEX_IMAG_CHAR_SCHEME)
