import ply.lex as lex
import re
import typing
tokens = ('dice', 'sign', 'number')
t_dice = r'\d*(d|к|д)\d+'
t_sign = r'\+|-'
t_number = r'\d+'

t_ignore = ' \r\n\t\f'


def t_error(t):
    t.lexer.skip(1)


lexer = lex.lex(reflags=re.UNICODE | re.DOTALL)
# test_string = '6d6 + 5 корова -к6 + 15 +-ddd20'
# lexer.input(test_string)


def parse_formula_string(string) -> typing.List[lex.LexToken]:
    string = string.replace(' ', '').strip()  # making sure there is no spaces in string
    tokens_ = []
    lexer.input(string)
    while True:
        tk = lexer.token()
        if not tk:
            break
        tokens_.append(tk)
    return tokens_


if __name__ == '__main__':
    for tk_ in parse_formula_string('2d6 + 12'):
        print(getattr(tk_, 'type'), getattr(tk_, 'value'))
