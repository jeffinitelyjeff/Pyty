import ast
from epydoc import docparser

from pyty_errors import TypeUnspecifiedError, \
                        TypeIncorrectlySpecifiedError
from pyty_types import PytyMod, PytyStmt, PytyInt, PytyBool

"""
Location for main typechecking function. Will probably import lots of
functions from parser.py.
"""

int_type = PytyInt()
bool_type = PytyBool()

def parse_type_declarations(filename):
    """Returns a dictionary mapping variables in file filenmae with their
    types defined in docstrings.

    @type filename: C{str}.
    @param filename: name of file to be parsed.
    """

    # XXX CURRENTLY ONLY DEALS WITH "#:" DOCSTRINGS (WILL ALSO GET MESSED UP
    # CUZ FUNCTIONS ARE CONSIDERED VARIABLES BY EPYDOC)

    d = docparser.parse_docs(filename)


    environment = {}

    for var in d.variables:
        # this seems to be the most straightforward way of checking whether a
        # variable has a docstring or not.
        if 'docstring' in d.variables[var].__dict__:
          
            # get string of form 'var_name : type'
            specified_str = d.variables[var].docstring.strip()
            # get string of form ': type'
            specified_str = specified_str[len(var):].strip()
            # get string of form 'type'
            specified_str = specified_str[1:].strip()

            if specified_str == "int":
                environment[var] = int_type
            elif specified_str == "bool":
                environment[var] = bool_type
            else:
                raise TypeIncorrectlySpecifiedError()


    return environment

def typecheck(env, node, t):
    """Checks whether the AST tree with C{node} as its root typechecks as type
    C{t} given environment C{env}.

    @type env: C{dict} {C{str}:C{str}}.
    @param env: an environment (mapping variable identifiers to types)
    @type node: AST node.
    @param node: an AST node.
    @type t: L{types.PytyType}.
    @param t: a type.
    """
    
    if isinstance(t, PytyMod):
        
        if isinstance(node, ast.Module):
            # If node is a module, then it must have a list of statements
            # which must typecheck as statements.
            statements = node.body
            statements_typecheck = True
            stmt_type = PytyStmt()

            for statement in statements:
                if not typecheck(env, statement, stmt_type):
                    statements_typecheck = False

            return statements_typecheck

        else:
            # If node is not a module, then it's not a module... this seems a
            # little stupid. 
            return False

    elif isinstance(t, PytyStmt):
        
        if isinstance(node, ast.Assign):
            # If node is an assign, then the expression must correctly
            # typecheck as the types of each of the assign targets.
            expr = node.value

            targets_typecheck = True
 
            for target in node.targets:
                # targets are ast.Name objects so need to get the id of the
                # target (the name of the variable).
                target_name = target.id

                if target_name not in env: 
                    raise TypeUnspecifiedError()
                expected_type = env[target_name]
                if not typecheck(env, expr, expected_type):
                    targets_typecheck = False

            return targets_typecheck

        elif isinstance(node, ast.Expr):
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
                

    elif isinstance(t, PytyInt):
        
        if isinstance(node, ast.Num):
            # number literals are stored as ast.Num objects.
            value = node.n
            return isinstance(value, int)

        elif isinstance(node, ast.BinOp):
            # if the node is a binary operation, then it typechecks if
            # both operands typecheck as ints.
            valid_operators = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)

            if isinstance(node.op, valid_operators): 
                return typecheck(env, node.left, int_type) and \
                       typecheck(env, node.right, int_type)
            else:
                return False

        else:
            # if the node isn't a number literal or a binary operation,
            # then it's not an int.
            return False

    elif isinstance(t, PytyBool):
        
        if isinstance(node, ast.Name):
            # boolean literals are stored as ast.Name objects with ids of
            # "True" or "False."
            return (node.id == "True" or node.id == "False")

        elif isinstance(node, ast.BoolOp):
            # if node is a boolean operation, then it typechecsk if all values
            # typechecks as bools and the operator is a valid operator.

            valid_operators = (ast.And, ast.Or)

            if not isinstance(node.op, valid_operators):
                # operator is invalid.
                return False
            else:
                # operator is valid.
                values_typecheck = True

                for value in node.values:
                    if not typecheck(env, value, bool_type):
                        values_typecheck = False

                return values_typecheck
            
        else:
            # if the node isn't a bool literal or a boolean operation, then
            # it's not a bool.
            return False

