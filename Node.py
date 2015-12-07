class Node(object):
    def __init__(self, name, children = []):
        self.name = name
        self.children = children
        self.print_name = name

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

################### Stmt ###################
class Assign(Node):
    def __init__(self, var, expr):
        super().__init__(':=', [var, expr])

class CallFunc(Node):
    def __init__(self, args):
        super().__init__('()', args)

