from tests.utils import run


def test_delay_force():
    # Simple delay/force
    code = """
    (begin
        (define p (delay (+ 1 2)))
        (force p)
    )
    """
    assert run(code) == 3


def test_memoization():
    # Check that side effects happen only once
    code = """
    (begin
        (define count 0)
        (define p (delay (begin (set! count (+ count 1)) count)))
        (define v1 (force p))
        (define v2 (force p))
        (list v1 v2 count)
    )
    """
    # v1 should be 1, v2 should be 1, count should be 1
    assert run(code) == [1, 1, 1]


def test_infinite_stream():
    # Infinite stream of ones
    # We use (list head promise) structure because cons expects a list as second arg
    code = """
    (begin
        (define ones (list 1 (delay ones)))
        (define (head s) (car s))
        (define (tail s) (force (car (cdr s))))
        (list (head ones)
              (head (tail ones))
              (head (tail (tail ones))))
    )
    """
    assert run(code) == [1, 1, 1]


def test_integers_stream():
    # Stream of integers starting from n
    code = """
    (begin
        (define (integers-from n)
            (list n (delay (integers-from (+ n 1)))))
        (define ints (integers-from 1))
        (define (head s) (car s))
        (define (tail s) (force (car (cdr s))))

        (list (head ints)
              (head (tail ints))
              (head (tail (tail ints))))
    )
    """
    assert run(code) == [1, 2, 3]


def test_nested_promises():
    # Test that force recursively unwraps promises
    code = """
    (begin
        (define p (delay (delay (delay 42))))
        (force p)
    )
    """
    assert run(code) == 42


def test_nested_promises_memoization():
    # Ensure side effects in nested promises happen correctly and are memoized
    code = """
    (begin
        (define count 0)
        (define p (delay 
                    (begin 
                        (set! count (+ count 1)) 
                        (delay 
                            (begin 
                                (set! count (+ count 10)) 
                                count)))))
        (define val1 (force p))
        (define val2 (force p))
        (list val1 val2 count)
    )
    """
    # First force: outer runs (+1), returns inner. Inner runs (+10), returns 11. Total count 11.
    # Second force: outer is memoized (inner promise). Inner is memoized (11). Returns 11.
    # Count should remain 11.
    assert run(code) == [11, 11, 11]


def test_force_non_promise():
    assert run("(force 123)") == 123

