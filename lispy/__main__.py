import sys
from .repl import load, repl

if __name__ == "__main__":
    if len(sys.argv) > 1:
        load(sys.argv[1])
    else:
        repl(out=sys.stdout)
