spec mode: mod

----pass----

---
#: a : int
a = 5
a += 5
---
# this is bad semantically, but it should typecheck
#: a : int
a += 5
---
#: a : float
a = 3.0
a += 5
---
#: a : float
a = 3
a += 5.0
---
#: a : float
a = 5.0
a -= 3.8
---
#: a : int
a = 3
a -= 2
---
#: a : float
a = 8.0
a *= 9.3
---
#: a : int
a = 9
a *= 3
---
#: a : int
a = 98
a /= 304
---
#: a : float
a = 83
#: b : float
a /= b
---
#: a : int
#: b : float
a /= b
---
#: a : int
a = 5
a **= 2
---
#: a : int
a = 5
a <<= 2
---
#: a : int
a = 5
a >>= 2
---
#: a : int
a = 256
a |= 2
---
#: a : int
a = 324
a &= 324
---
#: a : int
a = 432
a ^= 4231
---
#: a : int
a = 432
a //= 432
---
#: a : float
a = 432
a //= 342.3
---

----fail----

---
#: a : int
a = 8
a <<= True
---
#: a : int
a = 9
a >>= False
---
#: a : float
#: b : int
a <<= b
---


