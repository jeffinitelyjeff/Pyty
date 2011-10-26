import ast
import logging

from util import cname
from errors import TypeUnspecifiedError
from parse_type import PType, int_t, float_t, bool_t, str_t, gen_t
from settings import DEBUG_INFER

log = None

def i_debug(s, cond=True):
    log.debug(s, DEBUG_INFER and cond)

def call_function(fun_name, *args, **kwargs):
    return globals()[fun_name](*args, **kwargs)

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

    return PType.list_of(infer_expr(els[0], env))

def infer_Tuple_expr(tup, env):
    """
    Determine the type of AST `Tuple` expression under type environment `env`.
    """

    assert tup.__class__ == ast.Tuple

    els = tup.elts

    return PType.tuple_of([infer_expr(el, env) for el in els])

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
            return PType.tuple_of(
                [t.tuple_ts()[idxs[i]] for i in range(idxs)])
