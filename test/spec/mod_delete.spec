spec mode: mod

----pass----

---
#: x : int
x = 5
del x
---
#: x : int
#: y : int
x = 5
y = 6
del x, y
---
#: x : int
#: y : int
x = 5
y = 6
del [x, y]
---
#: x : int
#: y : int
x = 5
y = 6
del [x, y, 0][0:2]
---
# not sure if this should really pass...
del x
---

----fail----

---
del (x, y)
---

