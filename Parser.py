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
        self.last_csv = None
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
        a = Const(self.matched) if self.match('integer', 'real') else \
            self.parse_string() if self.match('string', 'char') else None
        return a

    def parse_var(self, expect = False):
        test = self.expect if expect else self.match
        return Var(self.matched) if test('ident') else None

    def parse_csv(self, sbracket, ebracket):
        if self.match(sbracket):
            csv = [ self.parse_expr() ]
            while self.match(','):
                csv.append(self.parse_expr())
            self.expect(ebracket)
            self.last_csv = csv
            return True
        else:
            return None

    def parse_prim(self):
        var = self.parse_right_val()
        if var:
            if self.parse_csv('(', ')'):
                return CallFunc(var, self.last_csv)
                
            # if type(var.type) == Func:
            #     return CallFunc(var, [])
            return var
        elif self.match('('):
            ret = self.parse_expr()
            self.expect(')')
            return ret
        elif self.match('['):
            ret = Set()
            if not self.match(']'):
                while True:
                    cur = self.parse_expr()
                    if self.match('..'):
                        cur = Range(cur, self.parse_expr())
                    ret.append(cur)
                    if not self.match(','):
                        break
                self.expect(']')
            return ret
        else:
            return self.parse_const(False) or self.expected_error('expression')
        
    def parse_right_val(self):
        var = self.parse_var(False)
        if not var:
            return None
        while True:
            if self.parse_csv('[', ']'):
                var = Index(var, self.last_csv)
            elif self.match('.'):
                var = Member(var, self.parse_var(True))
            elif self.match('^'):
                var = Deref(var)
            else:
                return var

    ################### parse stmt ###################
    def parse_stmt(self):
        var = self.parse_right_val()
        if var:
            if self.match(':='):
                return Assign(var, self.parse_expr())
            return CallFunc(var, self.last_csv if self.parse_csv('(', ')') else [])
        elif self.match('if'):
            ret = If(self.parse_expr())
            self.expect('then')
            ret.append(self.parse_stmt())
            if self.match('else'):
                ret.add_else(self.parse_stmt())
            return ret
        elif self.match('case'):
            ret = Cases(self.parse_expr())
            self.expect('of')
            while True:
                consts = ConstList()
                while True:
                    consts.append(self.parse_const() or self.error('Expected const'))
                    if not self.match(','):
                        break
                self.expect(':')
                ret.append(Case(consts, self.parse_stmt()))
                if not self.match(';'):
                    self.expect('end')
                    return ret
        elif self.match('while'):
            e = self.parse_expr()
            self.expect('do')
            return While(e, self.parse_stmt())
        elif self.match('repeat'):
            stmts = []
            while True:
                stmts.append(self.parse_stmt())
                if not self.match(';'):
                    break
            self.expect('until')
            return Repeat(stmts, self.parse_expr())
        elif self.match('for'):
            ret = For(self.parse_var(True))
            self.expect(':=')
            ret.append(self.parse_expr())
            self.expect('to', 'downto')
            if self.matched.lexem == 'downto':
                ret.set_down()
            ret.append(self.parse_expr())
            self.expect('do')
            ret.append(self.parse_stmt())
            return ret
        elif self.match('with'):
            ret = With(self.parse_var(True))
            while self.match(','):
                ret.append(self.parse_var(True))
            self.expect('do')
            ret.append(self.parse_stmt())
            return ret
        else:
            return self.parse_block() or Empty()
    
    def parse_block(self):
        if self.match('begin'):
            stmts = [ self.parse_stmt() ]
            while self.match(';'):
                stmt = self.parse_stmt()
                if stmt:
                    stmts.append(stmt) 
            self.expect('end')
            return Block(stmts)
        return None
