class Node(object):
    def __init__(self, name, children = []):
        self.name = name
        self.children = children
        self.print_name = name

    def nprint(self, indent = 0):
        print('\t' * indent + self.print_name)
        for i in self.children:
            i.nprint(indent + 1)

class BinOp(Node):
    def __init__(self, op, arg1, arg2):
        super().__init__(op, [arg1, arg2])

class UnOp(Node):
    def __init__(self, op, arg):
        super().__init__(op, [arg])

class Var(Node):
    def __init__(self, ident):
        super().__init__('var')
        self.ident = ident
        self.print_name = 'var<%s>' % self.ident

class Const(Node):
    def __init__(self, ttype, val):
        super().__init__(ttype)
        self.val = val
        self.print_name = ttype + '<%s>' % str(val)