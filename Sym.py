from Exceptions import *

class Sym(object):
    def __init__(self, name):
        self.name = name

class SymType(Sym):
    def __init__(self, name):
        super().__init__(name)

    def print_str(self, indent):
        return self.name

class EnumType(SymType):
    def __init__(self):
        super().__init__('enum')
        self.counter = 0

class RangeType(SymType):
    def __init__(self, fst_node, lst_node):
        super().__init__('range_%d_%d' % (fst_node.get_const_value(), lst_node.get_const_value()))
        self.fst = fst_node         # TODO get value
        self.lst = fst_node

class BaseType(SymType):
    def __init__(self, name):
        super().__init__(name)
    
    def equal(self, you):
        return self == yous

BASE_TYPES = dict((x, BaseType(x)) for x in ('integer', 'real', 'string'))
class DerType(SymType):
    def __init__(self, name, base):
        super().__init__(name)
        self.base = base

class PointerType(DerType):
    def __init__(self, base):
        super().__init__('pointer_' + base.name, base)

class ArrayType(DerType):
    def __init__(self, base):
        super().__init__('array_' + base.name, base)

class SetType(DerType):
    def __init__(self, base):
        super().__init__('set_' + base.name, base)

class SymVar(Sym):
    def __init__(self, id_token, stype, table):
        table.check_empty(id_token, False)
        ident = id_token.lexem
        super().__init__(ident)
        self.sym_type = stype
        table.var_table[ident] = self

    def print_str(self, indent):
        return indent_str(indent, self.name + ' - ' + self.sym_type.print_str(indent))

    def get_const_value(self):
        raise ParserException('Expected const but found var', id_token.get_coor())

class EnumVar(SymVar):
    def __init__(self, id_token, stype, func):
        super().__init__(id_token, stype, func)
        stype.name += '_' + self.name
        self.name = 'member_' + self.name
        self.ord = stype.counter
        stype.counter += 1

    # def sprint(self, indent):
    #     pass

class ParamVar(SymVar):
    def __init__(self, id_token, stype, func):
        super().__init__(id_token, stype, func)
        func.name += '_' + stype.name
        self.name += '_param'
        func.param.append(self)

class RefParamVar(ParamVar):
    def __init__(self, id_token, stype, func):
        super().__init__(id_token, stype, func)
        self.name += '_ref'

class ConstVar(SymVar):
    def __init__(self, id_token, node_val, func):
        super().__init__(id_token, node_val.get_sym_type(), func)             # TODO node_val.get_type()
        self.value = node_val.get_const_value()

    def get_const_value(self):
        return self.value

    def print_str(self, indent):
        return super().print_str(indent) + ' const<%s>' % self.value

class Table(SymType):
    def __init__(self, name):
        super().__init__(name)
        self.var_table = {}

    def local_id(self, id_token, is_type_or_var):
        table = self.type_table if is_type_or_var else self.var_table
        name = id_token.lexem
        return table[name] if name in table else None

    def check_empty(self, id_token, is_type_or_var):
        prev = self.local_id(id_token, is_type_or_var)
        if prev:
            raise ParserException('Redefinition ' + id_token.lexem + \
                ' prev def as ' + prev.sym_type.name, id_token.get_coor() )  # add info about prev def
        
    def print_str(self, indent):
        ret = super().print_str(indent) + '\n'
        if len(self.var_table):
            ret += indent_str(indent, 'VAR---------------\n')
            for v in self.var_table.values():
                ret += v.print_str(indent + 1) + '\n'
        return ret

class FuncType(Table):
    def __init__(self, id_token, func):
        super().__init__('func')
        SymVar(id_token, self, func)
        self.param = []
        self.type_table = {}
        self.ret_type = None
        self.par = func
        self.code = None

    def set_ret_type(self, id_token):
        self.ret_type = self.par.get(id_token, True)
        self.name = self.ret_type.name + '_' + self.name

    def define(self, code):
        self.code = code

    def get(self, id_token, is_type_or_var, raise_except = True, make_if_not_exist = False):    # make_if_not to realize predefine pointer
        return self.local_id(id_token, is_type_or_var) or self.par.get(id_token, is_type_or_var, raise_except)

    def add_type_alias(self, id_token, sym_type):
        self.check_empty(id_token, True)
        self.type_table[id_token.lexem] = sym_type

    def print_str(self, indent = 0):
        ret = super().print_str(indent)
        if len(self.type_table):
            ret += indent_str(indent, 'TYPE---------------\n')    
            for k, v in self.type_table.items():
                ret += indent_str(indent + 1, k + ' - ' + v.print_str(indent + 1) + '\n')
        ret += indent_str(indent, 'CODE---------------\n')
        ret += self.code.print_str(indent + 1)
        return ret

class ProgFuncType(FuncType):
    def __init__(self):
        self.name = 'programm'
        self.code = None
        self.var_table = {}
        self.type_table = {}
        self.par = DummyFuncType()


class DummyFuncType(FuncType):
    def __init__(self):
        self.type_table = BASE_TYPES

    def get(self, id_token, is_type_or_var, raise_except):
        if is_type_or_var:
            base_type = self.local_id(id_token, is_type_or_var)
            if base_type:
                return base_type
        if raise_except:
            raise ParserException('Undefined ' + ('type ' if is_type_or_var else\
               'var ') + id_token.lexem, id_token.get_coor())
        return None

class RecordType(Table):
    def __init__(self):
        super().__init__('record')
        self.var_table = {}
