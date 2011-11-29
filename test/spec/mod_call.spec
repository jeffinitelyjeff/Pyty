spec mode: mod

----pass----

---
#: foo: int -> int
def foo(i):
    return i

#: bar: int
bar = foo(5)
---
#: foo: () -> int
def foo():
    return 29

#: bar: int
bar = foo()
---
#: foo: int -> int
def foo(i):

    #: bar: (int, int) -> int
    def bar(i, j):
        return i + j

    return bar(5, i)

foo(6)
---
#: foo: int -> int
def foo(i):
    return i + 1

#: bar: (int, int, int -> int) -> (int -> int)
def bar(i, j, f):
    return j + f(i)

bar(1, 2, foo)
---

----fail----

---
#: foo: int -> ()
def foo(i):
    return

#: bar: int
bar = foo(5)
---
#: foo: () -> int
def foo():
    return 29

#: bar: int
bar = foo(5)
---
#: foo: () -> int
def foo():
    return 29

#: bar: int
bar = foo(5, 2)
---
#: foo: () -> int
def foo():
    return 29

#: bar: int
bar = foo
---
