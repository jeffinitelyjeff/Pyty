import ast

from logger import Logger
from typecheck import check_expr
from parse_type import PytyType

import typecheck

log = typecheck.log = Logger()

if __name__ == '__main__':
    while True:
        expr = raw_input('Expression: ')

        if expr == 'q' or expr == 'quit':
            break
        else:
            e = ast.parse(expr).body[0].value

        t = PytyType(raw_input('Expected type: '))

        print check_expr(e, t, {})
