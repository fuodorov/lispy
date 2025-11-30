import re
import io
from typing import Optional, TextIO, Union
from .types import Symbol, Exp, Atom, EOF_OBJECT, QUOTES, get_symbol

class InPort:
    """An input port. Retains a line of chars."""
    tokenizer = r'''\s*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)'''

    def __init__(self, file: TextIO) -> None:
        self.file = file
        self.line = ''

    def next_token(self) -> Optional[str]:
        """Return the next token, reading new text into line buffer if needed."""
        while True:
            if self.line == '':
                self.line = self.file.readline()
            if self.line == '':
                return EOF_OBJECT
            token, self.line = re.match(InPort.tokenizer, self.line).groups()
            if token != '' and not token.startswith(';'):
                return token

def readchar(inport: InPort) -> str:
    """Read the next character from an input port."""
    if inport.line != '':
        ch, inport.line = inport.line[0], inport.line[1:]
        return ch
    else:
        return inport.file.read(1) or EOF_OBJECT

def read(inport: InPort) -> Exp:
    """Read a Scheme expression from an input port."""
    def read_ahead(token: str) -> Exp:
        if '(' == token:
            L = []
            while True:
                token = inport.next_token()
                if token == ')':
                    return L
                else:
                    L.append(read_ahead(token))
        elif ')' == token:
            raise SyntaxError('unexpected )')
        elif token in QUOTES:
            return [QUOTES[token], read(inport)]
        elif token is EOF_OBJECT:
            raise SyntaxError('unexpected EOF in list')
        else:
            return atom(token)

    token1 = inport.next_token()
    return EOF_OBJECT if token1 is EOF_OBJECT else read_ahead(token1)

def atom(token: str) -> Atom:
    """Numbers become numbers; #t and #f are booleans; "..." string; otherwise Symbol."""
    if token == '#t':
        return True
    elif token == '#f':
        return False
    elif token[0] == '"':
        return token[1:-1].encode('utf-8').decode('unicode_escape')
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            try:
                return complex(token.replace('i', 'j', 1))
            except ValueError:
                return get_symbol(token)

def to_string(x: Exp) -> str:
    """Convert a Python object back into a Lisp-readable string."""
    if x is True:
        return "#t"
    elif x is False:
        return "#f"
    elif isinstance(x, Symbol):
        return x
    elif isinstance(x, str):
        return '"%s"' % x.encode('unicode_escape').decode('utf-8').replace('"', r'\"')
    elif isinstance(x, list):
        return '(' + ' '.join(map(to_string, x)) + ')'
    elif isinstance(x, complex):
        return str(x).replace('j', 'i')
    else:
        return str(x)
