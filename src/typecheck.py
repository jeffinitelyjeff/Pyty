import ast
import logging

from util import cname
from errors import TypeUnspecifiedError, ASTTraversalError
from parse_type import PytyType, int_t, float_t, bool_t, str_t, gen_t
from settings import DEBUG_TYPECHECK
from logger import Logger
from ast_extensions import TypeDec
from infer import infer_expr

log = None

def t_debug(s, cond=True):
    log.debug(s, DEBUG_TYPECHECK and cond)

def call_function(fun_name, *args, **kwargs):
    return globals()[fun_name](*args, **kwargs)

# ---------------------------------------------------------------------------
# GENERAL CHECKING FUNCTIONS ------------------------------------------------
# ---------------------------------------------------------------------------

def check_mod(node):
    """Checks whether the L{ast_extensions.EnvASTModule} node given by C{node}
    typechecks as a module with the environments defined in the AST structure."""

    t_debug("----- v Typechecking module v -----")

    if node.__class__ != ast.Module:
        t_debug("Returning false because this isn't a module")
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
    assert isinstance(t, PytyType), \
           "Should be checking against a PytyType, not a " + cname(t)

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
    environment (and the environments embedded within each child statement).

    NOTE: This currently only handles assignments with identifiers as the
    left-hand side, not lists, tuples, etc.

    `ast.Assign`
      - `value`: the value being assigned.
      - `targets`: Python list of the expressions being assigned to.
    """

    assert stmt.__class__ == ast.Assign

    e = stmt.value

    # return False if the expression doesn't match with one of the targets
    for v in stmt.targets:

        assert v.ctx.__class__ == ast.Store, \
               ("Assignment target variables should only appear in the Store "
                "context, not " + cname(v.ctx))

        # FIXME
        # `infer_expr` assumes that the expression typechecks correctly. For
        # now, we just verify that it also typechecks correctly after inferring
        # the type; there is probably a more elegant way to do this.
        t = infer_expr(v, stmt.env)
        if not check_expr(v, t, stmt.env):
            return False

        # Tuples and tuple subscription aren't allowed in assignment.
        if t.is_tuple() or not check_expr(e, t, stmt.env):
            return False

    # return True if we reached here, meaning that it matched with all targets
    return True

def check_If_stmt(stmt):
    """
    Check whether if statement node `stmt` typechecks under its embedded
    environment.

    We currently assume that the test must be a boolean, which is not considered
    very Pythonic by some.

    `ast.If`
      - `test`: the expression being tested.
      - `body`: Python list of statements to run if `test` is true.
      - `orelse`: Python list of statements to run if `test` is false.
    """

    assert stmt.__class__ == ast.If

    test = stmt.test
    body = stmt.body
    orelse = stmt.orelse

    return check_expr(test, bool_t, stmt.env) and \
           check_stmt_list(body) and check_stmt_list(orelse)

def check_While_stmt(stmt):
    """
    Check whether while node `stmt` typechecks under its embedded environment
    (and the environments embedded within each child statement).

    `ast.While`
      - `test`: the expression being tested each iteration.
      - `body`: Python list of statements to run on each iteration.
      - `orelse`: Python list of statements to run if `test` is false.
    """

    assert stmt.__class__ == ast.While

    # this code is IDENTICAL to the If stuff; should consider refactoring into
    # helper function.
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

def check_Call_expr(call, t, env):
    """Checks whhether the AST expression node given by C{call} typechecks as a
    function call expression of type C{t}."""

    assert call.__class__ == ast.Call

    # FIXME: this probably doesn't handle lambdas; do we want to handle that
    # here?

    fun = call.func
    fun_t = infer_expr(fun, env)

    # FIXME: this doesn't actually handle proper function subtyping; remeber,
    # there's the more complicated subtyping relation for functions.
    return fun_t.function_ts()[1].is_subtype(t)
        # FIXME: now check each argument, but this is slightly more complicated
        # because the PytyType thinks of the function as a tuple...


def check_Num_expr(num, t, env):
    """
    Check if AST Num expr node `num` typechecks as type `t` under type
    environment `env`.

    `ast.Num`
      - `n`: the numeric literal (as a Python object)

    FIXME see assignment_rules.pdf
    """

    assert num.__class__ == ast.Num

    n = num.n

    if t.is_int():
        return type(n) == int
    if t.is_float():
        return type(n) in [int, float]
    else:
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

    FIXME see assignment_rules.pdf
    """

    assert name.__class__ == ast.Name

    # FIXME reverted this assumption for time being
    # assert name.ctx.__class__ == ast.Load, \
    #        ("We should only be typechecking a Name node when it is being "
    #         "loaded, not when its context is " + cname(name.ctx))

    id = name.id

    # need to treat when the Name expr is a boolean and when it's a variable.
    if id == 'True' or id == 'False':
        # if the name is actually representing a boolean, then determine if
        # we're actually typechecking it as a boolean.
        return t.is_bool()
    else:
        # FIXME should litearlly look in dictionry, not use infer_expr;
        # infer_expr is too abstract/general.

        # if not checking for a boolean, then we must be looking for a variable,
        # so we need to see if it matches the type in the environment.
        spec_type = infer_expr(name, env)

        if not spec_type.is_subtype(t):
            t_debug(("Variable %s has been declared of type %s, so it does not "+
                    "typecheck as type %s") % (name.id, str(spec_type), str(t)))

        return infer_expr(name, env).is_subtype(t)

def check_BinOp_expr(binop, t, env):
    """
    Check if AST BinOp expr node `binop` typechecks as type `t` under type
    environment `env`:

    `ast.BinOp`
      - `left`: left expr
      - `op`: the operator (an `ast.operator`)
      - `right`: right expr

    FIXME see assignment_rules.pdf
    """

    assert binop.__class__ == ast.BinOp

    l = binop.left
    r = binop.right

    # the type needs to be an int or a float, and both expresions need to
    # typecheck as that type.
    return (t.is_int() or t.is_float()) and \
        check_expr(l, t, env) and check_expr(r, t, env)

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

    FIXME see assignment_rules.pdf
    """

    assert unop.__class__ == ast.UnaryOp

    rator = unop.op
    rand = unop.operand

    assert rator.__class__ in [ast.Invert, ast.Not, ast.UAdd, ast.USub]

    if rator.__class__ == ast.Invert:

        # FIXME need to write out inf rule to make sure this is correct
        return int_t.is_subtype(t) and check_expr(rand, int_t, env)

    elif rator.__class__ == ast.Not:

        return t.is_bool() and check_expr(rand, bool_t, env)

    else: # equiv to rator.__class__ == ast.UAdd or ast.USub

        # FIXME need to write out inference rule for this to be clear it's
        # correct
        return t.is_subtype(float_t) and check_expr(rand, t, env)

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
      - `ctx`: context (`ast.Load`, `ast.Store`, etc.)
      - `slice`: kind of subscript (`ast.Index` or `ast.Load`)

    For the purposes of typechecking, we should be able to ignore the context
    because this should be automatically handled by the structure of the
    typechecking algorithm. `ast.Store` contexts only show up on the left-hand
    side of assignment statements, so they will be typechecked by the assignment
    statement typechecking rule, not by the generic subscript typechecking rule.
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

        # The index must typecheck as an int, and the collection must typecheck
        # as a list of the expected type.
        return (check_expr(idx, int_t, env) and
                check_expr(col, PytyType.list_of(t), env))

    else: # col_t.is_tuple()

        col_ts = col_t.tuple_ts()

        # FIXME: need to ensure type inference algorithm can actually get full
        # list of tuple types.

        # The index must be be a nonnegative int smaller than the length of the
        # tuple, and the type at the specified position must be a subtype of the
        # expected type.
        return (idx.__class__ is ast.Num and
                type(idx.n) is int and
                0 <= idx.n < len(col_ts) and
                col_ts[idx.n].is_subtype(t))

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

        # The slice parameters must typecheck as ints, and the original
        # collection must typecheck as the expected type (slice of a list is
        # also a list).
        return ( (l is None or check_expr(l, int_t, env)) and
                 (u is None or check_expr(u, int_t, env)) and
                 (s is None or check_expr(s, int_t, env)) and
                 check_expr(col, t, env) )

    else: # col_t.is_tuple()

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

            # Get the indices the slice will hit.
            idxs = range(low, upp, step)

            # Each hit type must be a subtype of the corresponding expected type.
            return all([
                col_t.tuple_ts()[i].is_subtype(t.tuple_ts()[i]) for i in idxs])
