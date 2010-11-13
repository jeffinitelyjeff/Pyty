"""
Location for main typechecking function. Will probably import lots of
functions from parser.py.

NOTE: Currently, types are stored as strings. This will eventually be replaced
with a class hierarchy representing types eventually.
"""


def typecheck(env, node, t):
    """Checks whether the AST tree with C{node} as its root typechecks as type
    C{t} given environment C{env}.

    @type env: C{dict} {C{str}:C{str}}.
    @param env: an environment (mapping variable identifiers to types)
    @type node: AST node.
    @param node: an AST node.
    @type t: C{str}.
    @param t: a type.
    """
    
    if t == "mod":
        # implement
        pass

    if t == "stmt":
        # implement
        pass

    if t == "int":
        # implement
        pass

    if t == "bool":
        # implement
        pass

    # are these really only the 4 different types that would be typechecked
    # against currently? still confused about whether operator could be a type.
    # loop through various cases of node type in each type
