import ast
import logging

from util import cname, slice_range, node_is_int, valid_int_slice
from errors import TypeUnspecifiedError
from ptype import PType, int_t, float_t, bool_t, str_t, unit_t, unicode_t
from settings import DEBUG_INFER

# Need to use this form to resolve circular import.
import check

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

    return call_function(n, e, env)

def get_infer_expr_func_name(expr_type):
    return "infer_%s_expr" % expr_type

def infer_Num_expr(num, env):
    """
    Determine the type of AST `Num` expression under type environment `env`.

    `ast.Num`
      - `n`: the numeric literal (as a Python object)
    """

    assert num.__class__ is ast.Num

    n = num.n

    if type(n) is int:

        # (int) assignment rule.
        return int_t

    elif type(n) is float:

        # (flt) assignment rule.
        return float_t

    else:

        # No type assignment rule found.
        return None

def infer_Str_expr(s, env):
    """
    Determine the type of AST `Str` expression under type environment `env`.

    `ast.Str`
      - `s`: the string literal (as a Python object)
    """

    assert s.__class__ is ast.Str

    the_string = s.s

    if type(the_string) is str:

        # (str) assignment rule.
        return str_t

    elif type(the_string) is unicode:

        # (ustr) assignment rule.
        return unicode_t

    else:

        # No type assignment rule found..
        return None

def infer_Name_expr(name, env):
    """
    Determine the type of AST `Name` expression under type environment `env`.

    `ast.Name`
      - `id`: the identifier (as a Python `str`)
      - `ctx`: the context (e.g., load, store) in which the expr is used

    The AST treats `True` and `False` as Name nodes with id of `"True"` or
    `"False"`, strangely enough.
    """

    assert name.__class__ is ast.Name

    id_str = name.id

    if id_str == 'True' or id_str == 'False':

        # (bool) assignment rule.
        return bool_t

    elif id_str == 'None':

        # (none) assignment rule.
        return unit_t

    else:

        # (idn) assignment rule.
        return env_get(env, id_str)

def infer_List_expr(lst, env):
    """
    Determine the type of AST `List` expression under type environment `env`.

    `ast.List`
      - `elts`: Python list of contained expr nodes
      - `ctx': context of the expr (e.g., load, store)
    """

    assert lst.__class__ is ast.List

    elts_list = lst.elts

    first_type = infer_expr(elts_list[0], env)

    if all(check.check_expr(e, first_type, env) for e in elts_list[1:]):

        # (lst) assignment rule.
        return PType.list_of(first_type)

    else:

        # No assignment rule found.
        return None

def infer_Tuple_expr(tup, env):
    """
    Determine the type of AST `Tuple` expression under type environment `env`.

    `ast.Tuple`
      - `elts`: Python list of contained expr nodes
      - `ctx`: context of the expr (e.g., load, store)
    """

    assert tup.__class__ is ast.Tuple

    elts_list = tup.elts

    # (tup) assignment rule.
    # Note that this rule applies to any tuple expression.
    return PType.tuple_of([infer_expr(e, env) for e in elts_list])

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

        # If we can't assign a type to the collection, then we can't assign a
        # type to its subscript.
        return None

    # String subscripting
    elif col_t == str_t or col_t == unicode_t:

        if is_index and infer_expr(i, env) == int_t:

            # (sidx) assignment rule.
            return col_t

        elif is_slice and valid_int_slice(l, u, s, env):

            # (sslc) assignment rule.
            return col_t

        else:

            # No assignment rule found.
            return None

    # List subscripting
    elif col_t.is_list():

        if is_index and check.check_expr(i, int_t, env):

            # (lidx) assignment rule.
            return col_t.list_t()

        elif is_slice and valid_int_slice(l, u, s, env):

            # (lslc) assignment rule.
            return col_t

        else:

            # No assignment rule found.
            return None

    # Tuple subscripting
    elif col_t.is_tuple():

        col_ts = col_t.tuple_ts()
        n = len(col_ts)

        if is_index and node_is_int(i) and -n <= i.n < n:

            # (tidx) assignment rule.
            return col_ts[i.n]

        elif is_slice:

            rng = slice_range(l, u, s, len(col_ts))

            if rng is not None:

                # (tslc) assignment rule.
                return PType.tuple_of([col_ts[i] for i in rng])

            else:

                # No assignment rule found.
                return None

        else:

            # No assignment rule found.
            return None

    else:

        # No assignment rule found.
        return None
