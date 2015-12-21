class Token(object):
    operators = {
        'and',      'div',      'mod',      'not',       'or',        'xor',      '+',        '-',
        '*',        '/',        '^',        '+=',        '-=',        '*=',       '/=',       '<',
        '>',        '<=',       '>=',       '=',        '<>',        ':=',        '@',        '.'
    }

    separators = {
        '(',        ')',        '[',        ']',        ';',        ',',        ':',        '..',
    }

    reserved = {
        'begin',        'forward',  'do',       'else',     'end',          'for',
        'function',     'if',       'array',    'of',       'program',
        'record',       'then',     'to',       'type',     'var',          'while',
        'break',        'continue', 'downto',   'exit',     'repeat',       'until',
        'case',         'with',     'const',    'set'
    }

    pas2py_value = {
        'integer' : int,
        'real': float,
        'string': lambda x: x[1:-1].replace("''", "'"),            # cut quotes
        'hex': lambda x: int(x[1:], 16),
        'hexchar': lambda x: chr(int(x[2:], 16)),
        'decchar': lambda x: chr(int(x[1:])),
    }

    def tprint(self):
        print('%s %d\n%s' % (self.ttype, self.line, self.lexem))

    def to_cats(self):
        return '%d\t%d\t%s\t%s' % (self.line, self.col, self.ttype, self.lexem)

    def get_coor(self):
        return (self.line, self.col)

    def get_ptype(self):
        if self.ttype == 'hex':
            return 'integer'
        elif self.ttype == 'keyword' or self.ttype == 'op' or self.ttype == 'sep':
            return self.lexem
        return self.ttype

    def __init__(self, ttype, lexem, line, col):
        self.ttype = ttype
        self.lexem = lexem
        self.line = line
        self.col = col

    @classmethod
    def cons(cls, ttype, lexem, line, col):
        if ttype == '':
            if lexem in cls.operators:
                ttype = 'op'
            elif lexem in cls.separators:
                ttype = 'sep'
            else: 
                raise Exception("Undefined sign '%s'in token constructor" % lexem);

        elif ttype == 'ident':
            ttype = 'keyword' if lexem in cls.reserved \
                else ('op' if lexem in cls.operators else 'ident')
        if ttype in cls.pas2py_value.keys():
            return ValueToken(ttype, lexem, line, col)
        else: 
            return Token(ttype, lexem, line, col)

class ValueToken(Token):

    pas2format_value = {
        'integer' : 'd',
        'real': '.4E',
        'string': 's',
        'hex': 'd',
        'char': 's',
    }
    def __init__(self, ttype, lexem, line, col):
        super().__init__(ttype, lexem, line, col)
        self.value = self.pas2py_value[self.ttype](lexem)
        if self.ttype == 'string' and len(self.value) == 1 or self.ttype in ( 'hexchar', 'decchar' ):
            self.ttype = 'char'            

    def tprint(self):
        super().tprint()
        fmt = 'value: %' + self.pas2format_value[self.ttype]; 
        print( fmt % self.value)

    def to_cats(self):
        fmt = '\t%' + self.pas2format_value[self.ttype];
        return super().to_cats() + (fmt % self.value)

class DummyToken(Token):
    def __init__(self, line, col):
        super().__init__(None, None, line, col)
