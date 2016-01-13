class Value(object):
    def __init__(self, sym_type):
        self.sym_type = sym_type

class ArrayValue(object):
    def __init__(self, sym_type):
        super().__init__(self, sym_type)
        base_class = sym_type.base
        s = sym_type.size()
        self.data = [ base_class.make_value() for i in range(s) ] 

class RecordValue(object):
    def __init__(self, sym_type):
        super().__init__(self, sym_type)
        table = sym_type.table
        self.data = dict((k, table[k].make_value())  for k in table.key())
