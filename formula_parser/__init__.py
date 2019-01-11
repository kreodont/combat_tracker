import ply.lex as lex
import re
tokens = ('dice', 'plus', 'minus', 'number')
t_dice = r'\d*d|к\d+'
t_plus = r'\+'
t_minus = r'-'
t_number = r'\d+'

t_ignore = ' \r\n\t\f'


def t_error(t):
    t.lexer.skip(1)


lexer = lex.lex(reflags=re.UNICODE | re.DOTALL)
test_string = '6d6 + 5 корова -к6 + 15'
lexer.input(test_string)

while True:
    tk = lexer.token()
    if not tk:
        break
    print(tk)
