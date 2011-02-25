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

----fail----

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
