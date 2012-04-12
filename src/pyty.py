import ast
import sys

from optparse import OptionParser, OptionGroup

from logger import Logger
from check import check_mod
from infer import infer_expr
from ptype import PType
from parse_file import parse_type_decs
from ast_extensions import TypeDecASTModule

import check
import parse_file
import infer
log = check.log = parse_file.log = infer.log = Logger()

# Invoked like:
# python pyty.py <source_file.py>

usage = "usage: %prog [options]\n\nDo not mix options from different modes."

parser = OptionParser(usage=usage)

f_group = OptionGroup(parser, "File Mode",
                      "Use Pyty to typecheck source code files.")
f_group.add_option("-f", "--file", dest="filename",
                   help="file to typecheck", metavar="FIL")
parser.add_option_group(f_group)

e_group = OptionGroup(parser, "Expression Mode",
                      "Use Pyty to typecheck expressions (under the "
                      "empty environment). Both options are required.")
e_group.add_option("-e", "--expr", dest="expr",
                   help="string of expression", metavar="EXP")
e_group.add_option("-t", "--type", dest="type",
                   help="type to typecheck against", metavar="TYP")
parser.add_option_group(e_group)

i_group = OptionGroup(parser, "Inference Mode",
                      "Use Pyty to infer the type of an expression (under the "
                      "empty environment).")
i_group.add_option("-i", "--inf", dest="infer_expr",
                  help="string of expression", metavar="EXP")
parser.add_option_group(i_group)

(opt, args) = parser.parse_args()

if opt.filename and not opt.expr and not opt.type and not opt.infer_expr:
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

elif opt.expr and opt.type and not opt.filename and not opt.infer_expr:
    e = ast.parse(opt.expr).body[0].value
    t = PType(opt.type)
    template = ("YES! %s typechecks as type %s" if infer_expr(e, t, {}) else
                "NO! %s does not typechecka s type %s")
    print template % (opt.expr, opt.type)

elif opt.infer_expr and not opt.filename and not opt.expr and not opt.type:
    e = ast.parse(opt.infer_expr).body[0].value
    print "%s -- is the inferred type of %s" % (infer_expr(e, {}),
                                                opt.infer_expr)
    
else:
    parser.print_help()

