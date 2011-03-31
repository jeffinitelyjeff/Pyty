spec mode: mod

----pass----
# TEST NO 1
#: x : float
x = 3
---
#: x : int
x = 3
#: y : float
y = x
---
#: x : float
x = 4.2 + 4
---
#: x : float
x = 4 + (3 - 11 / 2) % 3.0
---
# TEST NO 5
#: x : float
x = 4 + (3 - 11 / 2) % 3
---
#: x : float
x = 4 + (3.24 - 1432.22 % 3.249)
----fail----
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
# TEST NO 10
#: x : int
x = 4 - (3 + 11 % 2) / 2.0
---
#: y : int
y = 4 + 3.0 + x
----TypeUnspecifiedError----
#: y : float
y = 4 + 3.0 + x
---
y = 4 + 3.0
---
