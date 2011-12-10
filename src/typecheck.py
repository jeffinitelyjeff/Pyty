import ast
import logging

from util import cname, slice_range, node_is_int, node_is_None, valid_int_slice
from errors import TypeUnspecifiedError, ASTTraversalError
from ptype import PType, int_t, float_t, bool_t, str_t, unit_t, unicode_t
from settings import DEBUG_TYPECHECK
from logger import Logger
from ast_extensions import TypeDec
from infer import infer_expr, env_get

log = None

def t_debug(s, cond=True):
    log.debug(s, DEBUG_TYPECHECK and cond)

def call_function(fun_name, *args, **kwargs):
    return globals()[fun_name](*args, **kwargs)

# ---------------------------------------------------------------------------
# GENERAL CHECKING FUNCTIONS ------------------------------------------------
# ---------------------------------------------------------------------------

def check_mod(mod):
    """
    Check whether the module node `mod` typechecks under its embedded
    environments.
    """

    t_debug("----- v Typechecking module v -----")

    if mod.__class__ != ast.Module:
        t_debug("Returning false because this isn't a module")
        t_debug("----- ^ Typechecking module ^ -----")
        return False

    result = check_stmt_list(mod.body, {})
    t_debug("return: " + str(result) + "\n----- ^ Typechecking module ^ -----")
    return result

def check_stmt(stmt, env):
    """
    Check whether the statement node `stmt` typechecks under type environment
    `env`.

    We defer to the specific `check_X_stmt` functions to determine which type
    assignemnt rule to try.
    """

    t_debug("--- v Typechecking " + stmt.__class__.__name__ + " stmt v ---"
            "\nStmt: " + str(stmt) + "\nEnv: " + str(env))

    n = get_stmt_func_name(stmt.__class__.__name__)

    # if we get a KeyError, then we're inspecting an AST node that is not in
    # the subset of the language we're considering (note: the subset is
    # defined as whatever there are check function definitions for).
    try:
        result = call_function(n, stmt, env)
        t_debug("return: " + str(result) + "\n--- ^ Typechecking stmt ^ ---")
        return result
    except KeyError as e:
        t_debug("Found a stmt not in the language subset. (" + str(e) + ")")
        return False

def check_stmt_list(stmt_list, env):
    """
    Check whether each stmt in `stmt_list` typechecks correctly. `env` is the
    common type environment shared by all stmts in `stmt_list`
    """

    # Make duplicate of environment to add to as we encounter type declarations.
    w_env = env.copy()

    for s in stmt_list:

        if s.__class__ is TypeDec:
            # Add each binding to the environment for future statements.
            for tar in s.targets:
                w_env[tar.id] = s.t
        elif not check_stmt(s, w_env):
            # Break out if a statement doesn't typecheck.
            return False

    # Reaching here means all statements typechecked.
    return True

def check_expr(expr, t, env):
    """Checks whether the AST expression node given by C{node} typechecks as
    an expression of type C{t}. The requirements of typechecking depend on the
    kind of expression C{node} is, and so this function calls one of several
    functions which typecheck C{code} as the specific kind of expression. The
    function to call is chosen from the class name of C{node}."""

    assert isinstance(expr, ast.expr), \
           "Should be typechecking an expr node, not a " + cname(expr)
    assert isinstance(t, PType), \
           "Should be checking against a PType, not a " + cname(t)

    n = get_check_expr_func_name(expr.__class__.__name__)

    t_debug("-- v Typechecking expr as " + str(t) + " v --\nExpr: " +
            str(expr) + "\nEnv: " + str(env))

    # if we get a KeyError, then we're inspecting an AST node that is not in
    # the subset of the language we're considering (note: the subset is
    # defined as whtaever there are check function definitions for).
    try:
        result = call_function(n, expr, t, env)
        t_debug("return: " + str(result) + "\n-- ^ Typechecking expr ^ --")
        return result
    except KeyError as e:
        t_debug("Found an expr not in the language subset. (" + str(e) + ")")
        return False


# ---------------------------------------------------------------------------
# STATEMENT CHECKING FUNCTIONS ----------------------------------------------
# ---------------------------------------------------------------------------
#   Valid statement types are:
#   = Done ------------------------------------------------------------------
#    - Assign(expr* targets, expr value)
#    - If(expr test, stmt* body, stmt* orelse)
#    - While(expr test, stmt* body, stmt* orelse)
#    - Print(expr? dest, expr* values, bool nl)
#   = To Do -----------------------------------------------------------------
#    - AugAssign(expr target, operator op, expr value)
#    - For(expr test, expr iter, stmt* body, stmt* orelse)

#    - FunctionDef(identifier name, arguments args, stmt* body, expr*
#       decorator_list)
#    - ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
#    - Return(expr? value)
#    - Delete(expr* targets)
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

def check_Expr_stmt(stmt, env):
    """
    Check whether expr statement node `stmt` typechecks under type environment
    `env`.

    `stmt` : `ast.Expr`
      - `value`: expression

    Note: In Python, any kind of expression can be used as a statement, but
    we're only going to allow typechecking of call expressions. There is no
    practical reason to use any other kind of expression as a statement.
    """

    assert stmt.__class__ == ast.Expr

    if stmt.value.__class__ == ast.Call:

        call = stmt.value

        # (exprs) assignment rule.

        # Determine the type that the call expression should typecheck as by
        # looking at the type of the function being called.
        tau = infer_expr(call.func, env).range_t()

        return check_expr(call, tau, env)

    else:

        return False


def check_FunctionDef_stmt(stmt, env):
    """
    Check whether function definition node `stmt` typechecks under type
    envirnoment `env`.

    `stmt` : `ast.FunctionDef`
      - `name`: string of function identifier.
      - `args`: `ast.arguments`
        + `args`: list of name nodes of normal arguments.
        + `vararg`: string identifier for the vararg parameter.
        + `kwarg`: string identifier for the kwarg parameter.
        + `defaults`: list of expressions to use as default parameter values.
      - `body`: list of statements to run to execute the function.
      - `decorator_list`: list of decorators associated with function.
    """

    assert stmt.__class__ == ast.FunctionDef

    name = stmt.name
    args = stmt.args.args
    body = stmt.body

    # (fndef) assignment rule.
    # The implementation here looks a lot messier than the (fndef) rule; most of
    # this is complication in determining whether args and sigma look similar
    # and args : sigma has meaning.

    # First, we ensure that all the arguments are `ast.Name` nodes, since the
    # AST specification allows arbitrary expressions).
    if any(arg.__class__ is not ast.Name for arg in args):
        return False

    # The user has to have declared the type of of the function prior to the
    # function definition, so choosing the sigma and tau reduces to environment
    # lookup.
    t = env_get(env, name)
    sigma = t.domain_t()
    tau = t.range_t()

    # Next, ensure that the input type is the correct form given the number of
    # parameters.
    if not ((len(args) == 0 and sigma == unit_t) or
            (len(args) == 1 and sigma != unit_t) or
            (sigma.is_tuple() and len(sigma.tuple_ts()) == len(args))):
        return False

    # The environment to use while typechecking the function body.
    body_env = env.copy()

    # Mandate the specified return type.
    body_env["return"] = tau

    # Add the types of the parameters.
    if len(args) == 1:
        body_env[args[0].id] = sigma
    elif len(args) > 1:
        t_debug(str(args))
        t_debug(str(sigma))
        for (arg, arg_t) in zip(args, sigma.tuple_ts()):
            body_env[arg.id] = arg_t

    return check_stmt_list(body, body_env)


def check_Assign_stmt(stmt, env):
    """
    Check whether assignment node `stmt` typechecks under type environment
    `env`.

    `ast.Assign`
      - `value`: the value being assigned.
      - `targets`: Python list of the expressions being assigned to.
    """

    assert stmt.__class__ == ast.Assign

    v = stmt.value
    tars = stmt.targets

    for tar in tars:

        assert tar.ctx.__class__ is ast.Store, \
            "Should be store ctx, not " + cname(tar.ctx)

        if tar.__class__ is ast.Subscript:

            col_t = infer_expr(tar.value, env)

            if col_t is not None and col_t.is_tuple():
                # Can't assign to a subscript of a tuple.
                return False

        t = infer_expr(tar, env)

        if t is None:
            # The target doesn't typecheck properly.
            return False

        if not check_expr(v, t, env):
            # The value doesn't typecheck as the type of the target.
            return False

    # return True if we reached here, meaning that it matched with all targets
    return True

def check_AugAssign_stmt(stmt, env):
    """
    Check whether augment assignment node `stmt` typechecks under type
    environment `env`.

    `ast.AugAssign`
      - `target`: the expression being assigned to.
      - `op`: the operation.
      - `value`: the expression `op`ed to `target`.
    """

    assert stmt.__class__ == ast.AugAssign

    v = stmt.value
    tar = stmt.target
    op = stmt.op

    binop = ast.BinOp(tar, op, v)

    t = infer_expr(tar, env)

    if t is None:
        # The target doesn't typecheck properly.
        return False
    else:
        return check_expr(binop, t, env)

def check_If_stmt(stmt, env):
    """
    Check whether if statement node `stmt` typechecks under type environment
    `env`.

    We currently assume that the test must be a boolean, which is not considered
    very Pythonic by some.

    `ast.If`
      - `test`: the expression being tested.
      - `body`: Python list of statements to run if `test` is true.
      - `orelse`: Python list of statements to run if `test` is false.
    """

    return check_If_While_stmt(stmt, env)

def check_While_stmt(stmt, env):
    """
    Check whether while node `stmt` typechecks under type environment `env`.

    `ast.While`
      - `test`: the expression being tested each iteration.
      - `body`: Python list of statements to run on each iteration.
      - `orelse`: Python list of statements to run if `test` is false.
    """

    assert stmt.__class__ == ast.While

    return check_If_While_stmt(stmt, env)

def check_If_While_stmt(stmt, env):
    """
    Check whether while or if node `stmt` typechecks under type environment
    `env`.

    'ast.If` and `ast.While` have identical structure, so this is a helper
    function to house the identical logic.
    """

    test = stmt.test
    body = stmt.body
    orelse = stmt.orelse

    return (check_expr(test, bool_t, env) and
            check_stmt_list(body, env) and
            check_stmt_list(orelse, env))

def check_For_stmt(stmt, env):
    """
    Check whether for node `stmt` typechecks under type environment `env`.

    `ast.For`
      - `target`: the loop variable
      - `iter`: the iterable beeing looped over.
      - `body`: list of statements to run on each iteration.
      - `orelse`: list of statements to run at the end of the loop.
    """

    assert stmt.__class__ == ast.For

    # Look up the type we've declared for the loop variable. We don't just do an
    # environment lookup because the target could be any left-hand side of an
    # assignment.
    t = infer_expr(stmt.target, env)

    if t is None:
        # The target expression doesn't typecheck properly.
        return False

    # (lfor) assigment rule.
    return (check_expr(stmt.iter, PType.list_of(t), env) and
            check_stmt_list(stmt.body, env) and
            check_stmt_list(stmt.orelse, env))


def check_Print_stmt(stmt, env):
    """
    Check whether print node `stmt` typechecks under type environment `env`.

    I guess a print statement always typechecks?
    """

    assert stmt.__class__ == ast.Print

    return True

def check_Pass_stmt(stmt, env):
    """
    Check whether pass node `stmt` typechecks under type environment `env`.

    A pass statement should always typecheck.
    """

    assert stmt.__class__ == ast.Pass

    return True

def check_Break_stmt(stmt, env):
    """
    Check whether break node `stmt` typechecks under type environment `env`.

    A break statement should always typecheck.
    """

    assert stmt.__class__ == ast.Break

    return True

def check_Continue_stmt(stmt, env):
    """
    Check whether continue node `stmt` typechecks under type environment `env`.

    A continue statement should always typecheck.
    """

    assert stmt.__class__ == ast.Continue

    return True

def check_Return_stmt(stmt, env):
    """
    Check whether return node `stmt` typechecks under type environment `env`.

    The type that the current function must return is stored as a special
    `return` entry in the type environment.

    `ast.Return`
      - `value`: the expression being returned.
    """

    e = stmt.value
    ret_t = env_get(env, "return")

    if e is None:

        # (urtn) assignment rule.
        return ret_t == unit_t

    else:

        # (rtn) assignment rule.
        return check_expr(e, ret_t, env)


# ---------------------------------------------------------------------------
# EXPRESSION CHECKING FUNCTIONS ---------------------------------------------
# ---------------------------------------------------------------------------
#   Valid expression types are:
#   = Done ------------------------------------------------------------------
#    - Num(object n)
#    - Name(identifier id, expr_context ctx)
#    - BinOp(expr left, operator op, expr right)
#    - Compare(expr left, cmpop* ops, expr* comparators)
#    - List(expr* elts, expr_context ctx)
#    - Tuple(expr* elts, expr_context ctx)
#    - UnaryOp(unaryop op, expr operand)
#   = To Do -----------------------------------------------------------------
#    - Subscript(expr value, slice slice, expr_context ctx)
#    - Attribute(expr value, identifier attr, expr_context ctx)
#    - BoolOp(boolop op, expr* values)
#    - Lambda(arguments args, expr body)
#    - IfExp(expr test, expr body, expr orelse)
#    - Dict(expr* keys, expr* values)
#    - Set(expr* elts)
#    - Call(expr func, expr* args, keyword* keywords, expr? starargs,
#       expr? kwargs)
#    - Str(string s)

def get_check_expr_func_name(expr_type):
    return "check_%s_expr" % expr_type

def check_Num_expr(num, t, env):
    """
    Check if AST Num expr node `num` typechecks as type `t` under type
    environment `env`.

    `ast.Num`
      - `n`: the numeric literal (as a Python object)
    """

    assert num.__class__ == ast.Num

    n = num.n

    if t == int_t:

        # (int) assignment rule.
        return type(n) is int

    elif t == float_t:

        # (flt) assignment rule.
        return type(n) is float

    else:

        # No type assignment rule found.
        return False

def check_Str_expr(s, t, env):
    """
    Check if AST Str expr node `s` typechecks as type `t` under type environment
    `env`.

    `ast.Str`
      - `s`: the string literal (as a Python object)
    """

    assert s.__class__ == ast.Str

    if t == str_t:

        # (str) assignment rule.
        return type(s.s) is str

    elif t == unicode_t:

        # (ustr) assignment rule.
        return type(s.s) is unicode

    else:

        # No type assignment rule found.
        return False

def check_Name_expr(name, t, env):
    """
    Check if AST Name expr node `name` typechecks as type `t` under type
    environment `env`.

    `ast.Name`
      - `id`: the identifier (as a Python `str`)
      - `ctx`: the context (e.g., load, store) in which the expr is used

    The AST treats `True` and `False` as Name nodes with id of `"True"` or
    `"False"`, strangely enough.

    Ideally, we should only be accessing name nodes in the load context, since
    the type checking rule for an assignment statement should handle all the
    cases where they are in load contexts. We currently have to typecheck load
    variables because the limited type inference assumes everything it infers
    typechecks correctly, which isn't always the case; to fix this, we also
    verify that something checks as the type we infer, which means we'll end up
    checking name loads.
    """

    assert name.__class__ == ast.Name

    id = name.id

    if id == 'True' or id == 'False':

        # (bool) assignment rule
        return t == bool_t

    elif id == 'None':

        # (none) assignment rule.
        return t == unit_t

    else:

        # (idn) assignment rule
        return env_get(env, id) == t

def check_BinOp_expr(binop, t, env):
    """
    Check if AST BinOp expr node `binop` typechecks as type `t` under type
    environment `env`:

    `ast.BinOp`
      - `left`: left expr
      - `op`: the operator (an `ast.operator`)
      - `right`: right expr
    """

    assert binop.__class__ == ast.BinOp

    l = binop.left
    r = binop.right
    op = binop.op

    arith_ops = [ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow]
    bit_ops = [ast.LShift, ast.RShift, ast.BitOr, ast.BitAnd, ast.BitXor]

    assert op.__class__ in arith_ops + bit_ops, \
        "Invalid binary operator, %s" % cname(op)


    # Numeric operations.
    if t == int_t or t == float_t:

        if op.__class__ in arith_ops:

            # (arith) assignment rule.
            return check_expr(l, t, env) and check_expr(r, t, env)

        else: # op.__class__ in bit_ops

            # (bitop) assignment rule.
            return (t == int_t and
                    check_expr(l, int_t, env) and
                    check_expr(r, int_t, env))

    # String operations.
    elif t == str_t or t == unicode_t:

        if op.__class__ is ast.Add:

            # (scat) assignment rule.
            # t is str_t or unicode_t.
            return check_expr(l, t, env) and check_expr(r, t, env)

        elif op.__class__ is ast.Mult:

            # (srep) or (surep) assignment rule.
            # t is str_t or unicode_t.
            return ((check_expr(l, t, env) and check_expr(r, int_t, env)) or
                    (check_expr(l, int_t, env) and check_expr(r, t, env)))

        elif op.__class__ is ast.Mod:

            # (sform) assignment rule.
            # t is str_t or unicode_t.
            return check_expr(l, t, env)

        else:

            # No assignment rule found.
            return False

    # List operations.
    elif t.is_list():

        if op.__class__ is ast.Add:

            # (lcat) assignment rule.
            return check_expr(l, t, env) and check_expr(r, t, env)

        elif op.__class__ is ast.Mult:

            # (lrep) assignment rule.
            return ((check_expr(l, t, env) and check_expr(r, int_t, env))
                    or (check_expr(l, int_t, env) and check_expr(r, t, env)))

        else:

            # No assignment rule found.
            return False

    # Tuple operations.
    elif t.is_tuple():

        if op.__class__ is ast.Add:

            # (tcat) assignment rule.
            # This is pretty inefficient; we check every way which `t` can
            # be split up into two tuples, but this seems to be the only way
            # around type inference.
            return any(check_expr(l, t.tuple_ts_slice(0, i), env)
                       and check_expr(r, t.tuple_ts_slice(i), env)
                       for i in range(1, len(t.tuple_ts())))

        elif op.__class__ is ast.Mult:

            # (trep) assignment rule.
            # We have to restrict ourselves to repeating tuples by integer
            # values because we need to know the value while type checking
            # to figure out the expected shape of the type.

            # Figure out if we're looking at e * m or m * e.
            if l.__class__ is ast.Num and type(l.n) is int:
                e = r
                m = l.n
            elif r.__class__ is ast.Num and type(r.n) is int:
                e = l
                m = r.n
            else:
                # These are the only two froms of expressions which can be
                # assigned in (trep).
                return False

            # the length of the tuple we expect e to typecheck as.
            e_len = len(t.tuple_ts()) / m
            # the tuple we expect e to typecheck as.
            e_typ = t.tuple_ts_slice(0, e_len)

            return (len(t.tuple_ts()) % m == 0 and
                    check_expr(e, e_typ, env) and
                    all(e_typ == t.tuple_ts_slice(e_len*i, e_len*(i+1))
                        for i in range(1, m)))

        else:

            # No assignment rule found.
            return False

    else:

        # No assignmment rules found.
        return False


def check_UnaryOp_expr(unop, t, env):
    """
    Check if AST UnaryOp expr node `unop` typechecks as type `t` under type
    environment `env`.

    - Invert is the bitwise inverse and can only be applied to ints
    - Not can be applied to bools
    - UAdd and USub can be applied to any numbers

    `ast.UnaryOp`:
      - `op`: the operator (an `ast.unaryop`)
      - `operand`: operand expr

    """

    assert unop.__class__ == ast.UnaryOp

    rator = unop.op
    rand = unop.operand

    assert rator.__class__ in [ast.Invert, ast.Not, ast.UAdd, ast.USub]

    if rator.__class__ is ast.Invert and t == int_t:

        # (inv) assignment rule.
        return check_expr(rand, int_t, env)

    elif rator.__class__ is ast.Not and t == bool_t:

        # (not) assignment rule.
        return check_expr(rand, bool_t, env)

    elif rator.__class__ in [ast.UAdd, ast.USub] and t == int_t:

        # (uadd) assignment rule v1.
        return check_expr(rand, int_t, env)

    elif rator.__class__ in [ast.UAdd, ast.USub] and t == float_t:

        # (uadd) assignment rule v2.
        return check_expr(rand, float_t, env)

    else:

        # No type assignment rules found.
        return False

def check_Compare_expr(compare, t, env):
    """
    Check if AST Compare expr node `compare` typechecks as type `t` under type
    environment `env`.

    `ast.Compare`
      - `left`: the left-most expression
      - `ops`: list of comparison operators (all `ast.cmpop`)
      - `comparators`: list of subsequent expressions

    A chained comparison expression is structured like so:
    `left` `ops[0]` `comparators[0]` `ops[1]` `comparators[1]` ...
    """

    assert compare.__class__ == ast.Compare

    # Operators that need to take numbers.
    num_ops = [ast.Lt, ast.LtE, ast.Gt, ast.GtE]
    # Operators that can take arbitrary expressions.
    eq_ops = [ast.Eq, ast.NotEq, ast.Is, ast.IsNot]

    e0 = compare.left
    ops = compare.ops
    es = compare.comparators

    if len(ops) == 1 and t == bool_t:
        # We're in a base case.

        e1 = es[0]

        if ops[0].__class__ in eq_ops:
            # (eqcmp) assignment rule.
            return True
        elif ops[0].__class__ in num_ops:
            # (numcmp) assignment rule.
            ts = (int_t, float_t, str_t, unicode_t)
            return any(all(check_expr(e, t, env) for e in (e0, e1)) for t in ts)

        else:
            # no assignment rule found.
            return False

    elif t == bool_t:

        # (cmp) assignment rule.

        head = ast.Compare(e0, [ops[0]], [es[0]])
        tail = ast.Compare(es[0], ops[1:], es[1:])

        return check_expr(head, bool_t, env) and check_expr(tail, bool_t, env)

    else:

        # no assignment rule fonud.
        return False


def check_List_expr(list, t, env):
    """
    Check if AST List expr node `list` typechecks as type `t` under type
    environment `env`.

    `ast.List`
      - `elts`: Python list of contained expr nodes
      - `ctx': context of the expr (e.g., load, store)
    """

    assert list.__class__ == ast.List

    es = list.elts

    if t.is_list():
        # Check whether each expression typechecks as the type which t is a list
        # of.
        e_t = t.list_t()
        return all(check_expr(e, e_t, env) for e in es)
    else:
        return False # desired type not a list

def check_Tuple_expr(tup, t, env):
    """
    Check if AST Tuple expr node `tup` typechecks as type `t` under type
    environment `env`.

    `ast.Tuple`
      - `elts`: Python list of contained expr nodes
      - `ctx`: context of the expr (e.g., load, store)
    """

    assert tup.__class__ == ast.Tuple

    es = tup.elts

    if t.is_tuple():
        e_ts = t.tuple_ts()
        return (len(es) == len(e_ts) and
                all(check_expr(es[i], e_ts[i], env) for i in range(len(e_ts))))
    else:
        return False # desired type is not a tuple

def check_Subscript_expr(subs, t, env):
    """
    Check if AST Subscript expr node `subs` typechecks as type `t` under type
    environment `env`.

    `ast.Subscript`
      - `value`: the collection being subscripted
      - `slice`: `ast.Index` or `ast.Slice`
        + `value`: expr used as index (if `ast.Index`)
        + `lower`: expr used as lower bound (if `ast.Slice`)
        + `upper`: expr used as upper bound (if `ast.Slice`)
        + `step`: expr used as step (if `ast.Slice`)

    We can only subscript tuples with numeric literals because the type checker
    needs to actually know the values of the subscript parameters.
    """

    assert subs.__class__ == ast.Subscript

    # Type inference is necessary becuase subscripting is very overloaded.
    col = subs.value
    col_t = infer_expr(col, env)

    is_index = subs.slice.__class__ is ast.Index
    is_slice = subs.slice.__class__ is ast.Slice
    assert is_index or is_slice

    # Store the attributes of the slice.
    if is_index:
        i = subs.slice.value
    else: # is_slice
        l = subs.slice.lower
        u = subs.slice.upper
        s = subs.slice.step

    if col_t is None:
        # The collection doesn't typecheck properly.
        return False

    # String subscripting.
    elif col_t == t == str_t or col_t == t == unicode_t:

        if is_index:

            # (sidx) assignment rule.
            return check_expr(i, int_t, env)

        else: # is_slice

            # (sslc) assignment rule.
            return valid_int_slice(l, u, s, env) and check_expr(col, t, env)

    # List subscripting.
    elif col_t.is_list():

        if is_index:

            # (lidx) assignment rule.
            return (check_expr(i, int_t, env) and
                    check_expr(col, PType.list_of(t), env))

        else: # is_slice

            # (lslc) assignment rule.
            return valid_int_slice(l, u, s, env) and check_expr(col, t, env)

    # Tuple subscripting.
    elif col_t.is_tuple():

        if is_index:

            col_ts = col_t.tuple_ts()
            n = len(col_ts)

            # (tidx) assignment rule.
            # Note: we don't need to normalize i.n by len(col_ts) if i.n < 0
            # because col_ts[i.n] handles this automatically.
            return node_is_int(i) and -n <= i.n < n and col_ts[i.n] == t

        else: # is_slice

            # (tslc) assignment rule.

            # Rule out easy failure case.
            if not t.is_tuple():
                return False # not expceting a tuple type.

            col_ts = col_t.tuple_ts()
            ts = t.tuple_ts()

            rng = slice_range(l, u, s, len(col_ts))

            if rng is None:
                # The range wasn't valid.
                return False

            z = zip(range(0, len(rng)), rng)
            return all(col_ts[j] == ts[i] for (i,j) in z)

    else:

        return False # Only subscripts of str, list, and tuple work.

def check_IfExp_expr(ifx, t, env):
    """
    Check if AST IfExp expr node `ifx` typechecks as type `t` under type
    environment `env`.

    `ast.IfExp`
      - `test`: the conditional to branch on.
      - `body`: the value of the expression if `test` is true.
      - `orelse`: the value of the expression if `test` is false.
    """

    assert ifx.__class__ == ast.IfExp

    test = ifx.test
    e1 = ifx.body
    e2 = ifx.orelse

    # (ifx) assignment rule.
    return (check_expr(test, bool_t, env) and
            check_expr(e1, t, env) and
            check_expr(e2, t, env))

def check_Call_expr(call, t, env):
    """
    Check if AST Call expr node `call` typechecks as type `t` under type
    environment `env`.

    We're currently only handling user-defined function calls (not built-in
    functions, methods of built-in objects, class objects, methods of class
    instances, or class instances).

    `ast.Call`
      - `func`: the function being called.
      - `args`: list of normal arguments provided.
      - `keywords`: list of keyboard arguments provided.
      - `starargs`: star argument (an iterable treated as additional positional
        arguments).
      - `kwargs`: double star argument (a mapping treated as additional keyword
        arguments).
    """

    assert call.__class__ == ast.Call

    f = call.func
    args = call.args

    # (call) assignment rule.

    # FIXME: We're using infer_expr here, but it's not clear whether this is
    # legitimate -- will the inferable subset of the language allow calling
    # functions returned by other functions? (this is fine if we're just calling
    # functions by identifiers.)
    f_t = infer_expr(f, env)

    # If f doesn't typecheck.
    if f_t is None:
        return False

    sigma = f_t.domain_t()
    tau = f_t.range_t()

    # In the type system, we treat no arguments as unit type, and multiple
    # arguments as a tuple.
    if len(args) == 0:

        return tau == t and sigma == unit_t

    else:

        if len(args) == 1:
            wrap_args = args[0]
        else:
            wrap_args = ast.Tuple(elts=[arg for arg in args], load=ast.Load())

        return tau == t and check_expr(wrap_args, sigma, env)

