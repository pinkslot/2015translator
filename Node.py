from Exceptions import ParserException, indent_str
from Sym import *

class Node(object):
    def __init__(self, name, children = None):
        self.name = name
        self.children = children or []

    def append(self, x):
        self.children.append(x)

    def get_print_name(self):
        return self.name

    def print_str(self, indent = 0):
        ret = indent_str(indent, self.get_print_name() + '\n')
        for i in self.children:
            ret += i.print_str(indent + 1)
        return ret

################### Expr ###################
class Expr(Node):
    def __init__(self, name, children = None):
        self.children = children or []
        super().__init__(name, children)

    def get_sym_type(self):                 # TODO inherit definition
        return self.children[0].get_sym_type()

    def get_const_value(self):
        assert False, 'get_value for some Expr'

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

    def get_const_value(self):
        return eval(self.py_op().join((str(self.children[i].get_const_value()) for i in (0,1))))

class UnOp(Expr):
    def __init__(self, op, arg):
        super().__init__(op, [arg])

    def get_const_value(self):
        return eval(self.name + self.children[0].get_const_value())

class Var(Expr):
    def __init__(self, token, sym_var):
        super().__init__('var')
        self.sym_var = sym_var
        self.ident = token.lexem

    def get_print_name(self):
        return 'var<%s>' % self.ident

    def get_sym_type(self):
        print(self.sym_var, self.ident)
        return self.sym_var.sym_type

    def get_const_value(self):
        return self.sym_var.get_const_value()

class Const(Expr):
    def __init__(self, token):
        super().__init__(token.get_ptype())
        self.value = token.value

    def get_print_name(self):
        return self.name + '<%s>' % str(self.value)

    def get_sym_type(self):
        return BASE_TYPES[self.name]

    def get_const_value(self):
        print 
        if self.get_sym_type() == BASE_TYPES['string']:
            return "'''%s'''" % self.value
        return self.value

class String(Expr):
    def __init__(self, parts):
        super().__init__('string', parts)

    def get_const_value(self):
        return ''.join((x.get_const_value() for x in self.children))

class Set(Expr):
    def __init__(self):
        super().__init__('set')

class Range(Expr):
    def __init__(self, left, right):
        super().__init__('range', [left, right])

class Index(Expr):
    def  __init__(self, array, indices):
        super().__init__('index', [array] + indices)

class Member(Expr):
    def  __init__(self, record, member):
        super().__init__('member', [record, member])

class Deref(Expr):
    def  __init__(self, pointer):
        super().__init__('deref', [pointer])    

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
