from Exceptions import ParserException, indent_str
from Sym import *
from types import MethodType

def non_bool_eval(s):
    return 0 + eval(s)

class Node(object):
    def __init__(self, name, ch = None):
        self.name = name
        self.ch = ch or []

    def append(self, x):
        self.ch.append(x)

    def get_print_name(self):
        return self.name

    def print_str(self, indent = 0):
        ret = indent_str(indent, self.get_print_name() + '\n')
        for i in self.ch:
            ret += i.print_str(indent + 1)
        return ret

################### Expr ###################
class Expr(Node):
    def __init__(self, name, ch = None):
        self.ch = ch or []
        super().__init__(name, ch)

    def get_sym_type(self):                 # TODO inherit definition
        return self.ch[0].get_sym_type()

    def eval(self):
        assert False, 'eval for some Expr'

    def is_true_int(self):
        if self.name in ('=', '<>', 'or', 'and', 'mod', 'div'):
            self.match_operand_type(True, ITYPE, ITYPE)
            return True
        if self.name == 'not':
            self.expect_operand_of_type(True, ITYPE)
            return True
        if self.name in ('<', '<=', '=>', '>'):
            return all(c.get_sym_type() in (ITYPE, RTYPE) for c in self.ch)
        return False

    def type_error(self):
        raise ParserException('Unsupported operands type: ' + ', '.join(x.get_sym_type().name for x in self.ch) +
         ' for operator ' + self.name)

    def match_operand_type(self, expect, types):            # m.b change ==, to isinstance
        for i in range(len(types)):
            et = types[i]
            ft = self.ch[i].get_sym_type()
            if type(ct) == 'type' and type(ft) != ct or type(ct) != 'type' and ft != ct:
                if expect:
                    raise ParserException('Expected operand of type ' + \
                        ct.__name__ if type(ct) == 'type' else ct.name + ' but found' + ft.name)
                return False
            return True

class BinOp(Expr):
    def __init__(self, op, arg1, arg2):
        super().__init__(op, [arg1, arg2])

    pas2py_op = {
        'div': '//',
        'mod': '%',
        '<>': '!='
    }

    def py_op(self):
        return self.pas2py_op[self.name] if self.name in self.pas2py_op else self.name

    def eval(self, is_const = False):
        return non_bool_eval((' ' + self.py_op() + ' ').join((str(self.ch[i].eval(is_const)) for i in (0,1))))

    def get_sym_type(self):
        return self.sym_type

class LogicOp(BinOp):
    def __init__(self, op, arg1, arg2):
        super().__init__(op, arg1, arg2)
        if self.is_true_int():
            pass
        else:
            self.type_error()

class AddOp(BinOp):
    def __init__(self, op, arg1, arg2):
        super().__init__(op, arg1, arg2)
        if self.is_true_int():
            return

        (ch0, ch1) = ( x.get_sym_type() for x in self.ch )
        is_plus_min = self.name in ('+', '-')

        if self.name == '+' and self.match_operand_type(False, STYPE, STYPE):
            self.sym_type = STYPE
            self.eval = MethodType(lambda lself, is_const = False: lself.ch[0].eval() + lself.ch[1].eval(), self)

        elif is_plus_min and self.match_operand_type(False, ITYPE, ITYPE):
            self.sym_type = ITYPE
        elif ch0 in (ITYPE, RTYPE) and ch1 in (ITYPE, RTYPE) and is_plus_min:
            self.sym_type = RTYPE
        else:
            self.type_error()
        # (at, mt) = self.another_type(PointerType)         # TODO pointer arithm
        # if at:
        #     if type(at) == PointerType and self.name == '-':
        #         return ITYPE
        #     if at == ITYPE and is_plus_min:
        #         return mt

class MulOp(BinOp):
    def __init__(self, op, arg1, arg2):
        super().__init__(op, arg1, arg2)
        if self.is_true_int():
            return

        (ch0, ch1) = ( x.get_sym_type() for x in self.ch )
        is_mul_div = self.name in ('*', '/')

        if is_mul_div and self.match_operand_type(False, ITYPE, ITYPE):
            self.sym_type = ITYPE
        elif ch0 in (ITYPE, RTYPE) and ch1 in (ITYPE, RTYPE) and is_mul_div:
            self.sym_type = RTYPE
        #if self.name == 'in' TODO in op
        else:
            self.type_error()

    # def another_match_type(self, TypeClass):
    #     (ch0, ch1) = ( x.get_sym_type() for x in self.ch )
    #     if type(ch0) == TypeClass:
    #         return (ch1, ch0)
    #     if type(ch1) == TypeClass:
    #         return (ch0, ch1)
    #     return None

    def get_sym_type(self):
        return self.sym_type

class UnOp(Expr):
    def __init__(self, op, arg):
        super().__init__(op, [arg])
        if self.name == '@':
            # TODO check is var and move into separate class

    def eval(self, is_const = False):
        if self.name == '@':
            if is_const:           # TODO eval addr
                raise ParserException('Expected const but found addr')
        else:
            return non_bool_eval(self.name + ' ' + str(self.ch[0].eval(is_const)))

    def get_sym_type(self):
        ch_type = self.ch[0].get_sym_type()
        return PointerType(ch_type) if self.name == '@' else ch_type

class Const(Expr):
    def __init__(self, token):
        super().__init__(token.get_ptype())
        self.value = token.value

    def get_print_name(self):
        return self.name + '<%s>' % str(self.value)

    def get_sym_type(self):
        return BASE_TYPES[self.name]

    def eval(self, is_const = False):
        return self.value

class String(Expr):
    def __init__(self, parts):
        super().__init__('string', parts)

    def eval(self, is_const):
        return ''.join((x.eval(is_const) for x in self.ch))

    def get_sym_type(self):
        return STYPE

class Set(Expr):
    def __init__(self):
        super().__init__('set')

class Range(Expr):
    def __init__(self, left, right):
        super().__init__('range', [left, right])

class LeftValue(Expr):
    def get_sym_var(self):
        assert False, 'get_sym_var for base left_value class'

    def get_sym_type(self):
        return self.get_sym_var().sym_type

    def eval(self, is_const = False):
        return self.get_sym_var.eval(is_const)

    def get_sym_var(self):
        return self.sym_var

class Var(LeftValue):
    def __init__(self, token, sym_var):
        super().__init__('var')
        self.sym_var = sym_var
        self.ident = token.lexem

    def get_print_name(self):
        return 'var<%s>' % self.ident

class Index(LeftValue):
    def  __init__(self, array, index):
        super().__init__('index', [array, index])
        self.match_operand_type(True, ArrayType, ITYPE)
        self.sym_type = array.base

class Member(LeftValue):
    def  __init__(self, record):
        super().__init__('member', [record, member])
        self.match_operand_type(True, RecordType)

    def set_member(self, m):
        self.append(m)
        self.sym_var = m.sym_var

class Deref(LeftValue):
    def  __init__(self, pointer):
        super().__init__('deref', [pointer])
        self.match_operand_type(True, PointerType)


################### Stmt ###################
class Assign(Node):
    def __init__(self, var, expr):
        super().__init__(':=', [var, expr])

class CallFunc(Node):
    def __init__(self, func, args):
        super().__init__('call', [func] + args)

class Block(Node):
    def __init__(self, stmts):
        super().__init__('block', stmts)

class If(Node):
    def __init__(self, expr):
        super().__init__('if', [expr])
        self.have_else = False

    def add_else(self, smtm):
        self.append(smtm)
        self.have_else = True
class Cases(Node):
    def __init__(self, expr):
        super().__init__('cases', [expr])

class Case(Node):
    def __init__(self, expr, stmt):
        super().__init__('case', [expr, stmt])

class ConstList(Node):
    def __init__(self):
        super().__init__('c_list')

class While(Node):
    def __init__(self, expr, stmt):
        super().__init__('while', [expr, stmt])

class Repeat(Node):
    def __init__(self, stmts, expr):
        super().__init__('repeat', [Block(stmts), expr])

class For(Node):
    def __init__(self, var):
        super().__init__('for', [var])
        self.down = False

    def set_down(self):
        self.name += '_down'
        self.down = True

class With(Node):
    def __init__(self, rec):
        super().__init__('with', [rec])

class Empty(Node):
    def __init__(self):
        super().__init__('empty')
