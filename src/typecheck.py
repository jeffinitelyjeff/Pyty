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
    
    node_info = get_node_info(node)
    
    if t == "mod":
        # typecheck as a module if the node is a valid expression node or a
        # list of valid statement nodes.
        # -- implement --

    if t == "stmt":
        if node_info['node_type'] == "Assign":
            targets = node_info['targets']
            expr = node_info['value']

            targets_typecheck = True

            for target in targets:
                # this checks if the expression typechecks as the type of each
                # target. this seems a little redundant, since the expression
                # is always the same type, so the targets should all have the
                # same type, but it should handle the case when expr is 5 and
                # one target is specified as an int and one as a float.
                raise VariableTypeUnspecifiedError if target not in env
                expected_type = env[target]
                targets_typecheck &= typecheck(env, expr, expected_type)

            return targets_typecheck

        # -- check if valid expression node --
                

    if t == "int":
        if node_info['node_type'] == "Num":
            value = node_info['n']
            return type(value) is int

        if node_info['node_type'] == "BinOp":
            # this only works when just ints are considered, because all
            # binary operations have the same typechecking rules in that case;
            # will have to greatly expand this once floats are considered.
            left = node_info[1]
            right = node_info[2]
            return typecheck(env, left, "int") and typecheck(env, right, "int")

    if t == "bool":
        # typecheck as a bool if the node is and or or and both arguments are
        # also bools.
        # -- implement --


    # are these really only the 4 different types that would be typechecked
    # against currently? still confused about whether operator could be a type.
    # loop through various cases of node type in each type
