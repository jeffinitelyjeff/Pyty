import ast
import sys

from optparse import OptionParser, OptionGroup

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

parser = OptionParser()

f_group = OptionGroup(parser, "File Mode",
                      "Options to use Pyty to typecheck source code files. Do "
                      "not use any Expression Mode options along with these.")
f_group.add_option("-f", "--file", dest="filename",
                   help="file to typecheck", metavar="FIL")
parser.add_option_group(f_group)

e_group = OptionGroup(parser, "Expression Mode",
                      "Options to use Pyty to typecheck expressions (under the "
                      "empty environment). Both options are required; do not use "
                      "any File Mode options along with these.")
e_group.add_option("-e", "--expr", dest="expr",
                   help="string of expression", metavar="EXP")
e_group.add_option("-t", "--type", dest="type",
                   help="type to typecheck against", metavar="TYP")
parser.add_option_group(e_group)

(opt, args) = parser.parse_args()

if opt.filename and not opt.expr and not opt.type:
    file_name = opt.filename

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

elif opt.expr and opt.type and not opt.filename:
    print "yay"
    # FIXME

else:
    parser.print_help()

