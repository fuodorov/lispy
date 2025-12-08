
import math

from tests.utils import run


def test_py_import():
    run("(define math (py-import \"math\"))")
    assert run("(py-getattr math \"pi\")") == math.pi


def test_py_call():
    run("(define os (py-import \"os\"))")
    run("(define getcwd (py-getattr os \"getcwd\"))")
    cwd = run("(getcwd)")
    assert isinstance(cwd, str)
    assert len(cwd) > 0


def test_py_getattr_nested():
    run("(define sys (py-import \"sys\"))")
    # sys.version_info.major
    run("(define v-info (py-getattr sys \"version_info\"))")
    major = run("(py-getattr v-info \"major\")")
    assert isinstance(major, int)


def test_py_eval():
    assert run("(py-eval \"1 + 2\")") == 3
    assert run("(py-eval \"'hello' + ' world'\")") == "hello world"


def test_py_exec():
    # exec returns None, but we can check side effects if we could share scope.
    # Since we don't share scope easily yet, just check it runs without error.
    assert run("(py-exec \"print('hello from python')\")") is None
