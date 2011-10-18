spec mode: mod

----pass----

---
#: x : [int]
x = [1,2,3,4,5]
---
#: x : [float]
x = [1.8, 2.2, 3.4, 4.2, 5.9]
x[0] = 2.0
---
#: x : [float]
x = [1.8, 2.2, 3.4, 4.2, 5.9]
#: a : int
a = 0
x[a] = 3.0
---
#: x : [bool]
x = [True, False, True]
#: a : int
#: b : int
a = 3
b = 4
x[b-a] = True
---

----fail----

---
#: x : [int]
x = [1, 2, 3.4, 5]
---
#: x : [float]
x = [1.8, 2.2, 3.5]
x[0.5] = 2.0
---
#: x : [float]
x = [1.8, 2.2, 3.4, 4.2, 5.9]
x[0] = [2.0]

