spec mode: mod

----fail----
# SUBTYPING
#: x : float
x = 3
---
# SUBTYPING
#: x : int
x = 3
#: y : float
y = x
---
# SUBTYPING
#: x : float
x = 4.2 + 4
---
# SUBTYPING
#: x : float
x = 4 + (3 - 11 / 2) % 3.0
---
# SUBTYPING
#: x : float
x = 4 + (3 - 11 / 2) % 3
---
# SUBTYPING
#: x : float
x = 4 + (3.24 - 1432.22 % 3.249)
---
#: x : int
x = 3.0
---
#: x : float
x = 5.0
#: y : int
y = x
---
#: x : float
x = 5
#: y : int
y = x
---
#: x : int
x = 4 - (3 + 11 % 2) / 2.0
---
#: y : int
y = 4 + 3.0 + x
----TypeUnspecifiedError----
#: y : float
y = 4.0 + 3.0 + x
---
#: y : float
y = 4.0 * x + 3
---
y = 4 + 3.0
---
