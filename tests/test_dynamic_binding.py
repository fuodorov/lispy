from tests.utils import run


def test_dynamic_let_global():
    # Define a global variable
    run("(define *x* 10)")

    # Define a function that uses it
    run("(define (read-x) *x*)")

    # Check initial value
    assert run("(read-x)") == 10

    # Use dynamic-let to change it temporarily
    res = run("(dynamic-let ((*x* 20)) (read-x))")
    assert res == 20

    # Check it is restored
    assert run("(read-x)") == 10


def test_dynamic_let_nested():
    run("(define *y* 1)")
    run("(define (read-y) *y*)")

    code = """
    (dynamic-let ((*y* 2))
        (list (read-y)
              (dynamic-let ((*y* 3))
                  (read-y))
              (read-y)))
    """
    res = run(code)
    # Should be (2 3 2)
    # (read-y) -> 2
    # inner (read-y) -> 3
    # (read-y) -> 2

    # Convert python list to check
    assert res == [2, 3, 2]

    # Check restored
    assert run("(read-y)") == 1


def test_dynamic_let_exception():
    run("(define *z* 100)")

    code = """
    (try
        (dynamic-let ((*z* 200))
            (raise "error"))
        (lambda (e) *z*))
    """
    # If dynamic-let restores correctly in finally block,
    # then when we catch the error outside, *z* should be restored to 100?
    # Wait. The catch handler is executed... where?
    # In the environment of the try?
    # The try is outside dynamic-let.
    # So dynamic-let should have finished (abruptly) and restored *z*.

    res = run(code)
    assert res == 100
