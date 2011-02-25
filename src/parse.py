import re

from epydoc import docparser

import base_types
from errors import TypeIncorrectlySpecifiedError

def parse_type_declarations(filename):
    return _type_parser(filename)

def _type_parser(filename):
    """Scans through the contents of C{filename} to find comments of the form
    '#: x : int' and creates an environment dictionary of those types.

    Note: will eventually have to be much more sophisticated to handle better
    integration with epydoc."""

    env = {}

    for l in open(filename, 'r'):
        comment_form = r"#: (%s) : (%s)"
        
        variable_regex = r"[\w\d]*"
        # we allow the type string to be anything here because we want it to
        # match and then throw an error instead of not matching as a variable
        # declaration.
        loose_type_regex = r".*"
        strict_type_regex = base_types.type_regex
        
        regex = comment_form % (variable_regex, loose_type_regex)

        m = re.match(regex, l)

        if m != None:
            g = m.groups()
            var_name = g[0]
            type_name = g[1]

            if re.match(strict_type_regex, type_name) == None:
                raise TypeIncorrectlySpecifiedError("Type incorrectly " +
                    "specified as: " + type_name)

            env[var_name] = type_name

    return env

##### NOW DEFUNCT
def _type_parser_epydoc(filename):
    """Returns a dictionary mapping variables in the file C{filename} with
    their types defined in docstrings."""

    # NOTE currently only deals with "#:" docstrings (will also be messed up
    # because functions are considered variables in epydoc)

    d = docparser.parse_docs(filename)

    env = {}

    for v in d.variables:
        # this seems to be the most straightforward way of checking whether a
        # variable has a docstring or not.
        if isinstance(d.variables[v].docstring, unicode):
            # get str of form 'var_name : type'
            s = d.variables[v].docstring.strip()
            # get str of form ': type'
            s = s[len(v):].strip()
            # get str of form 'type'
            s = s[1:].strip()

            try:
                env[v] = getattr(base_types, s+'_type')
            except AttributeError:
                raise TypeIncorrectlySpecifiedError("Type incorrectly " +
                    "specified as: " + s)
            
    return env
