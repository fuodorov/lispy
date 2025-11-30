import pytest
from lispy import env, types

def test_env_init_empty():
    e = env.Env()
    assert len(e) == 0
    assert e.outer is None

def test_env_init_params():
    keys = [types.get_symbol("x"), types.get_symbol("y")]
    vals = [1, 2]
    e = env.Env(keys, vals)
    assert e[types.get_symbol("x")] == 1
    assert e[types.get_symbol("y")] == 2

def test_env_init_mismatch():
    keys = [types.get_symbol("x")]
    vals = [1, 2]
    with pytest.raises(TypeError):
        env.Env(keys, vals)

def test_env_find_local():
    e = env.Env([types.get_symbol("x")], [1])
    assert e.find(types.get_symbol("x")) == e

def test_env_find_outer():
    outer = env.Env([types.get_symbol("x")], [1])
    inner = env.Env([types.get_symbol("y")], [2], outer)
    assert inner.find(types.get_symbol("x")) == outer
    assert inner.find(types.get_symbol("y")) == inner

def test_env_find_missing():
    e = env.Env()
    with pytest.raises(LookupError):
        e.find(types.get_symbol("z"))

def test_env_update():
    e = env.Env([types.get_symbol("x")], [1])
    e[types.get_symbol("x")] = 2
    assert e[types.get_symbol("x")] == 2
