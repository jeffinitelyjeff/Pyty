import ast
import math
import logging
from datetime import datetime

"""
Contains useful helper functions that are not directly tied to the purpose of
other source code files.
"""

def log_center(s):
    """Pads string `s` with `-`s to center it in debugging."""

    t = 57 - len(s) - 2
    l = t / 2
    r = t - l

    return "\n" + l*'-' + ' ' + s + ' ' + r*'-' + "\n"

def escape(s):
    """Escapes all instances of single or double quotes. Returns the escaped
    string.

    `"` --> `\"`
    `'` --> `\'`
    """

    return s.replace(r'"', r'\"').replace(r"'", r"\'")

### Some short hand

def cname(obj):
    """Returns the name of the class of the provided object. This is helpful
    because there are many assert statements which center around checking the
    types of objects, and so it helps to include the name of classes in
    assertion errors. Will also include the module name if it exists, so we get
    things like ast.Name instead of just Name.

    @rtype: C{str}.
    """

    if hasattr(obj, "__module__"):
        return obj.__module__ + "." + obj.__class__.__name__
    else:
        return obj.__class__.__name__

### Set operations

def disjoint_sum(union, sets):
    """Determines if the sets in the list of sets C{sets} form of a disjoint sum
    of the set C{union}. That is, if C{sets[0] U sets[1] U ... = union} and all
    the sets in C{sets} are disjoint with respect to each other.

    @type sets: C{list} of C{set}
    @param sets: a list of sets.
    @type union: C{set}
    @param union: a set.
    @rtype: C{bool}
    @return: C{True} if C{union} is the disjoint sum of the sets in C{sets}.
    """

    u = set([])

    for i in range(len(sets)):
        s1 = sets[i]

        u = u.union(u, s1)

        for j in range(len(sets)):
            s2 = sets[j]

            if i != j and not s1.isdisjoint(s2):
                return False

    return u == union

### Operations used for inference and checking

def node_is_None(node):
    """Determine if a given AST node represents the `None` literal."""

    return node.__class__ is ast.Name and node.id == 'None'

def node_is_True(node):
    """Determine if a given AST node represents the `True` literal."""

    return node.__class__ is ast.Name and node.id == 'True'

def node_is_False(node):
    """Determine if a given AST node represents the `False` literal."""

    return node.__class__ is ast.Name and node.id == 'False'

def node_is_int(node):
    """Determine if a given AST node represents an integer literal."""

    return node.__class__ is ast.Num and type(node.n) is int

def slice_range(l, u, s, n):
    """
    Given three AST `Num` nodes representing the parameters to a simple slice
    and the length `n` of the collection being sliced, returns a range of the
    indices hit by the slice. Namely, this method handles empty values, negative
    values, and the odd `None` parameter when we have to.

    Returns `None` if any parameter present but not an integer literal.

    - `l`: AST node representing lower bound of slice.
    - `u`: AST node representing upper bound of slice.
    - `s`: AST node representing step of slice.
    """

    # Ensure we're dealing with integer literals.
    if not ((node_is_int(l) or l is None) and
            (node_is_int(u) or u is None) and
            (node_is_int(s) or node_is_None(s) or s is None)):
        return None

    # Provide default values if parameters are emtpy.
    low = 0 if l is None else l.n
    upp = n if u is None else u.n
    stp = 1 if s is None or node_is_None(s) else s.n

    # Normalize bounds by `n` if they're negative.
    low = low + n if low < 0 else low
    upp = upp + n if upp < 0 else upp

    # Provide sane interpretations if bounds are still too low.
    low = 0 if low < 0 else low
    upp = 0 if upp < 0 else upp

    # Provide sane interpretations if bounds are too high.
    low = n if low > n else low
    upp = n if upp > n else upp

    rng = range(low, upp, int(math.fabs(stp)))

    if stp < 0:
        rng.reverse()

    return rng

def valid_int_slice(l, u, s, env):
    """Determine if three AST expr nodes representing the parameters to a simple
    slice are valid integers (or Nones) under type environment `env`."""

    # These are imported here because we don't want to pollute the entire util
    # module with potential circular references. In theory, util.py functions
    # shouldn't need to refer to checking or inferring, but this is a function
    # that happens to be shared between typecheck.py and infer.py.
    from typecheck import check_expr as check
    from ptype import int_t

    return ((l is None or check(l, int_t, env)) and
            (u is None or check(u, int_t, env)) and
            (s is None or node_is_None(s) or check(s, int_t, env)))

