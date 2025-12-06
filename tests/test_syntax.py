import pytest

from lispy.errors import SchemeSyntaxError
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
    with pytest.raises(SchemeSyntaxError, match="wrong length"):
        run("()")
    with pytest.raises(SchemeSyntaxError, match="wrong length"):
        run("(set! x)")
    with pytest.raises(SchemeSyntaxError, match="can define only a symbol"):
        run("(define 3 4)")
    with pytest.raises(SchemeSyntaxError, match="wrong length"):
        run("(quote 1 2)")
    with pytest.raises(SchemeSyntaxError, match="wrong length"):
        run("(if 1 2 3 4)")
    with pytest.raises(SchemeSyntaxError, match="illegal lambda argument list"):
        run("(lambda 3 3)")
    with pytest.raises(SchemeSyntaxError, match="wrong length"):
        run("(lambda (x))")
    with pytest.raises(SchemeSyntaxError, match="define-macro only allowed at top level"):
        run("""(if (= 1 2) (define-macro a 'a)
    (define-macro a 'b))""")
    with pytest.raises(SchemeSyntaxError, match="illegal binding list"):
        run("(let ((a 1) (b 2 3)) (+ a b))")
    with pytest.raises(SchemeSyntaxError, match="can't splice here"):
        run("`,@L")
