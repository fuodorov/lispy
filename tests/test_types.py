import pytest

from lispy.errors import TypeMismatchError, UserError
from tests.utils import run


def test_define_typed():
    run("(define x :: int 10)")
    assert run("x") == 10

    with pytest.raises(TypeMismatchError):
        run("(define y :: int 10.5)")


def test_lambda_typed():
    run("(define f (lambda (x :: int) (+ x 1)))")
    assert run("(f 10)") == 11

    with pytest.raises(TypeMismatchError):
        run("(f 10.5)")


def test_lambda_multi_typed():
    run("(define add (lambda (x :: int y :: int) (+ x y)))")
    assert run("(add 10 20)") == 30

    with pytest.raises(TypeMismatchError):
        run("(add 10 20.5)")


def test_define_func_typed():
    # This relies on macro expansion converting to lambda
    run("(define (g x :: int) (* x 2))")
    assert run("(g 5)") == 10

    with pytest.raises(TypeMismatchError):
        run("(g 5.5)")


def test_mixed_typed():
    run("(define (h x y :: int z) (list x y z))")
    assert run("(h 1 2 3)") == [1, 2, 3]

    with pytest.raises(TypeMismatchError):
        run("(h 1 2.5 3)")


def test_other_types():
    run('(define s :: str "hello")')
    assert run("s") == "hello"

    run("(define b :: bool #t)")
    assert run("b") is True

    run("(define f :: float 3.14)")
    assert run("f") == 3.14

    run("(define l :: list (list 1 2))")
    assert run("l") == [1, 2]


def test_type_mismatches_other_types():
    with pytest.raises(TypeMismatchError):
        run('(define s :: str 123)')

    with pytest.raises(TypeMismatchError):
        # 1 is int, not bool in Scheme view (though python bool is int)
        run("(define b :: bool 1)")

    with pytest.raises(TypeMismatchError):
        run("(define f :: float 10)")  # 10 is int

    with pytest.raises(TypeMismatchError):
        run("(define l :: list 123)")


def test_unknown_type():
    with pytest.raises(UserError, match="Unknown type"):
        run("(define x :: unknown 10)")


def test_bool_int_distinction():
    # Ensure bool is not accepted as int
    with pytest.raises(TypeMismatchError):
        run("(define x :: int #t)")

    # Ensure int is not accepted as bool
    with pytest.raises(TypeMismatchError):
        run("(define x :: bool 1)")
