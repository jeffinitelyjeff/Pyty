import ast

from logger import Logger
from check import check_expr
from infer import infer_expr
from ptype import PType

import check

log = check.log = Logger()
infer = False

if __name__ == '__main__':
    while True:
        inp = raw_input(('Infer' if infer else 'Check') + ' expression: ')

        if inp == 'i' or inp == 'infer':
            infer = True
            continue
        elif inp == 'c' or inp == 'check':
            infer = False
            continue
        elif inp == 'q' or inp == 'quit':
            break
        else:
            e = ast.parse(inp).body[0].value

        if infer:
            print infer_expr(e, {})
        else:
            t = PType(raw_input('Expected type: '))
            print check_expr(e, t, {})
