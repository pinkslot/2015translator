from Token import Token, ValueToken, DummyToken
from Exceptions import LexerException
class Lexer(object):
    buf_size = 10
    EOFs = '`'

    def isEOF(self):
        return self.EOFn >= 0 and self.EOFn == self.buf_iter

    def load_buf(self):
        self.buf_iter = 0;
        # self.prev_buf = self.buf
        self.buf = self.file.read(self.buf_size);
        if len(self.buf) != self.buf_size:
            self.buf += self.EOFs
            self.EOFn = len(self.buf) - 1

    def next(self, init = False):
        if not init:
            if self.cur == '\n':
                self.linec += 1;
                self.colc = 1;
            elif self.cur == '\t':
                self.colc += 4 - (self.colc-1) % 4
            else:
                self.colc += 1

            self.lexem += self.cur
            self.buf_iter += 1
        if init or self.buf_iter == len(self.buf):     
            self.load_buf()
        self.cur = self.buf[self.buf_iter]
        return self.cur

    def error(self, code):
        raise LexerException(code, self.linec, self.colc)

    def matchf(self, f):
        if f(self.cur):
            self.next()
            return True
        return False

    def match(self, *l):
        if self.cur in l:
            self.next()
            return True
        return False  

    def parse_num(self):
        ret = self.matchf(lambda x: x.isdigit())
        while self.matchf(lambda x: x.isdigit()):
            pass
        return ret

    def parse_hex(self):
        if self.match('$'):
            f = False
            while self.matchf(lambda x: x.isdigit() or 'A' <= x <= 'F' or 'a' <= x <= 'f'):
                f = True
            if not f:
                self.error('NoHex')
            return True
        else:
            return False

    def parse_exp(self):
        if self.match('e', 'E'):
            self.match('+', '-')
            if not self.parse_num():
                self.error('NoExp')
            return True
        return False

    def new_lexem(self):
        self.lexem = ''
        self.lcolc = self.colc
        self.llinec = self.linec

    def skip_white_space(self):
        ret = False
        while self.match('\t', ' ', '\n', '\r'):
            ret = True
        return ret

    def get_token(self):
        if self.token_buf:
            res = self.token_buf
            self.token_buf = None
            return res
        if self.isEOF():
            return DummyToken(self.llinec, self.lcolc)

        ttype = ''
        self.new_lexem()

        if self.skip_white_space():
            return self.get_token()

        elif self.match('{'):
            while True:
                if self.isEOF():
                    self.error('BadEOF')
                elif self.match('}'):
                    return self.get_token()
                else:
                    self.next()

        elif self.match('('): 
            if self.match('*'):
                while True:
                    if self.isEOF():
                        self.error('BadEOF')
                    elif self.match('*'):                                   # don't use:
                                                                            #    if self.match('*') and self.match(')')
                        if self.match(')'):                                 # because programm will go to ..
                            return self.get_token()
                    else:
                        self.next()                                         # this line and out of range

        elif self.match('/'):
            if self.match('/'):
                while True:
                    if self.isEOF():
                        return None
                    elif self.match('\n'):
                        return self.get_token()
                    else:
                        self.next()
            else: 
                self.match('=')

        elif self.matchf(lambda x: x.isalpha() or x == '_'):
            ttype = 'ident';
            while self.matchf(lambda x: x.isalpha() or x == '_' or x.isdigit()):
                pass
        
        elif self.matchf(lambda x: x.isdigit()):
            ttype = 'integer'
            self.parse_num()
            if self.match('.'):
                if self.match('.'):
                    self.token_buf = Token.cons('', '..', self.linec, self.colc - 2)
                    return Token.cons(ttype, self.lexem[:-2], self.llinec, self.lcolc)
                elif self.parse_num():
                    ttype = 'real'
                else:
                    self.error('NoFract')
            if self.parse_exp():
                ttype = 'real'

        elif self.parse_hex():
            ttype = 'hex'

        elif self.match('#'):
            if self.parse_num():
                code = int(self.lexem[1:])
                ttype = 'decchar'
            elif self.parse_hex():
                code = int(self.lexem[2:], 16)
                ttype = 'hexchar'
            else:
                self.error('NoCC')
            if not 0 <= code <= 127:
                self.error('BadCC')

        elif self.match("'"):
            while True:
                if self.cur == '\n':
                    self.error('BadNL')
                if self.isEOF():
                    self.error('BadEOF')
                elif self.match("'"):
                    if self.match("'"):
                        continue
                    else:
                        break
                else: 
                    self.next()
            ttype = 'string'

        elif self.match('.'):
            self.match('.')
        
        elif self.match('<'):
            self.match('>', '=')

        elif self.match('>', ':', '+', '-', '*'):
            self.match('=')

        elif self.match(',', '^', ';', ')', '[', ']', '=', '@'):
            pass
        else:
            self.error('BadChar')

        return Token.cons(ttype, self.lexem, self.llinec, self.lcolc)

    def __init__(self, f):
        self.file = f
        # self.prev_buf = ''
        self.linec = 1
        self.colc = 1
        self.EOFn = -1
        self.token_buf = None
        self.new_lexem()
        self.next(True)
