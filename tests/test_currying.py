import pytest

from lispy.errors import ArgumentError, UserError
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
    # Should propagate error from inside promise ONLY when called
    code = """
    (begin
        (define p (delay (raise "oops")))
        (define c (curry p))
        (c 1)
    )
    """
    with pytest.raises(UserError, match="oops"):
        run(code)


def test_curry_lazy_behavior():
    # Ensure side effects happen only when curried function is called
    code = """
    (begin
        (define side-effect 0)
        (define (my-add x y) (+ x y))
        (define p (delay (begin (set! side-effect 1) my-add)))
        
        (define c (curry p))
        
        (if (= side-effect 1)
            "Eager"
            (begin
                (c 1 2)
                (if (= side-effect 1)
                    "Lazy"
                    "Broken")))
    )
    """
    assert run(code) == "Lazy"

