import sys
import io
from typing import Optional, TextIO, Union
from .types import Exp, EOF_OBJECT
from .parser import InPort, read, to_string
from .evaluator import eval
from .macros import expand

def parse(inport: Union[str, InPort]) -> Exp:
    """Parse a program: read and expand/error-check it."""
    if isinstance(inport, str):
        inport = InPort(io.StringIO(inport))
    return expand(read(inport), toplevel=True)

def load(filename: str) -> None:
    """Eval every expression from a file."""
    repl(None, InPort(open(filename)), None)

def repl(prompt: str = 'lispy> ', inport: Optional[InPort] = None, out: Optional[TextIO] = sys.stdout) -> None:
    """A prompt-read-eval-print loop."""
    if inport is None:
        inport = InPort(sys.stdin)
    sys.stderr.write("Lispy version 2.0\n")
    while True:
        try:
            if prompt:
                sys.stderr.write(prompt)
                sys.stderr.flush()
            x = parse(inport)
            if x is EOF_OBJECT:
                return
            val = eval(x)
            if val is not None and out:
                print(to_string(val), file=out)
        except Exception as e:
            print('%s: %s' % (type(e).__name__, e))
