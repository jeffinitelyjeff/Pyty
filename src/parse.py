import re
import ast
import logging

from ast_extensions import TypeDec, TypeStore, TypeDecASTModule, EnvASTModule
from pyty_types import PytyType
from settings import *
from logger import Logger

log = None

# the \s are regexes for whitespace. the first group contains a regex for valid
# Python variable identifiers; the second group catches anything, and then this
# second group is validated against a regex for valid type names.
_TYPEDEC_REGEX = r"\s*#:\s*(?P<id>[a-zA-Z]\w*)\s*:\s*(?P<t>.*)\s*"
_TYPENAME_REGEX = PytyType.type_regex

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

    for l in open(filename, 'r'):
        # move to next line
        lineno += 1

        m = re.match(_TYPEDEC_REGEX, l)

        if m:
            log.debug(" tdec --> " + l[:-1], DEBUG_TYPEDEC_PARSING)
        else:
            log.debug("          " + l[:-1], DEBUG_TYPEDEC_PARSING)

        if m != None:
            var_name = m.group('id')
            type_name = m.group('t')

            if re.match(_TYPENAME_REGEX, type_name) == None:
                raise TypeIncorrectlySpecifiedError("Type incorrectly " +
                    "specified as: " + type_name)

            tdec = parse_type_dec(l, lineno, var_name, type_name)
            tdecs.append(tdec)

    return tdecs

def parse_type_dec(line, lineno, var_name, type_name):
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

    return TypeDec([name_node], PytyType(type_name), lineno, col_offset)
        
    

          

    

## import re

## import base_types
## from errors import TypeIncorrectlySpecifiedError

## def parse_type_declarations(filename):
##     return _type_parser(filename) 

## def _type_parser(filename):
##     """Scans through the contents of C{filename} to find comments of the form
##     '#: x : int' and creates an environment dictionary of those types.

##     Note: will eventually have to be much more sophisticated to handle better
##     integration with epydoc."""

##     env = {}

##     for l in open(filename, 'r'):
##         comment_form = r"#: (%s) : (%s)"
        
##         variable_regex = r"[\w\d]*"
##         # we allow the type string to be anything here because we want it to
##         # match and then throw an error instead of not matching as a variable
##         # declaration.
##         loose_type_regex = r".*"
##         strict_type_regex = base_types.type_regex
        
##         regex = comment_form % (variable_regex, loose_type_regex)

##         m = re.match(regex, l)

##         if m != None:
##             g = m.groups()
##             var_name = g[0]
##             type_name = g[1]

##             if re.match(strict_type_regex, type_name) == None:
##                 raise TypeIncorrectlySpecifiedError("Type incorrectly " +
##                     "specified as: " + type_name)

##             env[var_name] = type_name

##     return env

## ##### NOW DEFUNCT
## def _type_parser_epydoc(filename):
##     """Returns a dictionary mapping variables in the file C{filename} with
##     their types defined in docstrings."""

##     # NOTE currently only deals with "#:" docstrings (will also be messed up
##     # because functions are considered variables in epydoc)

##     d = docparser.parse_docs(filename)

##     env = {}

##     for v in d.variables:
##         # this seems to be the most straightforward way of checking whether a
##         # variable has a docstring or not.
##         if isinstance(d.variables[v].docstring, unicode):
##             # get str of form 'var_name : type'
##             s = d.variables[v].docstring.strip()
##             # get str of form ': type'
##             s = s[len(v):].strip()
##             # get str of form 'type'
##             s = s[1:].strip()

##             try:
##                 env[v] = getattr(base_types, s+'_type')
##             except AttributeError:
##                 raise TypeIncorrectlySpecifiedError("Type incorrectly " +
##                     "specified as: " + s)
            
##     return env

