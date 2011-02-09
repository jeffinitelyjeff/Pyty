import ast
from epydoc import docparser

from pyty_errors import TypeUnspecifiedError, \
                        TypeIncorrectlySpecifiedError
from pyty_types import PytyMod, PytyStmt, PytyInt, PytyFloat, PytyBool, \
                       PytyExpr

"""
Location for main typechecking function. Will probably import lots of
functions from parser.py.
"""

int_type = PytyInt()
flt_type = PytyFloat()
bool_type = PytyBool()
expr_type = PytyExpr()
stmt_type = PytyStmt()

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
            elif specified_str == "float":
                environment[var] = flt_type
            elif specified_str == "bool":
                environment[var] = bool_type
            else:
                raise TypeIncorrectlySpecifiedError("Type incorrectly " + 
                    "specified as: " + specified_str)


    return environment

def is_variable(node):
    """Returns whether AST node C{node} is a variable."""

    # this is how the AST seems to mark variables
    return isinstance(node, ast.Name) and \
           isinstance(node.ctx, (ast.Store, ast.Load)) and \
           node.id != 'True' and node.id != 'False'

def typecheck(env, node, t):
    """Checks whether the AST tree with C{node} as its root typechecks as type
    C{t} given environment C{env}.

    @type env: C{dict} {C{str}:L{types.PytyType}}.
    @param env: an environment (mapping variable identifiers to types)
    @type node: AST node.
    @param node: an AST node.
    @type t: L{types.PytyType}.
    @param t: a type.
    
    @rtype: C{bool}.
    @return: C{True} if the AST C{node} typechecks as type C{t} given
        environment C{env}.
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
                    raise TypeUnspecifiedError(var = target_name)
                expected_type = env[target_name]
                if not typecheck(env, expr, expected_type):
                    targets_typecheck = False

            return targets_typecheck
        
        # for now, we will treat everything that's not an assignment within a
        # statement as an expression. this replaces the old check of
        # isinstance(node, ast.Expr) which I'm pretty sure did not work as I'd
        # hoped it to, since an expression would actually be represented as a
        # BinOp or BoolOp or w/e in the AST.
        else:
            return typechecks_as_one_of(env, node.value, [int_type, flt_type,
                bool_type])

    elif isinstance(t, PytyInt):
        # This must be checked before the float check, since every integer is
        # also classified as a float
        #
        # To typecheck as an integer, must be a number, a binary operation
        # expression, or the result of a function.
        
        if isinstance(node, ast.Num):
            # number literals are stored as ast.Num objects.
            value = node.n
            return isinstance(value, int)

        if is_variable(node):
            return isinstance(env[node.id], PytyInt)

        elif isinstance(node, ast.BinOp):
            # if the node is a binary operation, then it typechecks if
            # both operands typecheck as ints.
            valid_operators = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)

            if isinstance(node.op, valid_operators): 
                return typecheck(env, node.left, int_type) and \
                       typecheck(env, node.right, int_type)
            else:
                return False

        # TODO
        # elif isinstance(node, function...?)
        # elif isinstance(node, unaryOp...?)

        else:
            # if the node isn't a number literal or a binary operation,
            # or function, then it's not an int.
            return False

    elif isinstance(t, PytyFloat):
        # To typecheck as a float, must be a number, a binary operation
        # expression, or the result of a function.

        if isinstance(node, ast.Num):
            # Num literals are stored as ast.Num objects.
            value = node.n

            # We want ints to typecheck as floats, but this type hierarchy
            # isn't built into python primitives, so isinstance(3, float)
            # returns false.
            return isinstance(value, float) or isinstance(value, int)
               
        elif is_variable(node):
            # Since PytyInt is a subclass of PytyFloat, this will cover ints
            # too.
            return isinstance(env[node.id], PytyFloat)

        elif isinstance(node, ast.BinOp):
            # if the node is a binary operation, then it typechecks if both
            # operands typecheck as floats or ints. Note: because of the type 
            # hierarchy, we check if each operand typechecks as a float, float
            # is a subclass of int, so it will first check if the operand
            # typechecks as an int, and then (if it doesn't typechecks as an
            # int) see if it typechecks as a float.
            valid_operators = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)

            if isinstance(node.op, valid_operators):
                return typecheck(env, node.left, flt_type) and \
                       typecheck(env, node.right, flt_type)
            
            else:
                return False

        # TODO
        # elif isinstance(node, funcction, ...?)
        # elif isinstane(node, unaryOp...?)


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
                and typecheck_each(env, node.values, bool_type)
        
        # TODO These need to be tested
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

def typecheck_each(env, l, t):
    """Checks whether every node in list C{l} typechecks as type C{t} given
    environment C{env}.

    @type env: C{dict} {{C{str}:C{PytyType}}.
    @param env: an environment (mapping variable identifiers to types).
    @type l: C{list} [AST node]
    @param l: a list of AST nodes.
    @type t: L{types.PytyType}.
    @param t: a type.
    
    @rtype: C{bool}.
    @return: C{True} if every node in C{l} typechceks as type C{t} given
        environment C{env}.
    """
    
    for node in l:
        if not typecheck(env, node, t): return False

    return True

def typechecks_as_one_of(env, node, ts):
    """Checks whether C{node} typechecks as one of the types in the list C{ts}.
    
    @type env: C{dict} {{C{str}:C{PytyType}}.
    @param env: an environment (mapping variable identifiers to types).
    @type node: AST node.
    @param node: an AST node.
    @type ts: C{list} [L{types.PytyType}].
    @param ts: a list of types.
    
    @rtype: C{bool}.
    @return: C{True} if C{node} typechecks as one of the types in C{ts} given
        environmetn C{env}.
    """

    for t in ts:
        if typecheck(env, node, t): return True

    # if we're here, then it didn't typecheck as any of the types in ts.
    return False
