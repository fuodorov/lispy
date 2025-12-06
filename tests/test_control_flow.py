from tests.utils import run


def test_if():
    assert run("(if 1 2)") == 2
    assert run("(if (= 3 4) 2)") is None


def test_begin():
    assert run("(begin (define x 1) (set! x (+ x 1)) (+ x 1))") == 3


def test_callcc():
    assert run("(call/cc (lambda (throw) (+ 5 (* 10 (throw 1)))))") == 1
    assert run("(call/cc (lambda (throw) (+ 5 (* 10 1))))") == 15
    assert run(
        "(call/cc (lambda (throw) \n         (+ 5 (* 10 (call/cc (lambda (escape) (* 100 (escape 3))))))))"
    ) == 35
    assert run(
        "(call/cc (lambda (throw) \n         (+ 5 (* 10 (call/cc (lambda (escape) (* 100 (throw 3))))))))"
    ) == 3
    assert run(
        "(call/cc (lambda (throw) \n         (+ 5 (* 10 (call/cc (lambda (escape) (* 100 1)))))))"
    ) == 1005


def test_and_or():
    assert run("(and 1 2 3)") == 3
    assert run("(and (> 2 1) 2 3)") == 3
    assert run("(and)") is True
    assert run("(and (> 2 1) (> 2 3))") is False

    assert run("(or 1 2 3)") == 1
    assert run("(or (> 2 1) 2 3)") is True
    assert run("(or)") is False
    assert run("(or (> 2 3) (> 2 1))") is True
    assert run("(or #f #f)") is False


def test_unless_macro():
    run("""(define-macro unless (lambda args `(if (not ,(car args)) (begin ,@(cdr args)))))""")
    assert run("(unless (= 2 (+ 1 1)) (display 2) 3 4)") is None
    # Note: display prints to stdout, we just check return value
    assert run("(unless (= 4 (+ 1 1)) (display 2) (display \"\\n\") 3 4)") == 4
