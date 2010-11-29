"""
Location for main typechecking function. Will probably import lots of
functions from parser.py.
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
    
    if isinstance(t, PytyMod):
        # typecheck as a module if the node is a valid expression node or a
        # list of valid statement nodes.
        # -- implement --

    if isinstance(t, PytyStmt):
        # this isinstance doesn't actually work
        if isinstance(node, Assign):
            targets = node.targets
            expr = node.value

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
                

    if isinstance(t, PytyInt):
        # this isinstance doesn't actaully work
        if isinstance(node, Num):
            value = node.n
            return isinstance(value, int)

        # this isinstance doesn't actually work
        if isinstance(node, BinOp):
            # this only works when just ints are considered, because all
            # binary operations have the same typechecking rules in that case;
            # will have to greatly expand this once floats are considered.
            left = node.left
            right = node.right
            return typecheck(env, left, "int") and typecheck(env, right, "int")

    if isinstance(t, PytyBool):
        # typecheck as a bool if the node is and or or and both arguments are
        # also bools.
        # -- implement --


    # are these really only the 4 different types that would be typechecked
    # against currently? still confused about whether operator could be a type.
    # loop through various cases of node type in each type
