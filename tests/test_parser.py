import io

import pytest

from lispy import errors, parser, types
from lispy.constants import FALSE_LITERAL, LPAREN, QUOTE_CHAR, RPAREN, TRUE_LITERAL


def test_atom_numbers():
    assert parser.atom("1") == 1
    assert parser.atom("-10") == -10
    assert parser.atom("3.14") == 3.14
    assert parser.atom("-2.5e10") == -2.5e10


def test_atom_booleans():
    assert parser.atom(TRUE_LITERAL) is True
    assert parser.atom(FALSE_LITERAL) is False


def test_atom_strings():
    assert parser.atom('"hello"') == "hello"
    assert parser.atom('"foo bar"') == "foo bar"
    assert parser.atom('"escaped \\"quote\\""') == 'escaped "quote"'


def test_atom_symbols():
    s = parser.atom("abc")
    assert isinstance(s, types.Symbol)
    assert s == "abc"
    assert parser.atom("+") == "+"


def test_tokenizer_simple():
    inp = parser.InPort(io.StringIO("(+ 1 2)"))
    tokens = []
    while True:
        token = inp.next_token()
        if token is types.EOF_OBJECT:
            break
        tokens.append(token)
    assert tokens == [LPAREN, '+', '1', '2', RPAREN]


def test_tokenizer_quotes():
    inp = parser.InPort(io.StringIO("'(1 2)"))
    tokens = []
    while True:
        token = inp.next_token()
        if token is types.EOF_OBJECT:
            break
        tokens.append(token)
    assert tokens == [QUOTE_CHAR, LPAREN, '1', '2', RPAREN]


def test_read_simple_list():
    inp = parser.InPort(io.StringIO("(+ 1 2)"))
    exp = parser.read(inp)
    assert exp == [types.get_symbol("+"), 1, 2]


def test_read_nested_list():
    inp = parser.InPort(io.StringIO("(+ 1 (* 2 3))"))
    exp = parser.read(inp)
    assert exp == [types.get_symbol("+"), 1, [types.get_symbol("*"), 2, 3]]


def test_read_quotes():
    inp = parser.InPort(io.StringIO("'x"))
    exp = parser.read(inp)
    assert exp == [types._quote, types.get_symbol("x")]


def test_to_string():
    assert parser.to_string(1) == "1"
    assert parser.to_string(True) == TRUE_LITERAL
    assert parser.to_string(False) == FALSE_LITERAL
    assert parser.to_string("hello") == '"hello"'
    assert parser.to_string(types.get_symbol("x")) == "x"
    assert parser.to_string([types.get_symbol("+"), 1, 2]) == "(+ 1 2)"


def test_read_error_unexpected_eof():
    inp = parser.InPort(io.StringIO("("))
    with pytest.raises(errors.ParseError):
        parser.read(inp)


def test_read_error_unexpected_paren():
    inp = parser.InPort(io.StringIO(")"))
    with pytest.raises(errors.ParseError):
        parser.read(inp)
