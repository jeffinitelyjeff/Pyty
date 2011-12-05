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


