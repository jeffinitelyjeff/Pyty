import ast
from epydoc import docparser

from pyty_errors import TypeUnspecifiedError, \
                        TypeIncorrectlySpecifiedError
from pyty_types import PytyMod, PytyStmt, PytyInt, PytyBool, PytyExpr

"""
Location for main typechecking function. Will probably import lots of
functions from parser.py.
"""

_DEBUG = True

int_type = PytyInt()
bool_type = PytyBool()
expr_type = PytyExpr()
stmt_type = PytyStmt()

def debug(string):
    """Prints string if global variable _DEBUG is true, otherwise
    does nothing
    
    @type string: C{str}.
    @param string: a string.
    """

    if _DEBUG: 
        print string

def debug_c(test, string):
    """Prints string if debugging is on and test is C{True}.

    @type test: C{bool}.
    @param test: a boolean test.
    @type string: C{str}.
    @param string: a string.
    """

    if test and _DEBUG: 
        debug(string)

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

def is_varibale(node):
    """Returns whether AST node C{node} is a variable."""

    # this is how the AST seems to mark variables
    return isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)

def typecheck(env, node, t):
    """Checks whether the AST tree with C{node} as its root typechecks as type
    C{t} given environment C{env}.

    @type env: C{dict} {C{str}:L{types.PytyType}}.
    @param env: an environment (mapping variable identifiers to types)
    @type node: AST node.
    @param node: an AST node.
    @type t: L{types.PytyType}.
    @param t: a type.
    """

    # mod
    # - module(stmt* body)
    if isinstance(t, PytyMod):
        
        if isinstance(node, ast.Module):
            # If node is a module, then it must have a list of statements
            # which must typecheck as statements.
            statements = node.body
            statements_typecheck = True

            for statement in statements:
                if not typecheck(env, statement, stmt_type):
                    statements_typecheck = False

            return statements_typecheck

        else:
            # If node is not a module, then it's not a module... this seems a
            # little stupid. 
            return False

    # stmt
    # - assign(expr* targets, expr value)
    # - expr(expr value)
    # - if(expr test, stmt* body, stmt* orelse)
    # - while(bool test, stmt* body, stmt* orelse)
    # - for(variable target, expr iter, stmt* body, stmt* orelse)
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

        # Crude implementation of conditionals / blocks.

        #elif isinstance(node, ast.If):
        #    debug("test: %s" % typecheck(env, node.test, bool_type))
        #    debug("body: %s" % typecheck_list(env, node.body, stmt_type))
        #    debug("orelse: %s" % typecheck_list(env, node.orelse, stmt_type))

        #    return \
        #        typecheck(env, node.test, bool_type) \
        #        and typecheck_list(env, node.body, stmt_type) \
        #        and typecheck_list(env, node.orelse, stmt_type)

        #elif isinstance(node, ast.While):
        #    return \
        #        typecheck(env, node.test, bool_type) \
        #        and typecheck_list(env, node.body, stmt_type) \
        #        and typecheck_list(env, node.orelse, stmt_type)

        #elif isinstance(node, ast.For):
        #    return \
        #        is_variable(node.target) \
        #        and typecheck(env, node.iter, expr_type) \
        #        and typecheck_list(env, node.body, stmt_type) \
        #        and typecheck_list(env, node.orelse, stmt_type)

        elif isinstance(node, ast.Expr):
            return typecheck(env, node.value, expr_type)

        else:
            return False
               

    elif isinstance(t, PytyExpr):
        return \
            typecheck(env, node, int_type) \
            or typecheck(env, node, bool_type)


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

            return \
                isinstance(node.op, valid_operators) \
                and typecheck_list(env, node.values, bool_type)
           
        elif isinstance(node, ast.Compare):
            # right now, we're only handling the case of compares with just
            # two expressions (like x > y, x == y, etc.)

            valid_operators = (ast.Gt, ast.GtE, ast.Lt, ast.LtE, ast.Eq)

            return \
                isinstance(node.ops[0], valid_operators) \
                and (typecheck(env, node.left, int_type)
                     and typecheck(env, node.comparators[0], int_type)) \
                or (typecheck(env, node.left, bool_type)
                     and typecheck(env, node.comparators[0], bool_type))

        else:
            # if the node isn't a bool literal or a boolean operation, then
            # it's not a bool.
            return False

def typecheck_list(env, l, t):
    """Checks whether every node in list C{l} typechecks as type C{t} given
    environment C{env}.

    @type env: C{dict} {{C{str}:C{PytyType}}.
    @param env: an environment (mapping variable identifiers to types).
    @type l: C{list} [AST node]
    @param l: a list of AST nodes.
    @type t: L{types.PytyType}.
    @param t: a type.
    """
    
    for node in l:
        if not typecheck(env, node, t): return False

    return True

