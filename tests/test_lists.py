from tests.utils import run


def test_list_basics():
    run("(define L (list 1 2 3))")
    assert run("L") == [1, 2, 3]
    assert run("(quote (1 2 three))") == [1, 2, "three"]
    assert run("'(one 2 3)") == ["one", 2, 3]


def test_combine_zip():
    run("""(define combine (lambda (f)
    (lambda (x y)
      (if (null? x) (quote ())
          (f (list (car x) (car y))
             ((combine f) (cdr x) (cdr y)))))))""")
    run("(define zip (combine cons))")
    assert run("(zip (list 1 2 3 4) (list 5 6 7 8))") == [[1, 5], [2, 6], [3, 7], [4, 8]]


def test_riff_shuffle():
    # Dependencies
    run("""(define combine (lambda (f)
    (lambda (x y)
      (if (null? x) (quote ())
          (f (list (car x) (car y))
             ((combine f) (cdr x) (cdr y)))))))""")

    run("""(define riff-shuffle (lambda (deck) (begin
    (define take (lambda (n seq) (if (<= n 0) (quote ()) (cons (car seq) (take (- n 1) (cdr seq))))))
    (define drop (lambda (n seq) (if (<= n 0) seq (drop (- n 1) (cdr seq)))))
    (define mid (lambda (seq) (/ (length seq) 2)))
    ((combine append) (take (mid deck) deck) (drop (mid deck) deck)))))""")

    # Helper for repeat
    run("(define compose (lambda (f g) (lambda (x) (f (g x)))))")
    run("(define repeat (lambda (f) (compose f f)))")

    assert run("(riff-shuffle (list 1 2 3 4 5 6 7 8))") == [1, 5, 2, 6, 3, 7, 4, 8]
    assert run("((repeat riff-shuffle) (list 1 2 3 4 5 6 7 8))") == [1, 3, 5, 7, 2, 4, 6, 8]
    assert run(
        "(riff-shuffle (riff-shuffle (riff-shuffle (list 1 2 3 4 5 6 7 8))))"
    ) == [1, 2, 3, 4, 5, 6, 7, 8]
