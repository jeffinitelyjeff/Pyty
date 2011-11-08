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
a = 83.3
#: b : float
b = 5.8
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
#: l : [int]
l = [1,2,3]
l += [4]
l *= 3
---
#: l : [int]
#: n : int
l = [1,2,3]
l += [n]
n = 3
l *= n
---
#: l : [float]
#: n : int
l = [1.0, 2.0, 3.0]
l += [4.0, 5.0, 6.0]
l += []
n = 3
l *= n
---
#: l : [(int, float)]
l = [(1, 1.0), (2, 2.0), (3, 3.0)]
l += [(4, 4.0)]
l *= 5
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
# SUBTYPING
#: a : float
a = 3.0
a += 5
---
# SUBTYPING
#: a : float
a = 3
a += 5.0
---
# SUBTYPING
#: a : int
#: b : float
a /= b
---
# SUBTYPING
#: a : float
a = 432
a //= 342.3
---
#: l : [int]
l = [1,2,3]
l += [4]
l *= 3.5
---
#: l : [int]
#: n : float
l = [1,2,3]
l += [n]
n = 3.9
l *= n
---
#: l : [float]
#: n : int
l = [1.0, 2.0, 3.0]
l += [4.0, 5.0, 6.0]
l += [True]
n = 3
l *= n
---
#: l : [(int, float)]
l = [(1, 1.0), (2, 2.0), (3, 3.0)]
l += [(4.0, 4)]
l *= 5
---
