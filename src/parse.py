from epydoc import docparser
from types import base_types

# creates an instance of each type defined in types.base_types.
#   all have form like: int_type, float_type, bool_type.
# this also handles importing the necessary type classes.
for t in base_types:
    exec("from types import Base" + t.capitalize())
    exec(t + "_type = Base" + t.capitalize() + "()")

def parse_type_declarations(filename):
    """Returns a dictionary mapping variables in the file C{filename} with
    their types defined in docstrings."""

    # NOTE currently only deals with "#:" docstrings (will also be messed up
    # because functions are considered variables in epydoc)

    d = docparser.parse_docs(filename)

    env = {}

    for v in d.variables:
        # this seems to be the most straightforward way of checking whether a
        # variable has a docstring or not.
        if hasattr(d.variables[v], 'docstring'):

            # get str of form 'var_name : type'
            s = d.variables[v].docstring.strip()
            # get str of form ': type'
            s = s[len(v):].strip()
            # get str of form 'type'
            s = s[1:].strip()

            
