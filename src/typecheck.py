import ast
import logging

from errors import TypeUnspecifiedError, \
                   ASTTraversalError
from parse_type import *
from settings import *
from logger import Logger
from ast_extensions import *

log = None

def t_debug(s, cond=True):
    log.debug(s, DEBUG_TYPECHECK and cond)

# HELPER FUNCTIONS ----------------------------------------------------------
# ---------------------------------------------------------------------------

def env_get_name(env, v):
    """Returns the type of the variable given by the AST name node C{v} in
    environment C{env}. Abstracts away needing to get the variable's id in or
    der to look it up in the environment dictionary.

    @type env: dict of str and PytyType
    @type v: C{ast.Name}
    """

    return env_get(env, v.id)

def env_get(env, var_id):
    """Returns the type of the variable given by AST node C{v} in environment
    C{env}. Abstracts away needing to get the variable's name in order to look
    it up in the environment dictionary. Also throws a TypeUnspecifiedError if
    C{v} is not in C{env}.

    @type env: dict of str and PytyType
    @type v: C{ast.Name}
    """

    # make sure the variable is in the environment
    if var_id not in env:
        t_debug("Type of %s not found in %s" % (var_id, env))
        raise TypeUnspecifiedError(var=var_id,env=env)
    
    # return the type stored in the environment
    return env[var_id]

def call_function(fun_name, *args, **kwargs):
    return globals()[fun_name](*args, **kwargs)


# ---------------------------------------------------------------------------
# GENERAL CHECKING FUNCTIONS ------------------------------------------------
# ---------------------------------------------------------------------------

def check_mod(node):
    """Checks whether the L{ast_extensions.EnvASTModule} node given by C{node}
    typechecks as a module with the environments defined in the AST structure."""

    t_debug("----- v Typechecking module v -----")

    if not isinstance(node, ast.Module):
        t_debug("Returning false cuz this isn't a module")
        t_debug("----- ^ Typechecking module ^ -----")
        return False

    result = check_stmt_list(node.body)
    t_debug("return: " + str(result) + "\n----- ^ Typechecking module ^ -----")
    return result

def check_stmt(stmt):
    """Checks whether the AST node given by C{node} typechecks as a statement.
    The requirements for typechecking as a statement depend on what kind of
    statement C{node} is, and so this function calls one of several functions
    which typecheck C{node} as the specific kind of statement. The function to
    call is generated from the class name of C{node}."""

    t_debug("--- v Typechecking " + stmt.__class__.__name__ + " stmt v ---")

    t_debug("Throwing assertion error because this statement is simple but " +
            "has no environment", stmt.is_simple() and not hasattr(stmt, 'env'))
    assert(hasattr(stmt, 'env') or stmt.is_compound())

    n = get_stmt_func_name(stmt.__class__.__name__)

    # if we get a KeyError, then we're inspecting an AST node that is not in
    # the subset of the language we're considering (note: the subset is
    # defined as whatever there are check function definitions for).
    try:
        result = call_function(n, stmt)
        t_debug("return: " + str(result) + "\n--- ^ Typechecking stmt ^ ---")
        return result
    except KeyError:
        t_debug("Found an AST node that is not in the subset of the " +
                "language we're considering." +
                "\n--- ^ Typechecking stmt ^ ---")
        return False

def check_stmt_list(stmt_list):
    """For each stmt in C{stmt_list}, checks whether stmt is a valid
    statement."""

    t_debug("---- v Typechecking stmt list v ----")

    for s in stmt_list:
        if not check_stmt(s):
            t_debug("return: False")
            t_debug("---- ^ Typechecking stmt list ^ ----")
            return False

    t_debug("return: True")
    t_debug("---- ^ Typechecking stmt list ^ ----")
    return True

def check_expr(expr, t, env):
    """Checks whether the AST expression node given by C{node} typechecks as
    an expression of type C{t}. The requirements of typechecking depend on the
    kind of expression C{node} is, and so this function calls one of several
    functions which typecheck C{code} as the specific kind of expression. The
    function to call is generated from the class name of C{node}."""

    n = get_expr_func_name(expr.__class__.__name__)

    t_debug("-- v Typechecking expr as " + str(t) + " v --\nExpr: " +
            str(expr) + "\nEnv: " + str(env))
    
    # if we get a KeyError, then we're inspecting an AST node that is not in
    # the subset of the language we're considering (note: the subset is
    # defined as whtaever there are check function definitions for).
    try:
        result = call_function(n, expr, t, env)
        t_debug("return: " + str(result) + "\n-- ^ Typechecking expr ^ --")
        return result
    except KeyError:
        t_debug("Found an AST node that is not in the subset of the " +
                "language we're considering.")
        return False
    

# ---------------------------------------------------------------------------
# STATEMENT CHECKING FUNCTIONS ----------------------------------------------
# ---------------------------------------------------------------------------
#   Valid statement types are:
#   = Done ------------------------------------------------------------------
#    - Assign(expr* targets, expr value)
#    - If(expr test, stmt* body, stmt* orelse)
#    - While(expr test, stmt* body, stmt* orelse)
#   = To Do -----------------------------------------------------------------
#    - FunctionDef(identifier name, arguments args, stmt* body, expr*
#       decorator_list)
#    - ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
#    - Return(expr? value)
#    - Delete(expr* targets)
#    - AugAssign(expr target, operator op, expr value)
#    - For(expr test, expr iter, stmt* body, stmt* orelse)
#    - With(expr context_expr, expr? optional_vars, stmt* body)
#    - Raise(expr? type, expr? inst, expr? tback)
#    - TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
#    - TryFinally(stmt* body, stmt* finalbody)
#    - Assert(expr test, expr? msg)
#    - Import(alias* names)
#    - ImportFrom(identifier? module, alias* names, int? level)
#    - Print(expr? dest, expr* values, bool nl)
#    - Pass
#    - Break
#    - Continue

def get_stmt_func_name(stmt_type):
    return "check_%s_stmt" % stmt_type

def check_TypeDec_stmt(stmt):
    """Any TypeDec should typecheck correctly as long as it doesn't try to
    reassign a type."""

    assert(isinstance(stmt, TypeDec))

    for target in stmt.targets:
        if target in stmt.old_env:
            # XXX ultimately, this should throw some kind of ERROR.
            t_debug("Found a TypeDec which tried to reassign a type.")
            return False

    return True

def check_Assign_stmt(stmt):
    """Checks whether the AST node given by C{stmt} typechecks as an
    assignment statement. This requires that the expression on the (far) right
    of the equal signs must typecheck as each of the assign targets. The
    expression can typecheck as multiple different types because of
    subtyping.
    NOTE: Currently, this only checks assignments of the form:
        a = b = 5
    and does not handle assigning to lists or tuples."""

    assert(isinstance(stmt, ast.Assign))

    e = stmt.value

    # return False if the expression doesn't match with one of the targets
    for v in stmt.targets:
        # ensure that the variables are appearing with "store" contexts, ie
        # that they are being assigned to and not referenced. this really
        # shouldn't be a problem, but this is just to be safe.
        assert(v.ctx.__class__.__name__ == "Store")

        t = env_get(stmt.env, v.id)
        if not check_expr(e, t, stmt.env):
            return False

    # return True if we reached here, meaning that it matched with all targets
    return True

def check_If_stmt(stmt):
    """Checks whether the AST node given by C{stmt} typechecks as an if
    statement. This requires that the test typecheck as a bolean and that the
    body and orelse branches both typecheck as lists of statements."""

    assert(isinstance(stmt, ast.If))

    test = stmt.test
    body = stmt.body
    orelse = stmt.orelse

    return check_expr(test, bool_t, stmt.env) and \
           check_stmt_list(body) and check_stmt_list(orelse)

def check_While_stmt(stmt):
    """Checks whether the AST node given by C{stmt} typechecks as a while
    statement. This requires that the test typecheck as a boolean and that the
    body and orelse branches both typecheck as lists of statements."""

    assert(isinstance(stmt, ast.While))

    # this code is IDENTICAL to the If stuff; should consider refactoring into
    # helper function.
    test = stmt.test
    body = stmt.body
    orelse = stmt.orelse

    return check_expr(test, bool_t, stmt.env) and \
           check_stmt_list(body) and check_stmt_list(orelse)

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

    if t.is_int():
        return isinstance(n, int)
    if t.is_float():
        return isinstance(n, float) or isinstance(n, int)
    else:
        return False

def check_Name_expr(name, t, env):
    """Checks whether the AST expression node given by C{name} typechecks as a
    name expression. Name expressions are used for variables and for boolean
    literals."""

    if not isinstance(name, ast.Name):
        t_debug("Not a Name expression")
        return False

    if name.ctx.__class__.__name__ != 'Load':
        t_debug("Name node read expecting Load context when the context was "
                + name.ctx.__class__.__name__)
        raise ASTTraversalError()
    
    id = name.id

    # need to treat when the Name expr is a boolean and when it's a variable.
    if id == 'True' or id == 'False':
        # if the name is actually representing a boolean, then determine if
        # we're actually typechecking it as a boolean.
        return t.is_bool()
    else:
        # if not checking for a boolean, then we must be looking for a variable,
        # so we need to see if it matches the type in the environment.
        spec_type = env_get_name(env, name)

        if not spec_type.is_subtype(t):
            t_debug(("Variable %s has been declared of type %s, so it does not "+
                    "typecheck as type %s") % (name.id, str(spec_type), str(t)))
        
        return env_get_name(env, name).is_subtype(t)

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
    return (t.is_int() or t.is_float()) and \
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
    return t.is_bool() and check_expr(l, float_t, env) \
           and check_expr(r, float_t, env)

def check_List_expr(list, t, env):
    """Checks whether the AST expression node given by C{list} typechecks as a
    list expression as specified by L{parse_type.PytyType} C{t}.
    """

    assert(isinstance(list, ast.List))

    if t.is_list():
        element_t = t.list_t()
        for x in list.elts:
            if not check_expr(x, element_t, env):
                # FIXME: specify that at least one element in the list did not
                # conform to the type of the list.
                return False
        return True

    else:
        # FIXME: specify that a something other than a list was typechecked as
        # a list.
        return False

        
    
        
