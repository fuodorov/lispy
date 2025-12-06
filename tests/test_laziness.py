import lispy


def test_delay_force():
    # Simple delay/force
    code = """
    (begin
        (define p (delay (+ 1 2)))
        (force p)
    )
    """
    assert lispy.eval(lispy.parse(code)) == 3


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
    assert lispy.eval(lispy.parse(code)) == [1, 1, 1]


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
    assert lispy.eval(lispy.parse(code)) == [1, 1, 1]


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
    assert lispy.eval(lispy.parse(code)) == [1, 2, 3]
