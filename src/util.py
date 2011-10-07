import logging
from datetime import datetime

"""
Contains useful helper functions that are not directly tied to the purpose of
other source code files.
"""

### Some short hand

def cname(obj):
    """Returns the name of the class of the provided object. This is helpful
    because there are many assert statements which center around checking the
    types of objects, and so it helps to include the name of classes in
    assertion errors.

    @rtype: C{str}.
    """

    return obj.__class__.__name__

### Set operations

def are_disjoint(set1, set2):
    """Determines whether two sets are disjoint.

    @type set1: C{set}
    @param set1: a set.
    @type set2: C{set}.
    @param set2: a set.
    @rtype: C{bool}.
    @return: C{True} if C{set1} and C{set2} are disjoint (ie, if they do not
    share any common elements).
    """

    return set1.intersection(set2) == set([])

def disjoint_sums_of(sets, union):
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

            if i != j and not are_disjoint(s1, s2):
                return False

    return u == union


