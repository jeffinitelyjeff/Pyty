spec mode: mod

----pass----

---
#: foo: int -> int
def foo(i):
    return i

#: bar: int
bar = foo(5)
---
#: foo: unit -> int
def foo():
    return 29

#: bar: int
bar = foo()
---
#: foo: int -> int
def foo(i):
    return i + 1

#: bar: (int, int, int -> int) -> int
def bar(i, j, f):

    return j + f(i)

#: baz: int
baz = bar(1, 2, foo)
---
#: foo: int -> int
def foo(i):

    #: bar: (int, int) -> int
    def bar(i, j):
        return i + j

    return bar(5, i)

#: baz : int
baz = foo(6)
---
#: foo: int -> (int -> int)
def foo(i):

    #: bar: int -> int
    def bar(j):
        return i + j

    return bar

#: baz : int -> int
baz = foo(6)
---
def foo(i):        #: foo: int -> (int -> int)

    def bar(j):    #: bar: int -> int
        return i + j

    return bar

baz = foo(6)       #: baz : int -> int
---

----fail----

---
#: foo: int -> unit
def foo(i):
    return

#: bar: int
bar = foo(5)
---
#: foo: unit -> int
def foo():
    return 29

#: bar: int
bar = foo(5)
---
#: foo: unit -> int
def foo():
    return 29

#: bar: int
bar = foo(5, 2)
---
#: foo: unit -> int
def foo():
    return 29

#: bar: int
bar = foo
---
#: foo: int -> (int -> int)
def foo(i):

    #: bar: (int, int) -> int
    def bar(i, j):
        return i + j

    return bar(5, i)

#: baz : int
baz = foo(6)
---
