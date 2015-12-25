from sys import argv
from Lexer import Lexer, LexerException
from Parser import Parser, ParserException

with open(argv[1], 'r') as i:
    try:
        l = Lexer(i)
        if len(argv) > 2 and argv[2] == 'l':
            a = l.get_token()
            while not a.ttype is None:
                print(a.to_cats())
                a = l.get_token()
        else:
            p = Parser(l)
            path = argv[1].split('\\')
            print(p.parse_stmt().print_str(), end='') if path[1] == 'parser-stmt'\
                else print(p.parse_expr().print_str(), end='') if path[1] == 'parser-expr'\
                else print(p.parse_program().print_str(), end='') if path[1] in ('parser-decl', 'sem')\
                else None

    except LexerException as e:
        print(e.to_cats(), end = '')
    except ParserException as e:
        e.eprint()
        