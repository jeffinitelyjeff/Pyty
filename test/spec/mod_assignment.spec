spec mode: mod

----pass----

---
#: x : int
x = 4
---
#: antohutneoa : int
antohutneoa = 93204
---
#: b : bool
b = True
---
#: i : int
i = 4
---
#: f : float
f = -4.2
---
#: f : float
f = 3.2
---
#: a : float
#: b : float
#: c : float
a = b = c = 5.0
---
#: a : int
#: b : float
a, b = 1, 2.1
---
#: a : int
#: b : float
(a, b) = (1, 2.1)
---
#: a : int
#: b : int
[a, b] = [1, 2]
---

----fail----

---
# SUBTYPING
#: a : float
#: b : float
#: c : float
a = b = c = 5
---
# SUBTYPING
#: a : float
#: b : int
#: c : int
a = b = c = 5
---
# SUBTYPING
#: a : float
#: b : float
[a, b] = [1, 2]
---
# SUBTYPING
#: a : float
#: b : float
a, b = 1, 2.1
---
# SUBTYPING
#: a : float
#: b : float
a, b = 1, 2
---
#: b : bool
b = 4
---
#: b : bool
b = 0
---
#: i : int
i = 3.3
---
#: b : bool
b = 3.2
---
#: a : int
#: b : int
#: c : int
a = b = c = 5.0
---
#: a : int
#: b : bool
[a, b] = [1, True]
---
#: a : float
#: b : (float,)
[a, b] = [1, (1,)]
---
#: t : (int, bool, float)
t = (1, True, 5.0)
t[0] = 0
---
#: t : (int, bool, float)
t = (1, True, 5.0)
t[1] = False
---
#: t : (int, bool, float)
t = (1, True, 5.0)
t[2] = 5.1
---

----TypeUnspecifiedError----

---
a = True
---
q = 4
---

----TypeIncorrectlySpecifiedError----

---
#: b : boolean
b = True
---
#: b : Bool
b = False
---
#: i : Integer
i = 52
---
