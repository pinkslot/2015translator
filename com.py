from sys import argv
from Lexer import Lexer, LexerException
from Parser import Parser, ParserException

with open(argv[1], 'r') as i:
    try:
        l = Lexer(i)
        if len(argv) > 2 and argv[2] == 'l':
            a = l.get_token()
            while not a.ttype is None:
                print(a.to_cats() + '\n')
                a = l.get_token()
        else:
            p = Parser(l)
            p.parse_expr().nprint()

    except LexerException as e:
        print(e.to_cats())
    except ParserException as e:
        e.eprint()