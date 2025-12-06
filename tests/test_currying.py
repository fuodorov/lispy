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
