import lispy


def test_try_success():
    res = lispy.eval(lispy.parse("(try (+ 1 2) (lambda (e) 0))"))
    assert res == 3


def test_try_catch_div_zero():
    res = lispy.eval(lispy.parse('(try (/ 1 0) (lambda (e) "caught"))'))
    assert res == "caught"


def test_try_catch_exception_object():
    res = lispy.eval(lispy.parse('(try (/ 1 0) (lambda (e) e))'))
    assert isinstance(res, ZeroDivisionError)


def test_try_catch_custom_error():
    # Trigger a TypeError by passing wrong args to +
    res = lispy.eval(lispy.parse('(try (+ 1 "a") (lambda (e) "type error"))'))
    assert res == "type error"


def test_raise_catch():
    res = lispy.eval(lispy.parse('(try (raise "my error") (lambda (e) (str e)))'))
    assert "my error" in str(res)
