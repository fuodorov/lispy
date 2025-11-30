from typing import Any, Dict, List, Union

Symbol = str
Number = Union[int, float]
Atom = Union[Symbol, Number]
ListType = List[Any]
Exp = Union[Atom, ListType]
EnvType = Dict[str, Any]


class Symbol(str):
    """A Scheme Symbol."""
    pass


def get_symbol(s: str, symbol_table: Dict[str, Symbol] = {}) -> Symbol:
    """Find or create unique Symbol entry for str s in symbol table."""
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

EOF_OBJECT = get_symbol('#<eof-object>')

QUOTES = {
    "'": _quote,
    "`": _quasiquote,
    ",": _unquote,
    ",@": _unquotesplicing
}
