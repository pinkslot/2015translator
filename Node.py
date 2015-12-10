class Node(object):
    def __init__(self, name, children = None):
        self.name = name
        self.children = children or []
        self.print_name = name

    def append(self, x):
        self.children.append(x)

    def nprint(self, indent = 0):
        print('\t' * indent + self.print_name)
        for i in self.children:
            i.nprint(indent + 1)

################### Expr ###################
class BinOp(Node):
    def __init__(self, op, arg1, arg2):
        super().__init__(op, [arg1, arg2])

class UnOp(Node):
    def __init__(self, op, arg):
        super().__init__(op, [arg])

class Var(Node):
    def __init__(self, token):
        super().__init__('var')
        self.ident = token.lexem
        self.print_name = 'var<%s>' % self.ident

class Const(Node):
    def __init__(self, ttype_or_token, val = None):
        if val is None:
            val = ttype_or_token.value;
            ttype_or_token = ttype_or_token.get_ptype();
            
        super().__init__(ttype_or_token)
        self.val = val
        self.print_name = ttype_or_token + '<%s>' % str(val)

class String(Node):
    def __init__(self, parts):
        super().__init__('string', parts)

class Set(Node):
    def __init__(self):
        super().__init__('set')

class Range(Node):
    def __init__(self, left, right):
        super().__init__('range', [left, right])

class Index(Node):
    def  __init__(self, array, indices):
        super().__init__('index', [array] + indices)

class Member(Node):
    def  __init__(self, record, member):
        super().__init__('member', [record, member])

class Deref(Node):
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
        super().__init__('cases', expr)

class Case(Node):
    def __init__(self, expr, stmt):
        super().__init__('case')

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
