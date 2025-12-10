
import pytest
import re
from tests.utils import run
from lispy.errors import SchemeSyntaxError
from lispy.messages import ERR_ILLEGAL_BINDING, ERR_WRONG_LENGTH


def test_do_simple():
    # Sum 0 to 4
    code = """
    (do ((idx 0 (+ idx 1))
         (sum 0 (+ sum idx)))
        ((= idx 5) sum))
    """
    assert run(code) == 10


def test_do_no_step():
    # x stays 10
    code = """
    (do ((idx 0 (+ idx 1))
         (x 10))
        ((= idx 3) x))
    """
    assert run(code) == 10


def test_do_commands():
    # Side effects
    code = """
    (let ((acc 0))
      (do ((idx 0 (+ idx 1)))
          ((= idx 3) acc)
        (set! acc (+ acc idx))))
    """
    assert run(code) == 3  # 0 + 1 + 2


def test_do_multiple_results():
    code = """
    (do ((idx 0 (+ idx 1)))
        ((= idx 3) "ignored" idx))
    """
    assert run(code) == 3


def test_do_no_results():
    code = """
    (do ((idx 0 (+ idx 1)))
        ((= idx 3)))
    """
    assert run(code) is None


def test_do_nested():
    code = """
    (do ((idx 0 (+ idx 1))
         (sum 0))
        ((= idx 3) sum)
      (do ((k 0 (+ k 1)))
          ((= k 3))
        (set! sum (+ sum 1))))
    """
    # Outer loop runs 3 times (idx=0,1,2).
    # Inner loop runs 3 times (k=0,1,2).
    # Total increments: 3 * 3 = 9
    assert run(code) == 9


def test_do_errors():
    # Missing test
    with pytest.raises(SchemeSyntaxError, match=ERR_WRONG_LENGTH):
        run("(do ((idx 0 (+ idx 1))))")

    # Invalid binding (not a list)
    # Here bindings is (idx 0 (+ idx 1)), so the first element 'idx' is not a list.
    with pytest.raises(SchemeSyntaxError, match=re.escape(ERR_ILLEGAL_BINDING.format("idx"))):
        run("(do (idx 0 (+ idx 1)) ((= idx 5) idx))")

    # Invalid binding element (too many elements)
    with pytest.raises(SchemeSyntaxError, match=re.escape(ERR_ILLEGAL_BINDING.format("(idx 0 (+ idx 1) extra)"))):
        run("(do ((idx 0 (+ idx 1) extra)) ((= idx 5) idx))")
