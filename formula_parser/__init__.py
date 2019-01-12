import ply.lex as lex
import re
tokens = ('dice', 'plus', 'minus', 'number')
t_dice = r'\d*(d|к|д)\d+'
t_plus = r'\+'
t_minus = r'-'
t_number = r'\d+'

t_ignore = ' \r\n\t\f'


def t_error(t):
    t.lexer.skip(1)


lexer = lex.lex(reflags=re.UNICODE | re.DOTALL)
# test_string = '6d6 + 5 корова -к6 + 15 +-ddd20'
# lexer.input(test_string)


def parse_formula_string(string):
    tokens_ = []
    lexer.input(string)
    while True:
        tk = lexer.token()
        if not tk:
            break
        tokens_.append(tk)
    return tokens_
