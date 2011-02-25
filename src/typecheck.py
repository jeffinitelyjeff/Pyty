import ast
from epydoc import docparser

from errors import TypeUnspecifiedError, \
                   ASTTraversalError
from base_types import *

# ---------------------------------------------------------------------------
# HELPER FUNCTIONS ----------------------------------------------------------
# ---------------------------------------------------------------------------

def env_get(env, v):
    """Returns the type of the variable given by AST node C{v} in environment
    C{env}. Abstracts away needing to get the variable's name in order to look
    it up in the environment dictionary. Also throws a TypeUnspecifiedError if
    C{v} is not in C{env}."""

    # make sure the variable is in the environment
    if v.id not in env:
        raise TypeUnspecifiedError(var=v.id,env=env)
    
    # return the type stored in the environment
    return env[v.id]

def is_node_type(node, ast_node_type):
    """Raises an ASTTraversalError if C{node} is not the right
    C{ast_node_type}; otherwise, returns C{True}."""

    found = node.__class__.__name__
    return found == ast_node_type

def call_function(fun_name, *args, **kwargs):
    return globals()[fun_name](*args, **kwargs)


# ---------------------------------------------------------------------------
# GENERAL CHECKING FUNCTIONS ------------------------------------------------
# ---------------------------------------------------------------------------

def check_mod(node, env):
    """Checks whether the AST node given by C{node} typechecks as a module
    with environment C{env}."""

    if not isinstance(node, ast.Module):
        return False

    for s in node.body:
        if not check_stmt(s, env):
            return False
    return True

def check_stmt(stmt, env):
    """Checks whether the AST node given by C{node} typechecks as a statement.
    The requirements for typechecking as a statement depend on what kind of
    statement C{node} is, and so this function calls one of several functions
    which typecheck C{node} as the specific kind of statement. The function to
    call is generated from the class name of C{node}."""

    n = get_stmt_func_name(stmt.__class__.__name__)

    # if we get a KeyError, then we're inspecting an AST node that is not in
    # the subset of the language we're considering (note: the subset is
    # defined as whatever there are check function definitions for).
    try:
        return call_function(n, stmt, env)
    except KeyError:
        return False

def check_expr(expr, t, env):
    """Checks whether the AST expression node given by C{node} typechecks as
    an expression of type C{t}. The requirements of typechecking depend on the
    kind of expression C{node} is, and so this function calls one of several
    functions which typecheck C{code} as the specific kind of expression. The
    function to call is generated from the class name of C{node}."""

    n = get_expr_func_name(expr.__class__.__name__)
    
    # if we get a KeyError, then we're inspecting an AST node that is not in
    # the subset of the language we're considering (note: the subset is
    # defined as whtaever there are check function definitions for).
    try:
        return call_function(n, expr, t, env)
    except KeyError:
        return False
    

# ---------------------------------------------------------------------------
# STATEMENT CHECKING FUNCTIONS ----------------------------------------------
# ---------------------------------------------------------------------------
#   Valid statement types are:
#   = Done ------------------------------------------------------------------
#    - Assign(expr* targets, expr value)
#   = To Do -----------------------------------------------------------------
#    - FunctionDef(identifier name, arguments args, stmt* body, expr*
#       decorator_list)
#    - ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
#    - Return(expr? value)
#    - Delete(expr* targets)
#    - AugAssign(expr target, operator op, expr value)
#    - Print(expr? dest, expr* values, bool nl)
#    - For(expr test, expr iter, stmt* body, stmt* orelse)
#    - While(expr test, stmt* body, stmt* orelse)
#    - If(expr test, stmt* body, stmt* orelse)
#    - With(expr context_expr, expr? optional_vars, stmt* body)
#    - Raise(expr? type, expr? inst, expr? tback)
#    - TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
#    - TryFinally(stmt* body, stmt* finalbody)
#    - Assert(expr test, expr? msg)
#    - Import(alias* names)
#    - ImportFrom(identifier? module, alias* names, int? level)
#    - Pass
#    - Break
#    - Continue

def get_stmt_func_name(stmt_type):
    return "check_%s_stmt" % stmt_type

def check_Assign_stmt(stmt, env):
    """Checks whether the AST node given by C{node} typechecks as an
    assignment statement. This requires that the expression on the (far) right
    of the equal signs must typecheck as each of the assign targets. The
    expression can typecheck as multiple different types because of
    subtyping.
    NOTE: Currently, this only checks assignments of the form:
        a = b = 5
    and does not handle assigning to lists or tuples."""

    e = stmt.value

    # return False if the expression doesn't match with one of the targets
    for v in stmt.targets:
        # ensure that the variables are appearing with "store" contexts, ie
        # that they are being assigned to and not referenced. this really
        # shouldn't be a problem, but this is just to be safe.
        if not isinstance(v.ctx, ast.Store):
            raise ASTTraversalError(msg="Targets in assignment do not have" + 
                " proper ctx's") 

        t = env_get(env, v)
        if not check_expr(e, t, env):
            return False

    # return True if we reached here, meaning that it matched with all targets
    return True

def check_If_stmt(stmt, env):
    """Checks whether the AST node given by C{node} typechceks as an if
    statement. This requires that the test typecheck as a bolean and that the
    body and orelse branches both typecheck as lists of statements."""

    test = stmt.test
    body = stmt.body
    orelse = stmt.orelse

    # make sure the test typechecks as aboolean
    if not check_expr(test, bool_type, env):
        return False

    # make sure each statement in body typechecks as a statement
    for s in body:
        if not check_stmt(s, env):
            return False

    # make sure each statement in orelse typechceks as a statement
    for s in orelse:
        if not check_stmt(s, env):
            return False

    # if nothing has failed to typecheck, then the statement as a whole
    # typechecks.
    return True

# ---------------------------------------------------------------------------
# EXPRESSION CHECKING FUNCTIONS ---------------------------------------------
# ---------------------------------------------------------------------------
#   Valid expression types are:
#   = Done ------------------------------------------------------------------
#    - Num(object n)
#    - Name(identifier id, expr_context ctx)
#    - BinOp(expr left, operator op, expr right)
#    - Compare(expr left, cmpop* ops, expr* comparators)
#   = To Do -----------------------------------------------------------------
#    - BoolOp(boolop op, expr* values)
#    - UnaryOp(unaryop op, expr operand)
#    - Lambda(arguments args, expr body)
#    - IfExp(expr test, expr body, expr orelse)
#    - Dict(expr* keys, expr* values)
#    - Set(expr* elts)
#    - List(expr* elts, expr_context ctx)
#    - Tuple(expr* elts, expr_context ctx)
#    - Call(expr func, expr* args, keyword* keywords, expr? starargs,
#       expr? kwargs)
#    - Str(string s)

def get_expr_func_name(expr_type):
    return "check_%s_expr" % expr_type

def check_Num_expr(num, t, env):
    """Checks whether the AST expression node given by C{num} typechecks as a
    num expression (ie, a numeric literal) of type C{t}."""

    if not isinstance(num, ast.Num):
        return False
    
    n = num.n

    if is_int(t):
        return isinstance(n, int)
    if is_float(t):
        return isinstance(n, float) or isinstance(n, int)
    else:
        return False

def check_Name_expr(name, t, env):
    """Checks whether the AST expression node given by C{name} typechecks as a
    name expression. Name expressions are used for variables and for boolean
    literals."""

    if not isinstance(name, ast.Name):
        return False

    if not isinstance(name.ctx, ast.Load):
        raise ASTTraversalError(msg="Referenced variables or booleans do" +
            " not have proper ctx's")
    
    id = name.id

    # need to treat when the Name expr is a boolean and when it's a variable.
    if id == 'True' or id == 'False':
        # if the name is actually representing a boolean, then determine if
        # we're actually typechecking it as a boolean.
        return is_bool(t)
    else:
        # if not checking for a boolean, then we must be looking for a variable,
        # so we need to see if it matches the type in the environment.
        return is_subt(env_get(env, name), t)

def check_BinOp_expr(binop, t, env):
    """Checks whether the AST expression node given by C{expr} typechecks as a
    binary operation expression. This will only typecheck if C{t} is an int
    or a float."""

    if not isinstance(binop, ast.BinOp):
        return False

    l = binop.left
    r = binop.right

    # the type needs to be an int or a float, and both expresions need to
    # typecheck as that type.
    return (is_int(t) or is_float(t)) and \
        check_expr(l, t, env) and check_expr(r, t, env)

def check_Compare_expr(compare, t, env):
    """Checks whethre the AST expression node given by C{compare} typechecks
    as a compare expression. The specified C{t} must be a boolean for this to
    typecheck correctly.
    NOTE: Right now, this only handles binary comparisons. That is, it only
    handles expressions of the form x>y or x==y, not x==y==z or x>y>z."""

    if not isinstance(compare, ast.Compare):
        return False

    # the Compare AST node anticipates expressions of the form x > y > z, in
    # which case x would be left, y would be comparators[0], and z would be
    # comparators[1]
    l = compare.left
    r = compare.comparators[0]

    # will typecheck if t is a boolean and both sides typecheck as floats.
    return is_bool(t) and \
           check_expr(l, float_type, env) and check_expr(r, float_type, env)

