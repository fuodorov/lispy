from typing import Any, Dict, List, Union

from .constants import QUASIQUOTE_CHAR, QUOTE_CHAR, UNQUOTE_CHAR, UNQUOTE_SPLICING_CHAR

Number = Union[int, float]
Atom = Union[str, Number]
ListType = List[Any]
Exp = Union[Atom, ListType]
EnvType = Dict[str, Any]


class Symbol(str):
    """
    A Scheme Symbol.

    This class inherits from `str` and is used to represent Scheme symbols
    in the Python environment.
    """
    pass


_symbol_table: Dict[str, Symbol] = {}


def get_symbol(s: str, symbol_table: Dict[str, Symbol] = _symbol_table) -> Symbol:
    """
    Find or create a unique Symbol entry for the string `s` in the symbol table.

    Args:
        s (str): The string representation of the symbol.
        symbol_table (Dict[str, Symbol], optional): The symbol table to use.
            Defaults to the module-level symbol table.

    Returns:
        Symbol: The unique Symbol instance corresponding to `s`.
    """
    if s not in symbol_table:
        symbol_table[s] = Symbol(s)
    return symbol_table[s]


# Global symbols
_quote = get_symbol('quote')
_if = get_symbol('if')
_set = get_symbol('set!')
_define = get_symbol('define')
_lambda = get_symbol('lambda')
_begin = get_symbol('begin')
_definemacro = get_symbol('define-macro')
_quasiquote = get_symbol('quasiquote')
_unquote = get_symbol('unquote')
_unquotesplicing = get_symbol('unquote-splicing')
_append = get_symbol('append')
_cons = get_symbol('cons')
_let = get_symbol('let')
_try = get_symbol('try')
_dynamic_let = get_symbol('dynamic-let')

EOF_OBJECT = get_symbol('#<eof-object>')

QUOTES = {
    QUOTE_CHAR: _quote,
    QUASIQUOTE_CHAR: _quasiquote,
    UNQUOTE_CHAR: _unquote,
    UNQUOTE_SPLICING_CHAR: _unquotesplicing
}
