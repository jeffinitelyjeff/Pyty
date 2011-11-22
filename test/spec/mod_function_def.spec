spec mode: mod

----pass----
---
#: foo: int -> int
def foo(bar):
    return bar
---
#: foo: int -> int
def foo(bar):
    return bar + 1
---
#: foo: float -> float
def foo(bar):
    return bar + 1.0
---
----fail----
---
#: foo: int -> int
def foo(bar):
    return bar + 1.0
---
