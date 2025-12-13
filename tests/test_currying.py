import pytest

from lispy.errors import UserError
from tests.utils import run


def test_curry_simple():
    code = """
    (begin
        (define (add x y) (+ x y))
        (define add-c (curry add))
        (define add-5 (add-c 5))
        (add-5 10)
    )
    """
    assert run(code) == 15


def test_curry_immediate():
    code = """
    (begin
        (define (add x y z) (+ x y z))
        (define add-c (curry add))
        (((add-c 1) 2) 3)
    )
    """
    assert run(code) == 6


def test_curry_mixed():
    code = """
    (begin
        (define (add x y z) (+ x y z))
        (define add-c (curry add))
        ((add-c 1 2) 3)
    )
    """
    assert run(code) == 6


def test_curry_full():
    code = """
    (begin
        (define (add x y) (+ x y))
        (define add-c (curry add))
        (add-c 1 2)
    )
    """
    assert run(code) == 3


def test_curry_promise():
    code = """
    (begin
        (define (add x y) (+ x y))
        (define p (delay add))
        (define add-c (curry p))
        ((add-c 10) 20)
    )
    """
    assert run(code) == 30


def test_curry_nested_promise():
    code = """
    (begin
        (define (mul x y) (* x y))
        (define p (delay (delay mul)))
        (define mul-c (curry p))
        ((mul-c 5) 6)
    )
    """
    assert run(code) == 30


def test_curry_promise_execution_error():
    # Should propagate error from inside promise
    code = """
    (begin
        (define p (delay (raise "oops")))
        (curry p)
    )
    """
    with pytest.raises(UserError, match="oops"):
        run(code)
