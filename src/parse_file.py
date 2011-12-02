import re
import ast
import logging

from ast_extensions import TypeDec, TypeStore, TypeDecASTModule
from ptype import PType
from settings import DEBUG_TYPEDEC_PARSING
from logger import Logger
# from epydoc import docparser ; may need this for functions

log = None

def p_debug(s, cond=True):
    log.debug(s, DEBUG_TYPEDEC_PARSING and cond)

# the \s are regexes for whitespace. the first group contains a regex for valid
# Python variable identifiers; the second group catches anything,
_TYPEDEC_REGEX = r".*#:\s*(?P<id>[a-zA-Z]\w*)\s*:\s*(?P<t>.*)\s*"

def parse_type_decs(filename):
    """Scans through the contents of C{filename} to find lines which contain a
    comment of the form '#: x : int' at the beginning (excluding whitespace) and
    creates a list of L{ast_extensions.TypeDec} nodes.

    TODO: This currently only handles single declarations like '#: x : int', but
    we want it to also handle things like '#: x,y : int' and
    '#: x : int, y : float'.

    TODO: this will eventually have to be more sophisticated to handle better
    integration with epydoc (ie, we shouldn't expect users to specify method
    paramater types with variable docstrings; they should be able to use the
    standard epydoc tag '@type'). This can be solved by either directly calling
    epydoc at some point, but this seems mostly trivial and not worth forcing
    clients of the applciation to install all 700 MB of the epydoc dependencies.
    """

    tdecs = []
    lineno = 0

    p_debug("--- v Typedec parsing v ---")

    for l in open(filename, 'r'):
        # move to next line
        lineno += 1

        m = re.match(_TYPEDEC_REGEX, l)

        p_debug(" tdec --> " + l[:-1], m)
        p_debug("          " + l[:-1], not m)

        if m:
            var_name = m.group('id')
            type_spec = m.group('t').split('#')[0].strip()

            tdec = parse_type_dec(l, lineno, var_name, type_spec)
            tdecs.append(tdec)

    p_debug("--- ^ Typedec parsing ^ ---")

    # FIXME: Function stuff
    # p_debug("--- v Function typedec parsing v ---")

    # d = docparser.parse_docs(filename)

    # for v in filter(lambda x: --IS X A FUNCTION VARIABLE?--, d.variables):
    #     docstring = d.variables[v].value.docstring

    #     # partypes is going to be a list of 2-tuples of parameter name and type
    #     partypes = []
    #     for line in filter(lambda x: re.match(r'\s*@type (.*): (.*)', x),
    #                        docstring.split('\n')):
    #         groups = re.match(r'\s*@type (.*): (.*)', line).groups()
    #         partypes.append((groups[0], groups[1]))

    #     rtype_line = filter(lambda x: re.match(r'\s*@rtype: .*', x),
    #            docstring.split('\n'))[0]
    #     rtype = re.match(r'\s*@rtype: (.*)', rtype_line).groups()[0]

    #     tdecs.append(make_function_tdec(partypes, rtype))

    # p_debug("--- ^ Function typedec parsing ^ ---")

    return tdecs

# FIXME: Function stuff
# def make_function_tdec(partypes, rtype, lineno, func_name):
#     # FIXME: this should be somehow built into the parser; this is a hack.
#     t = TypeSpecParser.parse("(" + ', '.join(partype) + ") -> " + rtype)

#     return TypeDec([func_name], t, lineno)



def parse_type_dec(line, lineno, var_name, type_spec):
    """Constructs a L{ast_extensions.TypeDec} from the type declaration in the
    provided line. The name of the variable and the name of the type are passed
    since they are stored when matching the typedec regex against the line and
    it would be wasteful to discard that information.

    @type line: str
    @param line: the line of source code containing the type declaration.
    @type lineno: int
    @param lineno: the index of this line in the orginial source code file.
    @type var_name: str
    @param var_name: the name of the identifier whose type is being declared.
    @type type_name: str
    @param type_name: the name of the type which is being declared.
    @rtype: L{ast_extensions.TypeDec}
    @return: a L{ast_extensions.TypeDec} node for the declaration in the given
        line.
    """

    col = line.index(var_name)
    name_node = ast.Name(ctx=TypeStore(), id=var_name, lineno=lineno,
                         col_offset=col)

    col_offset = line.index("#:")

    return TypeDec([name_node], PType(type_spec), lineno,
                   col_offset)
