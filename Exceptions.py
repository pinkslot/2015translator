class ParserException(Exception):
    def __init__(self, msg, coor):
        self.msg = msg
        self.coor = coor

    def eprint(self):
        print('SynError: %s at line %d col %d' % ((self.msg,) + self.coor))

class LexerException(Exception):
    msg = {
        'BadNL': "New line in string",
        'BadEOF': "EOF in comment",
        'BadChar': "Unexpected symbol", 
        'BadCC': "Char code not in range[0, 127]",
        'NoExp': "Expected atleast one digit after '[Ee][-+]?'", 
        'NoHex': "Expected atleast one hex digit after '$'",
        'NoCC': "Expected hex or decimal char code '#'",
        'NoFract': "Expected number after '.' in real number",
    }
    def __init__(self, etype, line, col):
        self.line = line
        self.col = col        
        self.etype = etype

    def eprint(self):
        print('LexerError: %s at line %d' % (self.msg[self.etype], self.line))

    def to_cats(self):
        return '%d\t%d\t%s' % (self.line, self.col, self.etype)

def indent_str(indent, pstr):
    return indent * '\t' + pstr
