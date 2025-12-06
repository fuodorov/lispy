import pytest

from lispy.errors import ArgumentError
from tests.utils import run


def test_define_set():
    run("(define x 3)")
    assert run("x") == 3
    assert run("(+ x x)") == 6


def test_lambda_simple():
    assert run("((lambda (x) (+ x x)) 5)") == 10
    run("(define twice (lambda (x) (* 2 x)))")
    assert run("(twice 5)") == 10


def test_lambda_variadic():
    run("(define lyst (lambda items items))")
    assert run("(lyst 1 2 3 (+ 2 2))") == [1, 2, 3, 4]


def test_lambda_errors():
    run("(define (twice x) (* 2 x))")
    with pytest.raises(ArgumentError):
        run("(twice 2 2)")


def test_closures():
    run("(define compose (lambda (f g) (lambda (x) (f (g x)))))")
    run("(define twice (lambda (x) (* 2 x)))")
    assert run("((compose list twice) 5)") == [10]

    run("(define repeat (lambda (f) (compose f f)))")
    assert run("((repeat twice) 5)") == 20
    assert run("((repeat (repeat twice)) 5)") == 80


def test_mutable_closure():
    run("(define ((account bal) amt) (set! bal (+ bal amt)) bal)")
    run("(define a1 (account 100))")
    assert run("(a1 0)") == 100
    assert run("(a1 10)") == 110
    assert run("(a1 10)") == 120


def test_let():
    assert run("(let ((a 1) (b 2)) (+ a b))") == 3
