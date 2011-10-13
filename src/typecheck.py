import ast
import logging

from util import cname
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

def env_get(env, var_id):
    """Look up variable id C{var_id} in type environment C{env}.

    @type env: {str: PType}
    @type var_id: C{str}
    @rtype: C{PType}
    @raise L{TypeUnspecifiedError}: If C{env} does not have information about
    C{var_id}
    """

    # make sure the variable is in the environment
    if var_id not in env:
        t_debug("Type of %s not found in %s" % (var_id, env))
        raise TypeUnspecifiedError(var=var_id,env=env)

    # return the type stored in the environment
    return env[var_id]

def call_function(fun_name, *args, **kwargs):
    return globals()[fun_name](*args, **kwargs)

# ------------------------------------------------------------------------------
# BASIC TYPE INFERENCE HELPERS -------------------------------------------------
# ------------------------------------------------------------------------------

# In most cases, these functions are just wrappers for accessing the
# environment, but there are more complicated cases like assigning to
# subscription expressions and assigning to lists/tuples.

def infer_expr(e, env):
    """
    Use limited type inference to determine the type of AST expression `e` under
    type environment `env`.
    """

    assert isinstance(e, ast.expr), \
           "Should be inferring type of an expr node, not a " + cname(e)

    n = get_infer_expr_func_name(e.__class__.__name__)

    # If we get a KeyError, then we're trying to infer the type of an AST node
    # that is not in the very limited subset of the language that we're trying
    # to perform type inference on.
    return call_function(n, e, env)

    # FIXME clean this up and write up inference algorithm
    # FIXME might want to break this up into separate functions

    # if e.__class__ == ast.Name:

    #     # The Python AST treats boolean literals like any other identifier.
    #     if e.id == 'True' or e.id == 'False':
    #         return bool_t
    #     else:
    #         return env_get(env, e.id)

    # elif e.__class__ == ast.Subscript:

    #     if

    #     col = e.value
    #     col_t = infer_expr(col, env)

    #     if t.is_list():

    #         # t
    #         return t.list_t()


    #     collection = e.value
    #     # Get the type of the collection.
    #     t = infer_expr(collection, env)

    #     if t.is_list():
    #         return t.list_t()
    #     elif t.is_tuple():
    #         slc = collection.slice
    #         if slc.__class__ == ast.Index:
    #             return t.tuple_ts()[slc.value.n]
    #         elif slc.__class__ == ast.Slice:
    #             # FIXME: gracefully fail instead of assertion error
    #             assert (slc.upper.__class__ == ast.Num and
    #                     slc.lower.__class__ == ast.Num and
    #                     slc.step.__class__ == ast.Num), \
    #                    ("Pyty requires tuples to be sliced by numeric "
    #                     "literals, not by (%s, %s, %s)" %
    #                     (cname(slc.upper), cname(slc.lower), cname(slc.step)))

    #             ts = t.tuple_ts()
    #             lower = slc.lower if slc.lower is not None else 0
    #             upper = slc.upper if slc.upper is not None else len(collection)
    #             step  = slc.step  if slc.step  is not None else 1
    #             idxs = range(lower, upper, step)
    #             return tuple(ts[idxs[i]] for i in range(idxs))
    #         else:
    #             assert False, ("Slices should only be ast.Index or ast.Slice, "
    #                            "not " + cname(slc))
    #     elif t.is_dict():
    #         # FIXME: implement when there are dictionaries and I have time
    #         pass
    #     else:
    #         assert False, ("Subscripted collections should only be lists, "
    #                        "tuples, and dictionaries, not " + cname(collection))
    # elif e.__class__ == ast.List:
    #     return PytyType.list_of(infer_expr(e.elts[0], env))
    # elif e.__class__ == ast.Tuple:
    #     return PytyType.tuple_of([infer_expr(elt, env) for elt in e.elts])
    # elif e.__class__ == ast.Dict:
    #     # FIXME: implement when there are dictionaries and I have time.
    #     pass
    # elif e.__class__ == ast.Num:
    #     if type(e.n) == int:
    #         return int_t
    #     elif type(e.n) == float:
    #         return float_t
    #     else:
    #         assert False, ("Only handling int and float numbers for now, "
    #                        "not " + cname(e.n))
    # else:
    #     assert False, "Pyty doesn't handle inferring " + cname(e)

def get_infer_expr_func_name(expr_type):
    return "infer_%s_expr" % expr_type

def infer_Num_expr(num, env):
    """
    Determine the type of AST `Num` expression under type environment `env`.
    """

    assert num.__class__ == ast.Num

    n = num.n

    if type(n) == int:
        return int_t
    elif type(n) == float:
        return float_t
    else:
        assert False, "Only handling int and float numbers, not " + cname(n)

def infer_Name_expr(name, env):
    """
    Determine the type of AST `Name` expression under type environment `env`.
    """

    assert name.__class__ == ast.Name

    # The Python AST treats boolean literals like any other identifier.
    if name.id == 'True' or name.id == 'False':
        return bool_t
    else:
        return env_get(env, name.id)

def infer_List_expr(lst, env):
    """
    Determine the type of AST `List` expression under type environment `env`.

    This assumes that the list properly typechecks (ie, that each of its
    elements is the same type).
    """

    assert lst.__class__ == ast.List

    els = lst.elts

    return PytyType.list_of(infer_expr(els[0], env))

def infer_Tuple_expr(tup, env):
    """
    Determine the type of AST `Tuple` expression under type environment `env`.
    """

    assert tup.__class__ == ast.Tuple

    els = tup.elts

    return PytyType.tuple_of([infer_expr(el, env) for el in els])

def infer_Subscript_expr(subs, env):
    """
    Determine the type of AST `Subscript` expression under type environment
    `env`.
    """

    assert subs.__class__ == ast.Subscript
    assert subs.slice.__class__ in [ast.Index, ast.Slice], \
        ("Subscript slice should only be ast.Index or ast.Slice, not " +
         cname(subs.slice))

    col = subs.value
    col_t = infer_expr(col, env)

    assert col_t.is_list() or col_t.is_tuple(), \
        ("The collection being subscripted should be a list or tuple type, "
         "not " + col_t)

    if subs.slice.__class__ == ast.Index:

        if col_t.is_list():

            # If we access an individual element of a list of type [a], then the
            # individual element has type a.
            return col_t.list_t()

        else: # this means col_t.is_tuple()

            # We're assuming that the expression properly typechecks, so we know
            # that the slice index is a nonnegative int literal.
            idx = col.slice.value.n

            # Best way to explain this is to look at the inference rule for
            # tuple indexing.
            return col_t.tuple_ts()[idx]

            # FIXME: Need to better handle uniform tuples.

    else: # this means subs.slice.__class__ == ast.Slice

        if col_t.is_list():

            # If we access a slice of a list of type [a], then the slice has
            # type [a].
            return t

        else: # this means col_t.is_tuple()

            # FIXME: Need to better handle uniform tuples.

            slc = subs.slice

            # We're assuming that the expression properly typechecks, so we know
            # that the slice parameters are nonnegative int literals.
            l = slc.lower.n if slc.lower is not None else 0
            u = slc.upper.n if slc.upper is not None else len(col_t)
            s = slc.step.n  if slc.step  is not None else 1
            idxs = range(l, u, s)

            # Best way to explain this is to look at the inference rule for
            # tuple slicing.
            return PytyType.tuple_of(
                [t.tuple_ts()[idxs[i]] for i in range(idxs)])



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

def check_FunctionDef_stmt(stmt):

    assert stmt.__class__ == ast.FunctionDef

    # how should this typecheck?

def check_TypeDec_stmt(stmt):
    """Any TypeDec should typecheck correctly as long as it doesn't try to
    reassign a type."""

    assert stmt.__class__ == TypeDec

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

    assert stmt.__class__ == ast.Assign

    e = stmt.value

    # return False if the expression doesn't match with one of the targets
    for v in stmt.targets:

        assert v.ctx.__class__ == ast.Store, \
               ("Assignment target variables should only appear in the Store "
                "context, not " + cname(v.ctx))

        t = infer_expr(v, stmt.env)

        # Tuples and tuple subscription aren't allowed in assignment.
        if t.is_tuple() or not check_expr(e, t, stmt.env):
            return False

    # return True if we reached here, meaning that it matched with all targets
    return True

def check_If_stmt(stmt):
    """Checks whether the AST node given by C{stmt} typechecks as an if
    statement. This requires that the test typecheck as a bolean and that the
    body and orelse branches both typecheck as lists of statements."""

    assert stmt.__class__ == ast.If

    test = stmt.test
    body = stmt.body
    orelse = stmt.orelse

    return check_expr(test, bool_t, stmt.env) and \
           check_stmt_list(body) and check_stmt_list(orelse)

def check_While_stmt(stmt):
    """Checks whether the AST node given by C{stmt} typechecks as a while
    statement. This requires that the test typecheck as a boolean and that the
    body and orelse branches both typecheck as lists of statements."""

    assert stmt.__class__ == ast.While

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
#    - List(expr* elts, expr_context ctx)
#    - Tuple(expr* elts, expr_context ctx)
#   = To Do -----------------------------------------------------------------
#    - Subscript(expr value, slice slice, expr_context ctx)
#    - Attribute(expr value, identifier attr, expr_context ctx)
#    - BoolOp(boolop op, expr* values)
#    - UnaryOp(unaryop op, expr operand)
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
    """Checks whether the AST expression node given by C{num} typechecks as a
    num expression (ie, a numeric literal) of type C{t}."""

    assert num.__class__ == ast.Num

    n = num.n

    if t.is_int():
        return type(n) == int
    if t.is_float():
        return type(n) in [int, float]
    else:
        return False

def check_Name_expr(name, t, env):
    """Checks whether the AST expression node given by C{name} typechecks as a
    name expression. Name expressions are used for variables and for boolean
    literals."""

    assert name.__class__ == ast.Name
    assert name.ctx.__class__ == ast.Load, \
           ("We should only be typechecking a Name node when it is being "
            "loaded, not when its context is " + cname(name.ctx))

    id = name.id

    # need to treat when the Name expr is a boolean and when it's a variable.
    if id == 'True' or id == 'False':
        # if the name is actually representing a boolean, then determine if
        # we're actually typechecking it as a boolean.
        return t.is_bool()
    else:
        # if not checking for a boolean, then we must be looking for a variable,
        # so we need to see if it matches the type in the environment.
        spec_type = infer_expr(name, env)

        if not spec_type.is_subtype(t):
            t_debug(("Variable %s has been declared of type %s, so it does not "+
                    "typecheck as type %s") % (name.id, str(spec_type), str(t)))

        return infer_expr(name, env).is_subtype(t)

def check_BinOp_expr(binop, t, env):
    """Checks whether the AST expression node given by C{expr} typechecks as a
    binary operation expression. This will only typecheck if C{t} is an int
    or a float."""

    assert binop.__class__ == ast.BinOp

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

    assert compare.__class__ == ast.Compare

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

    assert list.__class__ == ast.List

    if t.is_list():
        element_t = t.list_t()
        for x in list.elts:
            if not check_expr(x, element_t, env):
                # FIXME: specify that at least one element in the list did not
                # conform to the type of the list.
                return False
        return True

    else:
        # FIXME: specify that a list was typechecked as something other than a
        # list
        return False

def check_Tuple_expr(tup, t, env):
    """Checks whether the AST expression node given by C{tup} typechecks as a
    tuple expression as specified by L{parse_type.PytyType} C{t}.
    """

    assert tup.__class__ == ast.Tuple

    if t.is_tuple():
        element_ts = t.tuple_ts()
        for i in range(len(element_ts)):
            if not check_expr(tup.elts[i], element_ts[i], env):
                # FIXME specify that at least one element in the tuple did not
                # conform to the corresponding type in that position.
                return False
        return True

    else:
        # FIXME specify that a tuple was typechecked as something other than a
        # tuple.
        return False

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

#     # To typecheck a subscript expression, we actually need to know the type of
#     # the item we're subscripting. It's not enough to know the type of the AST
#     # node; we have to do a limited form of type inference to determine the
#     # actula type.
#     collection = subs.value
#     collection_t = infer_expr(collection, env)

#     if collection_t.is_list():
#         return check_expr(collection, PytyType.list_of(t), env)
#     elif collection_t.is_tuple():
#         slc = subs.slice
#         if slc.__class__ == ast.Index:
#             new_t = PytyType.gen_tuple_of([(t, slc.value.n)])
#         elif slc.__class__ == ast.Slice:
#             if (slc.upper.__class__ != ast.Num or
#                     slc.lower.__class__ != ast.Num or
#                     slc.step.__class__ != ast.Num):
#                 return False # Pyty restricts tuple slices to numeric literals,
#                              # should gracefully fail here and let the user know
#                              # that we just can't help them FIXME.
#             elif (type(slc.upper) != int or
#                     type(slc.lower) != int or
#                     type(slc.step) != int):
#                 return False # If we have numeric literals, they better be
#                              # ints. Should actually fail here.
#             else:
#                 # We're getting a slice of a tuple, so the expected type better
#                 # be a tuple.
#                 if not t.is_tuple(): return False # a tuple type wasn't specified

#                 lower = slc.lower if slc.lower is not None else 0
#                 upper = slc.upper if slc.upper is not None else len(collection)
#                 step  = slc.step  if slc.step  is not None else 1
#                 # t is going to be a tuple of expected types; idxs[i] is going
#                 # to be the index of the array that the expected type t[i] is
#                 # expected to match with.
#                 idxs = range(lower, upper, step)
#                 # FIXME: indicate failure - say that one of the expressions in the
#                 # tuple didn't typecheck as one of the expected types.
#                 return all([check_expr(collection.elts[idxs[i]], t[i], env)
#                             for i in idxs])
#         else:
#             assert False, ("Slices should only be ast.Index or ast.Slice, "
#                            "not " + cname(slc))
#     elif collection_t.is_dict():
#         # FIXME: implement
#         return False
#     else:
#         assert False, ("Subscripted collections should only be lists, tuples, "
#                        "tuples, and dictionaries, not " + collection_t)


def check_Subscript_Index_expr(subs, t, env):
    """
    Check if AST Subscript expr node `subs` typechecks as type `t` under type
    environment `env`. Assumes `subs` is a Subscript node representing an index.

    `ast.Subscript`
      - `value`: the collection being subscripted
      - `slice`: `ast.Index`
        + `value`: expr used as subscript index

    `ast.Num`
      - `n`: the number value
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

    assert col_t.is_list() or col_t.is_tuple, \
       "Subscripted collection type should be list or tuple, not " + col_t

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
        return (type(idx) == ast.Num and
                type(idx.n) == int and
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

        # We must be expecting a list, the slice parameters must typecheck as
        # ints, and the collection must be storing something that's a subtype of
        # what's being stored in the expected type.
        return ( t.is_list() and
                 (l is None or check_expr(l, int_t, env)) and
                 (u is None or check_expr(u, int_t, env)) and
                 (s is None or check_expr(s, int_t, env)) and
                 col_t.list_t().is_subtype(t.list_t()) )

    else: # col_t.is_tuple()

        # Rule out some easy failure cases.
        if not t.is_tuple():
            return False # TODO Not expecting a tuple type
        elif [x.__class__ == ast.Num for x in [l, u, s]] != [True, True, True]:
            return False # TODO Not numeric literals
        elif [type(x) == int for x in [l, u, s]] != [True, True, True]:
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




