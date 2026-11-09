"""Execute this project's PPL source for host regression tests.

This deliberately small interpreter checks the actual shipped source, including
keypad state transitions. It is not HP's compiler and does not establish firmware
compatibility. Native calculator checks are recorded separately.
"""
from __future__ import annotations
import copy
import math
import re


TOKEN = re.compile(r'\s+|//[^\n]*|"(?:[^"\\]|\\.)*"|(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?|[A-Za-z_]\w*|:=|<>|<=|>=|==|[^\s]')


class Return(Exception):
    def __init__(self, value):
        self.value = value


class Parser:
    def __init__(self, source):
        source = re.sub(r'^#pragma[^\n]*', '', source, flags=re.M)
        self.tokens = [m.group() for m in TOKEN.finditer(source)
                       if not m.group().isspace() and not m.group().startswith('//')]
        self.i = 0

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else ''

    def take(self, expected=None):
        token = self.peek()
        if expected is not None and token != expected:
            raise SyntaxError(f'Expected {expected}, got {token}; near {self.tokens[max(0,self.i-8):self.i+8]}')
        if not token:
            raise SyntaxError('Unexpected end of source')
        self.i += 1
        return token

    def expr(self, minimum=0):
        token = self.take()
        if token in ('-', '+', 'NOT'):
            left = ('unary', token, self.expr(7))
        elif token == '(':
            left = self.expr()
            self.take(')')
        elif token == '{':
            items = []
            while self.peek() != '}':
                items.append(self.expr())
                if self.peek() != ',': break
                self.take(',')
            self.take('}')
            left = ('list', items)
        elif token.startswith('"'):
            left = ('literal', token[1:-1].replace('\\"', '"'))
        elif re.fullmatch(r'(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?', token):
            left = ('literal', float(token))
        else:
            left = ('name', token)
        precedence = {'OR': 1, 'AND': 2, '==': 3, '=': 3, '<>': 3, '<': 3, '>': 3,
                      '<=': 3, '>=': 3, '+': 4, '-': 4, '*': 5, '/': 5, 'MOD': 5, '^': 8}
        while True:
            token = self.peek()
            if token == '(':
                self.take()
                args = []
                while self.peek() != ')':
                    args.append(self.expr())
                    if self.peek() != ',': break
                    self.take(',')
                self.take(')')
                left = ('call', left, args)
            elif token in precedence and precedence[token] >= minimum:
                self.take()
                prec = precedence[token]
                left = ('binary', token, left, self.expr(prec + (token != '^')))
            else:
                break
        return left

    def sequence(self, stops):
        out = []
        while self.peek() and self.peek() not in stops:
            out.append(self.statement())
        return out

    def declarations(self):
        out = []
        while True:
            name = self.take()
            value = ('literal', 0)
            if self.peek() == ':=':
                self.take()
                value = self.expr()
            out.append((name, value))
            if self.peek() != ',': break
            self.take(',')
        self.take(';')
        return out

    def statement(self):
        token = self.peek()
        if token == 'LOCAL':
            self.take()
            return ('local', self.declarations())
        if token == 'IF':
            self.take(); condition = self.expr(); self.take('THEN')
            yes = self.sequence({'ELSE', 'END'})
            no = []
            if self.peek() == 'ELSE':
                self.take(); no = self.sequence({'END'})
            self.take('END'); self.take(';')
            return ('if', condition, yes, no)
        if token == 'IFERR':
            self.take(); body = self.sequence({'THEN'}); self.take('THEN')
            error = self.sequence({'ELSE', 'END'}); success = []
            if self.peek() == 'ELSE':
                self.take(); success = self.sequence({'END'})
            self.take('END'); self.take(';')
            return ('iferr', body, error, success)
        if token == 'FOR':
            self.take(); var = self.take(); self.take('FROM'); start = self.expr()
            direction = self.take()
            if direction not in ('TO', 'DOWNTO'): raise SyntaxError(direction)
            end = self.expr(); self.take('DO'); body = self.sequence({'END'})
            self.take('END'); self.take(';')
            return ('for', var, start, end, -1 if direction == 'DOWNTO' else 1, body)
        if token == 'WHILE':
            self.take(); condition = self.expr(); self.take('DO')
            body = self.sequence({'END'}); self.take('END'); self.take(';')
            return ('while', condition, body)
        if token == 'REPEAT':
            self.take(); body = self.sequence({'UNTIL'}); self.take('UNTIL')
            condition = self.expr(); self.take(';')
            return ('repeat', body, condition)
        if token == 'RETURN':
            self.take(); value = self.expr(); self.take(';')
            return ('return', value)
        left = self.expr()
        if self.peek() == ':=':
            self.take(); value = self.expr(); self.take(';')
            return ('assign', left, value)
        self.take(';')
        return ('expression', left)

    def program(self):
        functions, globals_ = {}, []
        while self.peek():
            if self.peek() == 'EXPORT': self.take()
            name = self.take()
            if self.peek() != '(':
                self.i -= 1
                globals_.extend(self.declarations())
                continue
            self.take('('); args = []
            while self.peek() != ')':
                args.append(self.take())
                if self.peek() != ',': break
                self.take(',')
            self.take(')')
            if self.peek() == ';':
                self.take(); continue
            self.take('BEGIN')
            body = self.sequence({'END'})
            self.take('END'); self.take(';')
            functions[name] = (args, body)
        return functions, globals_


class Runner:
    def __init__(self, source):
        self.functions, globals_ = Parser(source).program()
        self.globals = {'HAngle': 0, 'HFormat': 0, 'HDigits': 11, 'HSeparator': 0}
        self.keys = []
        self.drawn = []
        self.budget = 1000000
        for name, value in globals_:
            self.globals[name] = self.eval(value, {})

    def call(self, name, *args):
        if name not in self.functions:
            return self.builtin(name, list(args))
        params, body = self.functions[name]
        if len(params) != len(args):
            raise TypeError(f'{name}: {len(params)} parameters, {len(args)} arguments')
        env = dict(zip(params, copy.deepcopy(args)))
        try:
            self.execute(body, env)
        except Return as result:
            return copy.deepcopy(result.value)
        return 0

    def builtin(self, name, args):
        degree = self.globals['HAngle'] == 0
        angle = lambda x: math.radians(x) if degree else x
        inverse = lambda x: math.degrees(x) if degree else x
        funcs = {'ABS': abs, 'FLOOR': math.floor, 'CEILING': math.ceil, 'SQRT': math.sqrt,
                 'SIN': lambda x: math.sin(angle(x)), 'COS': lambda x: math.cos(angle(x)),
                 'TAN': lambda x: math.tan(angle(x)), 'ATAN': lambda x: inverse(math.atan(x)),
                 'ASIN': lambda x: inverse(math.asin(x)), 'ACOS': lambda x: inverse(math.acos(x)),
                 'LN': math.log, 'EXP': math.exp, 'MAX': max, 'MIN': min,
                 'ROUND': lambda x, n=0: round(x, int(n)), 'SIZE': len,
                 'CONCAT': lambda a, b: a+b, 'STRING': lambda x: str(int(x)) if isinstance(x, (float,int)) and x == int(x) else str(x),
                 'LEFT': lambda s, n: s[:int(n)], 'RIGHT': lambda s,n: s[-int(n):] if n else '',
                 'MID': lambda s, n, count: s[int(n)-1:int(n)-1+int(count)],
                 'CHAR': lambda x: chr(int(x)), 'EXPR': lambda s: float(s),
                 'TYPE': lambda x: 0 if isinstance(x,(int,float)) else (2 if isinstance(x,str) else 6),
                 'WAIT': lambda t: 0, 'RGB': lambda *a: 0,
                 'RECT_P': lambda *a: 0, 'LINE_P': lambda *a: 0,
                 'TEXTOUT_P': lambda *a: self.drawn.append(a),
                 'GETKEY': lambda: self.keys.pop(0) if self.keys else self.no_keys()}
        if name not in funcs: raise NameError(name)
        return funcs[name](*args)

    def no_keys(self):
        raise RuntimeError('Simulated keypad input exhausted')

    def eval(self, node, env):
        kind, *args = node
        if kind == 'literal': return args[0]
        if kind == 'list': return [self.eval(x,env) for x in args[0]]
        if kind == 'name':
            name = args[0]
            if name in env: return env[name]
            if name in self.globals: return self.globals[name]
            if name == 'GETKEY': return self.builtin(name, [])
            return name
        if kind == 'call':
            target, values = args
            evaluated = [self.eval(x,env) for x in values]
            if target[0] == 'name' and target[1] not in env and target[1] not in self.globals:
                return self.call(target[1], *evaluated)
            result = self.eval(target,env)
            for index in evaluated: result = result[int(index)-1]
            return result
        if kind == 'unary':
            op, value = args; value = self.eval(value,env)
            return {'-': lambda: -value, '+': lambda: value, 'NOT': lambda: int(not value)}[op]()
        if kind == 'binary':
            op, left, right = args; a = self.eval(left,env)
            if op == 'AND' and not a: return 0
            if op == 'OR' and a: return 1
            b = self.eval(right,env)
            operations = {'+':lambda:a+b, '-':lambda:a-b, '*':lambda:a*b, '/':lambda:a/b,
                          '^':lambda:a**b, 'MOD':lambda:a%b, '=':lambda:int(a==b),
                          '==':lambda:int(a==b), '<>':lambda:int(a!=b), '<':lambda:int(a<b),
                          '>':lambda:int(a>b), '<=':lambda:int(a<=b), '>=':lambda:int(a>=b),
                          'AND':lambda:int(bool(a) and bool(b)), 'OR':lambda:int(bool(a) or bool(b))}
            return operations[op]()
        raise NotImplementedError(node)

    def assign(self, target, value, env):
        if target[0] == 'name':
            name = target[1]
            (env if name in env or name not in self.globals else self.globals)[name] = copy.deepcopy(value)
        elif target[0] == 'call':
            container = self.eval(target[1],env)
            indexes = [int(self.eval(x,env))-1 for x in target[2]]
            for index in indexes[:-1]: container = container[index]
            container[indexes[-1]] = copy.deepcopy(value)
        else:
            raise SyntaxError(f'Invalid assignment {target}')

    def execute(self, body, env):
        for statement in body:
            self.budget -= 1
            if self.budget < 0: raise RuntimeError('PPL test execution budget exceeded')
            kind, *args = statement
            if kind == 'local':
                for name, value in args[0]: env[name] = self.eval(value,env)
            elif kind == 'assign': self.assign(args[0],self.eval(args[1],env),env)
            elif kind == 'expression': self.eval(args[0],env)
            elif kind == 'return': raise Return(self.eval(args[0],env))
            elif kind == 'if': self.execute(args[1] if self.eval(args[0],env) else args[2],env)
            elif kind == 'iferr':
                try: self.execute(args[0],env)
                except Return: raise
                except Exception: self.execute(args[1],env)
                else: self.execute(args[2],env)
            elif kind == 'for':
                name, start, end, step, loop = args
                for i in range(int(self.eval(start,env)), int(self.eval(end,env))+step,step):
                    env[name] = i; self.execute(loop,env)
            elif kind == 'while':
                while self.eval(args[0],env): self.execute(args[1],env)
            elif kind == 'repeat':
                while True:
                    self.execute(args[0],env)
                    if self.eval(args[1],env): break
            else: raise NotImplementedError(statement)
