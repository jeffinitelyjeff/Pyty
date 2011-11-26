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
#: foo: int -> ()
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
