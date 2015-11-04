from Node import BinOp, UnOp, Const, Var

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
        self.cur = self.lexer.get_token()

    def error(self, msg):
        raise ParserException(msg, self.cur.get_coor())

    def match(self, *l):
        ans = self.cur.get_ptype()
        if ans in l:
            self.matched = ans
            self.next()
            return True
        else: 
            return False

    def expect(self, *l):
        if not self.match(*l):
            pat = 'Expected %s. But found %s'
            expected = l[0] if len(l) == 1 else 'one of: ' + ', '.join(l)
            found = self.cur.get_ptype()
            if found is None:
                found = 'nothing'
            self.error(pat % (expected, found))

    def parse_expr(self):
        ret = self.parse_add()
        while self.match('<', '<=', '=', '<>', '=>', '>'):
            ret = BinOp(self.matched, ret, self.parse_add())
        return ret

    def parse_add(self):
        ret = self.parse_mul()
        while self.match('+', '-', 'or'):
            ret = BinOp(self.matched, ret, self.parse_mul())
        return ret

    def parse_mul(self):
        ret = self.parse_un()
        while self.match('*', '/', 'div', 'mod', 'and', 'in'):
            ret = BinOp(self.matched, ret, self.parse_un())
        return ret

    def parse_un(self):
        if self.match('-', '+', 'not'):
            return UnOp(self.matched, self.parse_un())
        return self.parse_prim()


    def parse_prim(self):
        last = self.cur
        if self.match('('):
            ret = self.parse_expr()
            self.expect(')')
            return ret
        else: 
            self.expect('integer', 'real', 'string', 'ident')
            return Var(last.lexem) if self.matched == 'ident' else Const(last.ttype, last.value)
