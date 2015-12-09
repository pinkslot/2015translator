from Node import *

class ParserException(Exception):
    def __init__(self, msg, coor):
        self.msg = msg
        self.coor = coor

    def eprint(self):
        print('SynError: %s at line %d col %d' % ((self.msg,) + self.coor))

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.next()

    def next(self):
        self.cur_token = self.lexer.get_token()

    def error(self, msg):
        raise ParserException(msg, self.cur_token.get_coor())

    def match(self, *l):
        ans = self.cur_token
        if ans.get_ptype() in l:
            self.matched  = ans
            self.next()
            return True
        else: 
            return False

    def expect(self, *l):
        if not self.match(*l):
            pat = 'Expected %s. But found %s'
            expected = l[0] if len(l) == 1 else 'one of: ' + ', '.join(l)
            found = self.cur_token.get_ptype()
            if found is None:
                found = 'nothing'
            self.error(pat % (expected, found))
        return True

    ################### parse expr ###################
    def parse_expr(self):
        ret = self.parse_add()
        while self.match('<', '<=', '=', '<>', '=>', '>'):
            ret = BinOp(self.matched.get_ptype(), ret, self.parse_add())
        return ret

    def parse_add(self):
        ret = self.parse_mul()
        while self.match('+', '-', 'or'):
            ret = BinOp(self.matched.get_ptype(), ret, self.parse_mul())
        return ret

    def parse_mul(self):
        ret = self.parse_un()
        while self.match('*', '/', 'div', 'mod', 'and', 'in'):
            ret = BinOp(self.matched.get_ptype(), ret, self.parse_un())
        return ret

    def parse_un(self):
        if self.match('-', '+', 'not'):
            return UnOp(self.matched.get_ptype(), self.parse_un())
        return self.parse_prim()

    def parse_string(self):
        parts = [ Const(self.matched) ]
        while self.match('char', 'string'):
            parts.append(Const(self.matched))
        return String(parts) if len(parts) > 1 else parts[0]

    def parse_const(self):
        return Const(self.matched) if self.match('integer', 'real') else \
            self.parse_string() if self.match('string', 'char') else None

    def parse_var(self, expect = False):
        test = self.expect if expect else self.match
        return Var(self.matched) if test('ident') else None

    def parse_prim(self):
        if self.match('('):
            ret = self.parse_expr()
            self.expect(')')
            return ret
        else:
            return self.parse_var() or self.parse_const() or self.error('Expected expr')

    ################### parse stmt ###################
    def parse_stmt(self):
        if self.match('ident'):
            var = Var(self.matched)
            if self.match(':='):
                return [Assign(var, self.parse_expr())]
            else:
                args = [var]
                if self.match('('):
                    args.append(self.parse_expr())
                    while self.match(','):
                        args.append(self.parse_expr())
                    self.expect(')')
                return [CallFunc(args)]
        else:
            return self.parse_block()
    
    def parse_block(self):
        stmts = []
        if self.match('begin'):
            stmts += self.parse_stmt()
            while self.match(';'):
                stmts += self.parse_stmt()
            self.expect('end')
        return stmts
