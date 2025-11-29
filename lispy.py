import math
import operator as op

Symbol, Number, List = str, (int, float), list

def parse(program):
    return read_from_tokens(tokenize(program))

def tokenize(s):
    return s.replace('(', ' ( ').replace(')', ' ) ').split()

def read_from_tokens(tokens):
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
        
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)  # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)

def repl(prompt='> '):
    print("Lispy REPL. Type '(exit)' or '(quit)' to leave.")
    while True:
        try:
            inp = input(prompt)
            if inp is None:
                continue
            inp = inp.strip()
            if not inp:
                continue
            if inp.lower() in ('(exit)', '(quit)'):
                print("Exiting Lispy REPL.")
                break
            try:
                val = eval(parse(inp))
                if val is not None:
                    print(lispstr(val))
            except Exception as e:
                print(f"{type(e).__name__}: {e}")
        except KeyboardInterrupt:
            print("\nInterrupted. Type '(exit)' or '(quit)' to leave.")
            continue

def lispstr(exp):
    return '(' + ' '.join(map(lispstr, exp)) + ')' if isinstance(exp, List) else str(exp)

class Procedure(object):
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env

    def __call__(self, *args):
        return eval(self.body, Env(self.parms, args, self.env))

class Env(dict):
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        if var in self:
            return self
        if self.outer is None:
            raise NameError(f"undefined variable: {var}")
        return self.outer.find(var)

global_env = Env()
global_env.update({
    '+': op.add, 
    '-': op.sub, 
    '*': op.mul, 
    '/': op.truediv, 
    '>': op.gt,
    '<': op.lt, 
    '>=': op.ge, 
    '<=': op.le, 
    '=': op.eq, 
    'abs': abs,
    'append': op.add, 
    'begin': lambda *x: x[-1], 
    'car': lambda x: x[0],
    'cdr': lambda x: x[1:], 
    'cons': lambda x, y: [x] + y, 
    'eq?': op.is_,
    'equal?': op.eq, 
    'length': len, 
    'list': lambda *x: list(x),
    'list?': lambda x: isinstance(x, list), 
    'map': map, 
    'max': max, 
    'min': min, 
    'not': op.not_,
    'null?': lambda x: x == [], 
    'number?': lambda x: isinstance(x, Number),
    'procedure?': callable, 
    'round': round, 
    'symbol?': lambda x: isinstance(x, Symbol),
    **vars(math), # sin, cos, sqrt, pi, ...
})

def eval(x, env=global_env):
    if isinstance(x, Symbol):      # variable reference
        return env.find(x)[x]
    elif not isinstance(x, List):  # constant literal
        return x
    elif x[0] == 'quote':          # (quote exp)
        (_, exp) = x
        return exp
    elif x[0] == 'if':             # (if test conseq alt)
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif x[0] == 'define':         # (define var exp)
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'set!':           # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'lambda':         # (lambda (var...) body)
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:                          # (proc arg...)
        proc = eval(x[0], env)
        args = [eval(exp, env) for exp in x[1:]]
        return proc(*args)  

if __name__ == '__main__':
    repl()
