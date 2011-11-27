spec mode: mod

----pass----

---
#: foo: bool -> int
def foo(bar):
    return 5
---
#: foo: int -> int
def foo(bar):
    return 9
---
#: foo: () -> int
def foo():
    return 4
---
#: foo: () -> float
def foo():
    return 3.93
---
#: foo: int -> int
def foo(bar):
    return bar + 1
---
#: foo: bool -> bool
def foo(bar):
    return True
---
#: foo: int -> bool
def foo(bar):
    #: x : int
    x = bar
    return False
---
#: foo: () -> bool
def foo():
    return True
---
#: foo: () -> float
def foo():
    return 3.93
---
#: foo: int -> int
def foo(bar):
    return bar + 1
---
#: foo: float -> float
def foo(bar):
    return bar + 1.0
---
#: foo: int -> ()
def foo(bar):
    return
---
#: foo: int -> ()
def foo(bar):
    #: x : int
    x = bar + 1

    return
---
#: foo: int -> int
def foo(bar):
    #: x : int
    x = bar + 1

    return x
---
#: foo: ([int], int, [int]) -> [int]
def foo(l0, i, l1):
    #: l2 : [int]
    l2 = i * l0

    return l2 + l1
---
#: foo: ([int], (bool, bool)) -> (bool, bool)
def foo(l, t):
    return t
---
#: foo: int -> int
def foo(i):

    #: bar: bool -> bool
    def bar(i):
        return i

    return i
---
#: foo: int -> [bool]
def foo(i):

    if i > 0:
        return [True, False, True]
    elif i == 0:
        return [True, False, False]
    else:
        return [False, True, False]

    return [False, False, False]
---
#: foo: int -> ()
def foo(i):
    if i > 0:
        return
    else:
        print "yo"
        return
---
#: foo: int -> ()
def foo(i):
    return i

#: bar: int -> ()
bar = foo
---
#: foo: int -> ()
def foo(i):
    return i

#: bar: (int -> ()) -> int
def bar(f):
    return 0
---


----fail----

---
#: foo: int -> int
def foo(bar):
    return bar + 1.0
---
#: foo: bool -> int
def foo(bar):
    return bar
---
#: foo: int -> int
def foo(bar, baz):
    return 9
---
#: foo: () -> int
def foo(bar):
    return 4
---
#: foo: int -> int
def foo(bar):
    return bar or False
---
#: foo: bool -> bool
def foo(bar):
    return bar + 0
---
#: foo: int -> bool
def foo(bar):
    return bar
---
#: foo: () -> bool
def foo():
    return 4
---
#: foo: () -> float
def foo():
    #: x : int
    return x
---
#: foo: int -> int
def foo(bar, baz):
    return bar + 1
---
#: foo: float -> float
def foo(bar):
    return bar + 1
---
#: foo: int -> ()
def foo(bar):
    return 5
---
#: foo: int -> ()
def foo(bar):
    #: x : int
    x = bar + 1
    #: y : bool
    y = x > 5

    return y
---
#: foo: int -> ()
def foo(bar):
    #: x : int
    x = bar + 1

    return x
---
#: foo: ([int], float, [int]) -> [int]
def foo(l0, i, l1):
    #: l2 : [int]
    l2 = i * l0

    return l2 + l1
---
#: foo: ([int], (bool, bool)) -> (int, int)
def foo(l, t):
    return t
---
#: foo: int -> int
def foo(i):

    #: bar: int -> bool
    def bar(i):
        return i

    return i
---
#: foo: int -> int
def foo(i):

    #: bar: bool -> int
    def bar(i):
        return i

    return i
---
#: foo: bool -> int
def foo(i):

    #: bar: bool -> bool
    def bar(i):
        return i

    return i
---
#: foo: int -> bool
def foo(i):

    #: bar: bool -> bool
    def bar(i):
        return i

    return i
---
#: foo: int -> [bool]
def foo(i):

    if i > 0:
        return (True, False, True)
    elif i == 0:
        return [True, False, False]
    else:
        return [False, True, False]

    return [False, False, False]
---
#: foo: int -> [bool]
def foo(i):

    if i > 0:
        return [True, False, True]
    elif i == 0:
        return (True, False, False)
    else:
        return [False, True, False]

    return [False, False, False]
---
#: foo: int -> [bool]
def foo(i):

    if i > 0:
        return [True, False, True]
    elif i == 0:
        return [True, False, False]
    else:
        return (False, True, False)

    return [False, False, False]
---
#: foo: int -> [bool]
def foo(i):

    if i > 0:
        return [True, False, True]
    elif i == 0:
        return [True, False, False]
    else:
        return [False, True, False]

    return (False, False, False)
---
#: foo: bool -> ()
def foo(i):
    if i > 0:
        return
    else:
        print "yo"
        return
---
#: foo: int -> ()
def foo(i):
    return i
---
#: foo: int -> ()
def foo(i):
    return i

#: bar: int -> ()
bar = foo()
---
#: foo: int -> ()
def foo(i):
    return i

#: bar: (int -> ()) -> int
def bar(f):
    return f
---




----TypeUnspecifiedError----

---
#: foo: () -> float
def foo():
    return 3.93 + bar
---
#: foo: int -> ()
def foo(bar):
    return x
---
#: foo: int -> int
def foo(i):

    def bar(i):
        return i

    return i
---
#: foo: int -> [bool]
def foo(i):

    if x > 0:
        return [True, False, True]
    elif x == 0:
        return [True, False, False]
    else:
        return [False, True, False]

    return [False, False, False]
---
