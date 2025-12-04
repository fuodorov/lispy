import io
import sys
from typing import Optional, TextIO, Union

from .errors import LispyError
from .evaluator import eval
from .macros import expand
from .messages import GOODBYE, PROMPT, WELCOME
from .parser import InPort, read, to_string
from .types import EOF_OBJECT, Exp


def parse(inport: Union[str, InPort]) -> Exp:
    """
    Parse a program: read and expand/error-check it.

    Args:
        inport (Union[str, InPort]): The input string or port to read from.

    Returns:
        Exp: The parsed and expanded expression.
    """
    if isinstance(inport, str):
        inport = InPort(io.StringIO(inport))
    return expand(read(inport), toplevel=True)


def load(filename: str) -> None:
    """
    Eval every expression from a file.

    Args:
        filename (str): The path to the file to load.
    """
    repl(None, InPort(open(filename)), None)


def repl(prompt: str = PROMPT, inport: Optional[InPort] = None, out: Optional[TextIO] = sys.stdout) -> None:
    """
    A prompt-read-eval-print loop.

    Args:
        prompt (str, optional): The prompt string. Defaults to 'lispy> '.
        inport (Optional[InPort], optional): The input port. Defaults to None (stdin).
        out (Optional[TextIO], optional): The output stream. Defaults to sys.stdout.
    """
    if inport is None:
        inport = InPort(sys.stdin)
    # Informational messages to the same stream as prompt/output for consistency
    if out:
        out.write(WELCOME + '\n')
    while True:
        try:
            if prompt and out:
                out.write(prompt)
                out.flush()
            x = parse(inport)
            if x is EOF_OBJECT:
                sys.stderr.write(GOODBYE + '\n')
                return
            val = eval(x)
            if val is not None and out:
                print(to_string(val), file=out)
        except LispyError as e:
            print('%s: %s' % (type(e).__name__, e), file=sys.stderr)
        except Exception as e:
            print('%s: %s' % (type(e).__name__, e), file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        load(sys.argv[1])
    else:
        repl()
