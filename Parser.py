from Node import *
from Sym import *
from Exceptions import ParserException

class Parser(object):
    def __init__(self, lexer):
        self.buf = []
        self.lexer = lexer
        self.last_csv = None
        self.cur_func = ProgFuncType()
        self.next()
        ParserException.parser = self

    def next(self):
        self.cur_token = self.buf.pop() if len(self.buf) else self.lexer.get_token()

    def prev(self, last):
        self.buf.append(self.cur_token)
        self.cur_token = last

    def error(self, msg):
        raise ParserException(msg, self.cur_token.get_coor())

    def match(self, *l):
        ans = self.cur_token
        if ans.get_ptype() in l:
            self.matched = ans
            self.next()
            return ans
        else: 
            return False

    def expected_error(self, expected):
        found = self.cur_token.get_ptype() or 'nothing'
        self.error('Expected %s but found %s' % (expected, found))

    def expect(self, *l):
        return self.match(*l) or \
            self.expected_error(l[0] if len(l) == 1 else 'one of: ' + ', '.join(l))

    ################### parse expr ###################
    def parse_expr(self):
        ret = self.parse_add()
        while self.match('<', '<=', '=', '<>', '=>', '>'):
            ret = LogicOp(self.matched.get_ptype(), ret, self.parse_add())
        return ret

    def parse_add(self):
        ret = self.parse_mul()
        while self.match('+', '-', 'or'):
            ret = AddOp(self.matched.get_ptype(), ret, self.parse_mul())
        return ret

    def parse_mul(self):
        ret = self.parse_un()
        while self.match('*', '/', 'div', 'mod', 'and', 'in'):
            ret = MulOp(self.matched.get_ptype(), ret, self.parse_un())
        return ret

    def parse_un(self):
        if self.match('-', '+', 'not', '@'):
            return UnOp(self.matched.get_ptype(), self.parse_un())
        return self.parse_prim()

    def parse_string(self):
        parts = [ Const(self.matched) ]
        while self.match('char', 'string'):
            parts.append(Const(self.matched), )
        return String(parts) if len(parts) > 1 else parts[0]

    def parse_const(self, expect):
        return Const(self.matched) if self.match('integer', 'real') else \
            self.parse_string() if self.match('string', 'char') else \
            self.expected_error('constant') if expect else None

    def parse_var(self, expect, table = False):
        table = table or self.cur_func
        test = self.expect if expect else self.match
        return Var(self.matched, self.cur_func.get(self.matched, False)) if test('ident') else None

    def parse_csv(self, sbracket, ebracket):
        if self.match(sbracket):
            csv = [ self.parse_expr() ]
            while self.match(','):
                csv.append(self.parse_expr())
            self.expect(ebracket)
            self.last_csv = csv
            return True
        else:
            return False

    def parse_prim(self):
        var = self.parse_left_val()
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
        
    def parse_left_val(self):
        var = self.parse_var(False)
        if not var:
            return None
        while True:
            if self.match('['):
                var = Index(var, self.parse_expr())         # multi index unsupported!
                self.expect(']')
            elif self.match('.'):
                table = var
                var = Member(var)
                var.set_member(self.parse_var(True, table))
            elif self.match('^'):
                var = Deref(var)
            else:
                return var

    ################### parse stmt ###################
    def parse_stmt(self):
        var = self.parse_left_val()
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
                    consts.append(self.parse_const(True))
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
    
    def parse_block(self, expect = False):
        test = self.expect if expect else self.match
        if test('begin'):
            stmts = [ self.parse_stmt() ]
            while self.match(';'):
                stmt = self.parse_stmt()
                if stmt:
                    stmts.append(stmt) 
            self.expect('end')
            return Block(stmts)
        return None

    ################### parse declaration ###################
    def parse_simple_type(self):
        if self.match('('):
            t = EnumType()
            while True:
                EnumVar(self.expect('ident'), t, self.cur_func)
                if not self.match(','):
                    break
            self.expect(')')
            return t
        else:
            if self.match('ident'):
                t = self.cur_func.get(self.matched, True, False)
                if t:
                    return t
                self.prev(self.matched)
            try:
                fst = self.parse_expr()
            except ParserException as e:
                e.msg = e.msg.replace('expression', 'simple type')
                raise
            self.expect('..')
            lst = self.parse_expr()
            return RangeType(fst, lst)

    def parse_type(self):
        if self.match('^'):
            return PointerType(self.cur_func.get(self.expect('ident'), True, True, True))
        elif self.match('set'):
            self.expect('of')
            return SetType(self.parse_simple_type())
        elif self.match('array'):
            self.expect('of')
            return ArrayType(self.parse_type())
        elif self.match('record'):
            table = RecordType()
            while True:
                self.parse_idents_type(SymVar, False, table)
                if not self.match(';'):
                    self.expect('end')
                    return table
        else:
            return self.parse_simple_type()

    def parse_idents_type(self, Type, just_id = False, table = None):
        table = table or self.cur_func
        fst = self.expect('ident')
        arr = [ fst ]
        while self.match(','):
            arr.append(self.expect('ident'))
        self.expect(':')
        t = self.cur_func.get(self.expect('ident'), True) if just_id else self.parse_type()
        for i in arr:
            a = Type(i, t, table)

    def parse_body(self):
        if self.match('const'):
            ident = self.expect('ident')
            while ident:
                self.expect('=')
                ConstVar(ident, self.parse_expr(), self.cur_func)
                self.expect(';')
                ident = self.match('ident')

        if self.match('type'):
            ident = self.expect('ident')
            while ident:
                self.expect('=')
                self.cur_func.add_type_alias(ident, self.parse_type())
                self.expect(';')
                ident = self.match('ident')

        if self.match('var'):
            while True:
                self.parse_idents_type(SymVar)
                self.expect(';')
                if self.cur_token.get_ptype() != 'ident':
                    break

        while self.parse_head():
            self.parse_body()           # TODO forward
            self.expect(';')
            self.cur_func = self.cur_func.par

        self.cur_func.define(self.parse_block(True))

    def parse_head(self):
        if not self.match('function'):
            return False
        self.cur_func = FuncType(self.expect('ident'), self.cur_func)
        if self.match('('):
            while True:
                if self.match('var'):
                    self.parse_idents_type(RefParamVar, True)
                # elif self.parse_head():            # TODO arg - func
                #     pass
                else:
                    self.parse_idents_type(ParamVar, True)
                if not self.match(';'):
                    break
            self.expect(')')
        if self.match(':'):
            self.cur_func.set_ret_type(self.expect('ident'))
        self.expect(';')
        return True

    def parse_program(self):
        self.match('program')
        self.parse_body()
        self.expect('.')
        return self.cur_func
