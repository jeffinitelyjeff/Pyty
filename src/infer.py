import ast
import logging

from util import cname, slice_range, node_is_int
from errors import TypeUnspecifiedError
from ptype import PType, int_t, float_t, bool_t, str_t, unit_t, unicode_t
from settings import DEBUG_INFER

# Need to use this form to resolve circular import.
import typecheck

log = None

def i_debug(s, cond=True):
    log.debug(s, DEBUG_INFER and cond)

def call_function(fun_name, *args, **kwargs):
    return globals()[fun_name](*args, **kwargs)

def env_get(env, var_id):
    """
    Look up the PType stored for identifier `var_id` in type environment
    `env`. Returns a PType. Raises `TypeUnspecifiedError` if `env` does not
    contain `var_id`.

    - `env`: dictionary mapping strings to PTypes.
    - `var_id`: string representing identifier.
    """

    # make sure the variable is in the environment
    if var_id not in env:
        i_debug("Type of %s not found in %s" % (var_id, env))
        raise TypeUnspecifiedError(var=var_id,env=env)

    # return the type stored in the environment
    return env[var_id]

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

    t = call_function(n, e, env)

    if t is not None and typecheck.check_expr(e, t, env):
        return t
    else:
        return None

def get_infer_expr_func_name(expr_type):
    return "infer_%s_expr" % expr_type

def infer_Num_expr(num, env):
    """
    Determine the type of AST `Num` expression under type environment `env`.
    """

    assert num.__class__ is ast.Num

    n = num.n

    if type(n) is int:
        return int_t
    elif type(n) is float:
        return float_t
    else:
        assert False, "Only handling int and float numbers, not " + cname(n)

def infer_Name_expr(name, env):
    """
    Determine the type of AST `Name` expression under type environment `env`.
    """

    assert name.__class__ is ast.Name

    # The Python AST treats boolean literals like any other identifier.
    if name.id == 'True' or name.id == 'False':
        return bool_t
    # And the None literal.
    elif name.id == 'None':
        return unit_t
    else:
        return env_get(env, name.id)

def infer_Str_expr(s, env):
    """
    Determine the type of AST `Str` expression under type environment `env`.
    """

    assert s.__class__ is ast.Str
    assert type(s.s) in (str, unicode)

    if type(s.s) is str:
        return str_t
    else: # type(s.s) is unicode
        return unicode_t

def infer_List_expr(lst, env):
    """
    Determine the type of AST `List` expression under type environment `env`.

    This assumes that the list properly typechecks (ie, that each of its
    elements is the same type).
    """

    assert lst.__class__ is ast.List

    els = lst.elts

    return PType.list_of(infer_expr(els[0], env))

def infer_Tuple_expr(tup, env):
    """
    Determine the type of AST `Tuple` expression under type environment `env`.
    """

    assert tup.__class__ is ast.Tuple

    els = tup.elts

    return PType.tuple_of([infer_expr(el, env) for el in els])

def infer_Subscript_expr(subs, env):
    """
    Determine the type of AST `Subscript` expression under type environment
    `env`.

    `ast.Subscript`
      - `value`: the collection being subscripted
      - `slice`: `ast.Index` or `ast.Slice`
        + `value`: expr used as index (if `ast.Index`)
        + `lower`: expr used as lower bound (if `ast.Slice`)
        + `upper`: expr used as upper bound (if `ast.Slice`)
        + `step`: expr used as step (if `ast.Slice`)

    We can only subscript tuples with numeric literals because the inference
    algorithm needs to actually know the values of the subscript parameters.
    """

    assert subs.__class__ is ast.Subscript

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
        return None

    # String subscripting
    elif col_t == str_t or col_t == unicode_t:

        if is_index:

            # (sidx) assignment rule.
            if typecheck.check_expr(i, int_t, env):
                return col_t
            else:
                return None

        else: # is_slice

            # (sslc) assignment rule.
            if all(typecheck.check_expr(x, int_t, env) for x in (l, u, s)):
                return col_t
            else:
                return None

    # List subscripting
    elif col_t.is_list():

        if is_index:

            # (lidx) assignment rule.
            if typecheck.check_expr(i, int_t, env):
                return col_t.list_t()
            else:
                return None

        else: # is_slice

            # (lslc) assignment rule.
            if all(x is None or typecheck.check_expr(x, int_t, env)
                   for x in (l, u, s)):
                return col_t
            else:
                return None

    # Tuple subscripting
    elif col_t.is_tuple():

        col_ts = col_t.tuple_ts()
        n = len(col_ts)

        if is_index:

            # (tidx) assignment rule.
            if node_is_int(i) and type(i.n) is int and -n <= i.n < n:
                return col_ts[i.n]
            else:
                return None

        else: # is_slice

            # (tslc) assignment rule.

            col_ts = col_t.tuple_ts()

            rng = slice_range(l, u, s, len(col_ts))

            if rng is None:
                return None
            else:
                return PType.tuple_of([col_ts[i] for i in rng])

    else:

        # No assignment rule found.
        return None
