import ast
import sys

from logger import Logger
from check import check_mod
from parse_file import parse_type_decs
from ast_extensions import TypeDecASTModule

import check
import parse_file
import infer
log = check.log = parse_file.log = infer.log = Logger()

# Invoked like:
# python pyty.py <source_file.py>

if __name__ == '__main__':
    file_name = sys.argv[1]

    try:
        # FIXME: this is copied from unit_test_core, should be abstracted
        # away somewhere, but don't know the best way to deal with logging.
        with open(file_name, 'r') as f:
            text = f.read()
        untyped_ast = ast.parse(text)
        typedecs = parse_type_decs(file_name)
        typed_ast = TypeDecASTModule(untyped_ast, typedecs)
        if check_mod(typed_ast.tree):
            print "Typechecked correctly!"
        else:
            print "Did not typecheck."

    except IOError as e:
        print "File not found: %s" % e.filename

