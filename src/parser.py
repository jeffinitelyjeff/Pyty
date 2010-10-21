import sys
import compiler
import ast
from parser_helper import get_ast
from parser_helper import AssignmentBuilder

_PRACTICE_FILE = "test.py"

def main(argv):
    try:
        ast0 = get_ast(argv[1])
    except IndexError:
        ast0 = get_ast(_PRACTICE_FILE)

    variable_dict = {}
    variable_walker = AssignmentBuilder(variable_dict)
    variable_walker.generic_visit(ast0)
    
    print variable_dict

    return 0

if __name__=='__main__':
    sys.exit(main(sys.argv))
