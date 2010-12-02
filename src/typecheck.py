import ast

from pyty_errors import VariableTypeUnspecifiedError
from pyty_types import PytyMod, PytyStmt, PytyInt, PytyBool

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

    int_type = PytyInt()
    bool_type = PytyBool()
    
    if isinstance(t, PytyMod):
        
        if isinstance(node, ast.Module):
            # If node is a module, then it must have a list of statements
            # which must typecheck as statements.
            statements = node.body
            statements_typecheck = True
            stmt_type = PytyStmt()

            for statement in statements:
                statements_typecheck &= typecheck(env, statement, stmt_type)

            return statements_typecheck

        else:
            # If node is not a module, then it's not a module... this seems a
            # little stupid. 
            return False

    if isinstance(t, PytyStmt):
        
        if isinstance(node, ast.Assign):
            # If node is an assign, then the expression must correctly
            # typecheck as the types of each of the assign targets.
            targets = node.targets
            expr = node.value

            targets_typecheck = True

            for target in targets:
                if target not in env: raise VariableTypeUnspecifiedError()
                expected_type = env[target]
                targets_typecheck &= typecheck(env, expr, expected_type)

            return targets_typecheck

        if isinstance(node, ast.Expr):
            # If node is an expression, then its value must either typecheck 
            # as an int or as a bool.
            val = node.value
            if typecheck(env, val, int_type):
                return True
            elif typecheck(env, val, bool_type):
                return True
            else:
                return False

        else:
            # If the node isn't an assign or an expression, it's not a
            # statement.
            return False
                

    if isinstance(t, PytyInt):
        # this isinstance doesn't actaully work
        if isinstance(node, ast.Num):
            value = node.n
            return isinstance(value, int)

        # this isinstance doesn't actually work
        if isinstance(node, ast.BinOp):
            # this only works when just ints are considered, because all
            # binary operations have the same typechecking rules in that case;
            # will have to greatly expand this once floats are considered.
            left = node.left
            right = node.right
            return typecheck(env, left, int_type) and typecheck(env, right,
                    int_type)

    if isinstance(t, PytyBool):
        # typecheck as a bool if the node is and or or and both arguments are
        # also bools.
        # -- implement --
        return False # XXX


    # are these really only the 4 different types that would be typechecked
    # against currently? still confused about whether operator could be a type.
    # loop through various cases of node type in each type
