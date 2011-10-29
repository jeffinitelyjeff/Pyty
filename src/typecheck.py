import ast
import logging

from util import cname
from errors import TypeUnspecifiedError, ASTTraversalError
from parse_type import PType, int_t, float_t, bool_t, str_t, gen_t
from settings import DEBUG_TYPECHECK
from logger import Logger
from ast_extensions import TypeDec

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

    result = check_stmt_list(mod.body)
    t_debug("return: " + str(result) + "\n----- ^ Typechecking module ^ -----")
    return result

def check_stmt(stmt):
    """
    Check whether the statement node `stmt` typechecks under its embedded
    environment.

    Each kind of statement has only one type assignment rule, so this is syntax
    directed and we just test the type assignment rule for the appropriate kind
    of statement node.
    """
    """Checks whether the AST node given by C{node} typechecks as a statement.
    The requirements for typechecking as a statement depend on what kind of
    statement C{node} is, and so this function calls one of several functions
    which typecheck C{node} as the specific kind of statement. The function to
    call is generated from the class name of C{node}."""

    t_debug("--- v Typechecking " + stmt.__class__.__name__ + " stmt v ---")

    assert hasattr(stmt, 'env') or stmt.is_compound(), \
           "Simple statements need to have environments"

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

    # This is more succinct, but the commented code is better for debugging
    return all(check_stmt(s) for s in stmt_list)

    # t_debug("---- v Typechecking stmt list v ----")

    # for s in stmt_list:
    #     if not check_stmt(s):
    #         t_debug("return: False")
    #         t_debug("---- ^ Typechecking stmt list ^ ----")
    #         return False

    # t_debug("return: True")
    # t_debug("---- ^ Typechecking stmt list ^ ----")
    # return True

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

def check_FunctionDef_stmt(stmt):

    assert stmt.__class__ == ast.FunctionDef

    # how should this typecheck?

def check_TypeDec_stmt(stmt):
    """
    Check whether type declaration node `stmt` typechecks under its embedded
    environment.

    `TypeDec`
      - `t`: the type declared for `targets`.
      - `targets`: the identifiers declared to have type `t`.
      - `old_env`: the environment prior to this type declaration.
      - `env`: the environment with this type declaration.
    """

    assert stmt.__class__ == TypeDec

    for target in stmt.targets:
        if target in stmt.old_env:
            # FIXME ultimately, this should throw some kind of ERROR
            t_debug("Found a TypeDec which tried to reassign a type.")
            return False

    return True

def check_Assign_stmt(stmt):
    """
    Check whether assignment node `stmt` typechecks under its embedded
    environment.

    NOTE: This currently only handles assignments with identifiers as the
    left-hand side, not lists, tuples, etc.

    `ast.Assign`
      - `value`: the value being assigned.
      - `targets`: Python list of the expressions being assigned to.
      - `env`: the type environment of this statement.
    """

    assert stmt.__class__ == ast.Assign

    v = stmt.value

    for tar in stmt.targets:

        assert tar.ctx.__class__ is ast.Store, \
            "Should be store ctx, not " + cname(tar.ctx)

        if tar.__class__ is ast.Subscript and infer_expr(tar.value).is_tuple():
            # Can't assign to a subscript of a tuple.
            return False

        t = infer_expr(tar, stmt.env)

        if t is None:
            # The target doesn't typecheck properly.
            return False

        if not check_expr(v, t, stmt.env):
            # The value doesn't typecheck as the type of the target.
            return False

    # return True if we reached here, meaning that it matched with all targets
    return True

def check_AugAssign_stmt(stmt):
    """
    Check whether augment assignment node `stmt` typechecks under its embedded
    environment.

    `ast.AugAssign`
      - `target`: the expression being assigned to.
      - `op`: the operation.
      - `value`: the expression `op`ed to `target`.
      - `env`: the type environment of this statement.
    """

    assert stmt.__class__ == ast.AugAssign

    tar = stmt.target
    op = stmt.op
    val = stmt.value
    env = stmt.env

    binop_node = ast.BinOp(tar, op, val)
    ts = [int_t, float_t, bool_t, str_t]

    return any(check_expr(binop_node, t, env) for t in ts)

def check_Delete_stmt(stmt):
    """
    Check whether delete node `stmt` typechecks under its embedded environment.

    NOTE: The python language reference is a bit unclear about what can actually
    be deleted. This assumes that only identifiers, lists, and subscripts can be
    deleted.

    `ast.Delete`
      - `targets` : a Python list of expressions to be deleted.
      - `env`: the type environment of this statement.
    """

    assert stmt.__class__ == ast.Delete

    tars = stmt.targets
    env = stmt.env

    assert all(tar.ctx.__class__ == ast.Del for tar in tars), \
        "Each target should have a delete context"

    return all(tar.__class__ in [ast.Name, ast.List, ast.Subscript]
               for tar in tars)

def check_If_stmt(stmt):
    """
    Check whether if statement node `stmt` typechecks under its embedded
    environment (and the environments embedded within each child statement,
    since `stmt` is a compound statement).

    We currently assume that the test must be a boolean, which is not considered
    very Pythonic by some.

    `ast.If`
      - `test`: the expression being tested.
      - `body`: Python list of statements to run if `test` is true.
      - `orelse`: Python list of statements to run if `test` is false.
      - `env`: the type environment of this statement.
    """

    return check_If_While_stmt(stmt)

def check_While_stmt(stmt):
    """
    Check whether while node `stmt` typechecks under its embedded environment
    (and the environments embedded within each child statement, since `stmt` is
    a compound statement).

    `ast.While`
      - `test`: the expression being tested each iteration.
      - `body`: Python list of statements to run on each iteration.
      - `orelse`: Python list of statements to run if `test` is false.
      - `env`: the type environment of this statement.
    """

    assert stmt.__class__ == ast.While

    return check_If_While_stmt(stmt)

def check_If_While_stmt(stmt):
    """
    Check whether while or if node `stmt` typechecks under its embedded
    environment (and the environments embedded within each child statement,
    since `stmt` is a compouund statement).

    'ast.If` and `ast.While` have identical structure, so this is a helper
    function to house the identical logic.
    """

    test = stmt.test
    body = stmt.body
    orelse = stmt.orelse

    return check_expr(test, bool_t, stmt.env) and \
           check_stmt_list(body) and check_stmt_list(orelse)

def check_Print_stmt(stmt):
    """
    Checks whether AST statement node `stmt` typechecks as a print statement under
    the environment stored within the node.

    I guess a print statement always typechecks?
    """

    assert stmt.__class__ == ast.Print

    return True

def check_Pass_stmt(stmt):
    """
    Checks whether AST statement node `stmt` typechecks as a print statement
    under the environment stored within the node.

    A pass statement should always typecheck.
    """

    assert stmt.__class__ == ast.Pass

    return True

def check_Break_stmt(stmt):
    """
    Checks whether AST statement node `stmt` typechecks as a break statement
    under the environment stored within the node.

    A break statement should always typecheck.
    """

    assert stmt.__class__ == ast.Break

    return True

def check_Continue_stmt(stmt):
    """
    Checks whether AST statement node `stmt` typechecks as a continue statement
    under the environment stored within the nod.

    A continue statement should always typecheck.
    """

    assert stmt.__class__ == ast.Continue

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

# def check_Call_expr(call, t, env):
#     """Checks whhether the AST expression node given by C{call} typechecks as a
#     function call expression of type C{t}."""

#     assert call.__class__ == ast.Call

#     # FIXME: this probably doesn't handle lambdas; do we want to handle that
#     # here?

#     fun = call.func
#     fun_t = infer_expr(fun, env)

#     # FIXME: this doesn't actually handle proper function subtyping; remeber,
#     # there's the more complicated subtyping relation for functions.
#     return fun_t.function_ts()[1].is_subtype(t)
#         # FIXME: now check each argument, but this is slightly more complicated
#         # because the PType thinks of the function as a tuple...


def check_Num_expr(num, t, env):
    """
    Check if AST Num expr node `num` typechecks as type `t` under type
    environment `env`.

    `ast.Num`
      - `n`: the numeric literal (as a Python object)
    """

    assert num.__class__ == ast.Num

    n = num.n

    if t.is_int():

        # (int) assignment rule.
        return isinstance(n, int)

    elif t.is_float():

        # (flt) assignment rule.
        return isinstance(n, float) # or isinstance(n, int)

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

        # (bool) type assignment rule
        return t.is_bool()

    else:

        # (idn) type assignment rule
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

    if op.__class__ in arith_ops:

        if t.is_int() or t.is_float():

            # (arith) rule
            return check_expr(l, t, env) and check_expr(r, t, env)

        elif t.is_list():

            if op.__class__ is ast.Add:

                # (lcat)
                return check_expr(l, t, env) and check_expr(r, t, env)

            elif op.__class__ is ast.Mult:

                # (lrep)
                return ((check_expr(l, t, env) and check_expr(r, int_t, env))
                        or (check_expr(l, int_t, env) and check_expr(r, t, env)))

            else:
                # No rule to assign a list type to a binop unless op is add or
                # mult.
                return False

        elif t.is_tuple():

            if op.__class__ is ast.Add:

                # (tcat)
                # This is pretty inefficient; we check every way which `t` can
                # be split up into two tuples, but this seems to be the only way
                # around type inference.
                ts = t.tuple_ts()
                return any(check_exp(l, PType.tuple_of(ts[0:i]), env)
                           and check_expr(r, PType.tuple_of(ts[i:]), env)
                           for i in range(1, len(ts)))

            elif op.__class__ is ast.Mult:

                # (trep)
                # Until we're sure where we can use type inference, we have to
                # restrict ourselves to only repeating tuples by integer
                # literals.
                # FIXME: this isn't really correct; we're not actually checking
                # that the types repeat within `t`, but to do that we'll need a
                # notion of equivalent PTypes.
                ts = t.tuple_ts()
                return ((l.__class__ is ast.Num and
                         isinstance(l.n, int) and
                         len(ts) % l.n == 0 and
                         check_expr(r, ts[:len(ts) / l.n], env))
                     or (r.__class__ is ast.Num and
                         isinstance(r.n, int) and
                         len(ts) % r.n == 0 and
                         check_expr(l, ts[:len(ts) / r.n], env)))

            else:
                # No rule to assign a tuple type to a binop unless op is add or
                # mult.
                return False

        else:

            # An arithmetic binary operation can only typecheck as an int,
            # float, list, or tuple.
            return False

    else: # op in bit_ops

        # (bitop) rule
        return (t.is_int() and
                check_expr(l, int_t, env) and
                check_expr(r, int_t, env))

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

    if rator.__class__ is ast.Invert and t.is_int():

        # (inv) assignment rule.
        return check_expr(rand, int_t, env)

    elif rator.__class__ is ast.Not and t.is_bool():

        # (not) assignment rule.
        return check_expr(rand, bool_t, env)

    elif rator.__class__ in [ast.UAdd, ast.USub] and t.is_int():

        # (uadd) assignment rule v1.
        return check_expr(rand, int_t, env)

    elif rator.__class__ in [ast.UAdd, ast.USub] and t.is_float():

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

    NOTE This doesn't handle chained comparison.

    FIXME see assignment_rules.pdf
    FIXME add is/isnot/in/notin
    """

    assert compare.__class__ == ast.Compare

    l = compare.left
    r = compare.comparators[0]

    # will typecheck if t is a boolean and both sides typecheck as floats.
    return t.is_bool() and check_expr(l, float_t, env) \
           and check_expr(r, float_t, env)

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
        return all(check_expr(es[i], e_ts[i], env) for i in range(len(e_ts)))
    else:
        return False # desired type is not a tuple

def check_Subscript_expr(subs, t, env):
    """
    Check if AST Subscript expr node `subs` typechecks as type `t` under type
    environment `env`.

    `ast.Subscript`
      - `value`: the collection being subscripted
      - `slice`: kind of subscript (`ast.Index` or `ast.Load`)
      - `ctx`: context (`ast.Load`, `ast.Store`, etc.)

    For the purposes of typechecking, we should be able to ignore the context
    because this should be automatically handled by the structure of the
    typechecking algorithm. `ast.Store` contexts only show up on the left-hand
    side of assignment statements, so they will be typechecked by the assignment
    statement typechecking rule, not by the generic subscript typechecking rule.

    Until we're sure where we can use type inference, we can only subscript
    tuples by numeric (integer) literals.
    """

    assert subs.__class__ == ast.Subscript

    if subs.slice.__class__ == ast.Index:
        return check_Subscript_Index_expr(subs, t, env)
    elif subs.slice.__class__ == ast.Slice:
        return check_Subscript_Slice_expr(subs, t, env)
    else:
        assert False, ("Slices should be ast.Index or ast.Slice, "
                       "not %" % cname(subs.slice))

def check_Subscript_Index_expr(subs, t, env):
    """
    Check if AST Subscript expr node `subs` typechecks as type `t` under type
    environment `env`. Assumes `subs` is a Subscript node representing an index.

    `ast.Subscript`
      - `value`: the collection being subscripted
      - `slice`: `ast.Index`
        + `value`: expr used as subscript index

    `ast.Num`
      - `n`: the numeric literal (as a Python object)
    """

    assert subs.__class__ == ast.Subscript
    assert subs.slice.__class__ == ast.Index

    col = subs.value
    idx = subs.slice.value

    # We actually need to know the type of the item we're indexing. It's not
    # enough to know the type of the AST node; we have to do a limited form of
    # type inference to determine the actual type.
    col = subs.value
    col_t = infer_expr(col, env)

    assert col_t.is_list() or col_t.is_tuple(), \
       "Subscripted collection type should be list or tuple, not %s" % col_t + \
       "\n" + ast.dump(subs) + str(infer_expr(ast.parse("(True, 4)").body[0].value, {}))

    if col_t.is_list():

        # (lidx) assignment rule.
        return (check_expr(col, PType.list_of(t), env) and
                check_expr(idx, int_t, env))

    else: # col_t.is_tuple()

        col_ts = col_t.tuple_ts()

        # (tidx) assignment rule.
        return (idx.__class__ is ast.Num and
                isinstance(idx.n, int) and
                0 <= idx.n < len(col_ts) and
                col_ts[idx.n] == t)

def check_Subscript_Slice_expr(subs, t, env):
    """
    Check if AST Subscript expr node `subs` typechecks as type `t` under type
    environment `env`. Assumes `subs` is a Subscript node representing a slice.

    `ast.Subscript`
      - `value`: the collection being subscripted
      - `slice`: `ast.Slice`
        + `lower`: expr used as first arg to slice
        + `upper`: expr used as second arg to slice
        + `step`: expr used as third arg to slice

    `ast.Num`
      - `n`: the number value
    """

    assert subs.__class__ == ast.Subscript
    assert subs.slice.__class__ == ast.Slice

    # To typecheck a slice expression, we actually need to know the type of the
    # item we're indexing. It's not enough to know the type of the AST node; we
    # have to do a limited form of type inference to determine the actual type.
    col = subs.value
    col_t = infer_expr(col, env)

    assert col_t.is_list() or col_t.is_tuple(), \
        "Subscripted collection must be list or tuple type, not " + col_t

    l = subs.slice.lower
    u = subs.slice.upper
    s = subs.slice.step

    if col_t.is_list():

        # (lslc) assignment rule.
        return ( (l is None or check_expr(l, int_t, env)) and
                 (u is None or check_expr(u, int_t, env)) and
                 (s is None or check_expr(s, int_t, env)) and
                 check_expr(col, t, env) )

    else: # col_t.is_tuple()

        # (tslc) assignment rule.

        # Rule out some easy failure cases.
        if not t.is_tuple():
            return False # TODO Not expecting a tuple type
        elif not all(x.__class__ is ast.Num for x in [l,u,s]):
            return False # TODO Not numeric literals
        elif not all(type(x) is int for x in [l,u,s]):
            return False # TODO Not int literals
        else:

            low = l if l is not None else 0
            upp = u if u is not None else len(col_t)
            stp = s if s is not None else 1

            return all(col_t.tuple_ts()[i] == t.tuple_ts()[i]
                       for i in range(low, upp, step))

from infer import infer_expr, env_get
