from tests.utils import run


def test_arithmetic():
    assert run("(+ 2 2)") == 4
    assert run("(+ (* 2 100) (* 1 10))") == 210


def test_comparisons():
    assert run("(if (> 6 5) (+ 1 1) (+ 2 2))") == 2
    assert run("(if (< 6 5) (+ 1 1) (+ 2 2))") == 4


def test_complex_numbers():
    assert run("(* 1i 1i)") == -1 + 0j
    assert run("(sqrt -1)") == 1j


def test_abs():
    run("(define abs (lambda (n) ((if (> n 0) + -) 0 n)))")
    assert run("(list (abs -3) (abs 0) (abs 3))") == [3, 0, 3]


def test_factorial():
    run("(define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))")
    assert run("(fact 3)") == 6
    # Large number might be tricky to assert exactly if it's huge, but python handles large ints
    assert run("(fact 50)") == (
        30414093201713378043612608166064768844377641568960512000000000000
    )


def test_newton_sqrt():
    run("""(define (newton guess function derivative epsilon)
    (define guess2 (- guess (/ (function guess) (derivative guess))))
    (if (< (abs (- guess guess2)) epsilon) guess2
        (newton guess2 function derivative epsilon)))""")

    run("""(define (square-root a)
    (newton 1 (lambda (x) (- (* x x) a)) (lambda (x) (* 2 x)) 1e-8))""")

    assert run("(> (square-root 200.) 14.14213)") is True
    assert run("(< (square-root 200.) 14.14215)") is True
    assert run("(= (square-root 200.) (sqrt 200.))") is True


def test_sum_squares_tco():
    run("""(define (sum-squares-range start end)
         (define (sumsq-acc start end acc)
            (if (> start end) acc (sumsq-acc (+ start 1) end (+ (* start start) acc))))
         (sumsq-acc start end 0))""")
    assert run("(sum-squares-range 1 3000)") == 9004500500
