from epydoc import docparser

import base_types
from errors import TypeIncorrectlySpecifiedError

def parse_type_declarations(filename):
    return _type_parser_epydoc(filename)

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
