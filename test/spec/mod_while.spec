spec mode: mod

----pass----

---
#: x : int
while True:
    x = 5
---
#: x : bool
#: y : float
x = True
while x:
    y = 0.2
---
# this should work even though it doesn't make sense
#: x : bool
while x:
    x = True
---

----fail----

---
#: x : int
while x:
    x = 0
---
#: x : int
x = 0
while x:
    x = 1
---
#: x : int
x = 1
while x:
    x = 0
---

----TypeUnspecifiedError----

---
#: x : int
while y:
    x = 0
---
#: x : bool
x = True
while x:
    y = 0
---
#: x : bool
x = False
while x:
    y = 0
---
