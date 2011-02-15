import ast
from epydoc import docparser

from pyty_errors import TypeUnspecifiedError, \
                        TypeIncorrectlySpecifiedError, \
                        ASTTraversalError
from pyty_types import PytyMod, PytyStmt, PytyInt, PytyFloat, PytyBool, \
                       PytyExpr


def env_get(env, v):
    """Returns the type of the variable given by AST node C{v} in environment
    C{env}. Abstracts away needing to get the variable's name in order to look
    it up in the environment dictionary. Also throws a TypeUnspecifiedError if
    C{v} is not in C{env}."""

    # make sure the variable is in the environment
    if v.id not in env:
        raise TypeUnspecifiedError(var=v.id)
    
    # return the type stored in the environment
    return env[v.id]

def assert_node_type(node, ast_node_type):
    """Raises an ASTTraversalError if C{node} is not the right
    C{ast_node_type}; otherwise, returns C{True}."""

    found = node.__class__.__name__
    if found != ast_node_type
        raise ASTTraversalError(expected=ast_node_type, found=found)

    return True

def check_mod(node, env):
    """Checks whether the AST node given by C{node} typechecks as a module
    with environment C{env}."""

    assert_node_type(node, "Module")

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

    n = "check_" + stmt.__class__.__name__ + "_stmt"

    f = getattr(typecheck, n)

    return f(stmt, env)

def check_expr(expr, t, env):
    """Checks whether the AST expression node given by C{node} typechecks as
    an expression of type C{t}. The requirements of typechecking depend on the
    kind of expression C{node} is, and so this function calls one of several
    functions which typecheck C{code} as the specific kind of expression. The
    function to call is generated from the class name of C{node}."""

    n = "check_" + expr.__class__.__name__ + "_expr"

    f = getattr(typecheck, n)

    return f(expr, t, env)

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

# ---------------------------------------------------------------------------
# EXPRESSION CHECKING FUNCTIONS ---------------------------------------------
# ---------------------------------------------------------------------------
#   Valid expression types are:
#   = Done ------------------------------------------------------------------
#    - Num(object n)
#    - Name(identifier id, expr_context ctx)
#   = To Do -----------------------------------------------------------------
#    - BoolOp(boolop op, expr* values)
#    - BinOp(expr left, operator op, expr right)
#    - UnaryOp(unaryop op, expr operand)
#    - Lambda(arguments args, expr body)
#    - IfExp(expr test, expr body, expr orelse)
#    - Dict(expr* keys, expr* values)
#    - Set(expr* elts)
#    - List(expr* elts, expr_context ctx)
#    - Tuple(expr* elts, expr_context ctx)
#    - Compare(expr left, cmpop* ops, expr* comparators)
#    - Call(expr func, expr* args, keyword* keywords, expr? starargs,
#       expr? kwargs)
#    - Str(string s)

def check_Num_expr(expr, t, env):
    """Checks whether the AST expression node given by C{expr} typechecks as a
    num expression (ie, a numeric literal)."""

    n = expr.n

    if isinstance(t, PytyInt):
        return isinstance(n, int)
    elif isinstance(t, PytyFloat):
        return isinstance(n, float)
    else:
        return False

def check_Name_expr(expr, t, env):
    """Checks whether the AST expression node given by C{expr} typechecks as a
    name expression. Name expressions are used for variables and for boolean
    literals."""

    if not isinstance(expr.ctx, ast.Load):
        raise ASTTraversalError(msg="Referenced variables or booleans do" +
            " not have proper ctx's")
    
    id = expr.id

    # if checking for a boolean, say whether it's a bool literal 
    if isinstance(t, PytyBoolean):
        return id == 'True' or id == 'False'

    # if not checking for a boolean, then must be looking for a variable, so
    # we need to see if the type in the environment matches.
    return isinstance(env_get(env, expr), t)

def check_BinOp_expr(expr, t, env):
    """Checks whether the AST expression node given by C{expr} typechecks as a
    binary operation expression."""

    l = expr.left
    r = expr.right

    return isinstance(t, (PytyInt, PytyFloat)) and \
        check_expr(l, t, env) and check_expr(r, t, env)
