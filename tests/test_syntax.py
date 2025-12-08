import re

import pytest

from lispy.errors import SchemeSyntaxError
from lispy.messages import (
    ERR_CANT_SPLICE,
    ERR_DEFINE_MACRO_TOPLEVEL,
    ERR_DEFINE_SYMBOL,
    ERR_ILLEGAL_BINDING,
    ERR_ILLEGAL_LAMBDA,
    ERR_WRONG_LENGTH,
)
from tests.utils import run


def test_quote():
    assert run("(quote x)") == "x"
    assert run("'x") == "x"


def test_quasiquote():
    run("(define L (list 1 2 3))")
    assert run("`(testing ,@L testing)") == ["testing", 1, 2, 3, "testing"]
    assert run("`(testing ,L testing)") == ["testing", [1, 2, 3], "testing"]


def test_comments():
    code = """'(1 ;test comments '
     ;skip this line
     2 ; more ; comments ; ) )
     3)"""
    assert run(code) == [1, 2, 3]


def test_syntax_errors():
    with pytest.raises(SchemeSyntaxError, match=ERR_WRONG_LENGTH):
        run("()")
    with pytest.raises(SchemeSyntaxError, match=ERR_WRONG_LENGTH):
        run("(set! x)")
    with pytest.raises(SchemeSyntaxError, match=ERR_DEFINE_SYMBOL.format("3")):
        run("(define 3 4)")
    with pytest.raises(SchemeSyntaxError, match=ERR_WRONG_LENGTH):
        run("(quote 1 2)")
    with pytest.raises(SchemeSyntaxError, match=ERR_WRONG_LENGTH):
        run("(if 1 2 3 4)")
    with pytest.raises(SchemeSyntaxError, match=ERR_ILLEGAL_LAMBDA.format("3")):
        run("(lambda 3 3)")
    with pytest.raises(SchemeSyntaxError, match=ERR_WRONG_LENGTH):
        run("(lambda (x))")
    with pytest.raises(SchemeSyntaxError, match=ERR_DEFINE_MACRO_TOPLEVEL):
        run("""(if (= 1 2) (define-macro a 'a)
    (define-macro a 'b))""")
    with pytest.raises(SchemeSyntaxError, match=re.escape(ERR_ILLEGAL_BINDING.format("(b 2 3)"))):
        run("(let ((a 1) (b 2 3)) (+ a b))")
    with pytest.raises(SchemeSyntaxError, match=ERR_CANT_SPLICE):
        run("`,@L")
