spec mode: mod

----pass----
---
#: x : int
x = 4 + (3 - 11 / 2) % 2
---
#: x : float
x = 4.2 + (3.1 - 11.3 / 2.0) % 3.09
---
#: x : int
x = 4 / 2 * 3 % 9
---
----fail----
---
#: x : bool
x = True * 2 / 3 % 1
---
----TypeUnspecifiedError----
---
x = 4 + (3 - 11 / 2) % 3
---

