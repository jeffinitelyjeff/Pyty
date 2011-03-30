spec mode: mod

----pass----

---
#: x : int
if False:
    x = 4
---
#: x : int
x = 5
if x > 3:
    x = 1
else:
    x = 0
---
#: x : float
if True:
    x = 3.2
else:
    x = 4.0
---
#: x : int
#: y : float
x = 3
if x == 0:
    y = 0.0
elif x == 1:
    y = 1.0
elif x == 2:
    y = 2.0
else:
    y = 3.0
---
# this should typecheck correctly even though it has no meaning
#: x : int
#: y : int
if x > 0:
    y = 3
---
#: x : int
x = 3
if x == 0:
    #: y: float
    y = 0.0
elif x == 3:
    #: y: bool
    y = True
---
#: x : bool
if x:
    #: y : int
    y = 3
---
    

----fail----

---
#: x : int
if True:
    x = 3
else:
    x = 3.3
---
#: x : int
if x:
    x = 1
---
#: x : float
if x:
    x = 1
---
#: x : int
if 0:
    x = 1
---
#: x : int
if 0.0:
    x = 1
---
#: x : int
if 1.0:
    x = 1
---
#: x : int
#: y : float
if x > 0:
    y = 3.0
else:
    y = bool
---
#: x : int
#: y : int
x = 0
y = 3
if y > 0:
    #: y : float
    y = 3.0
x = y
---
    


----TypeUnspecifiedError----

---
#: x : int
if True:
    x = 3
else:
    y = 3
---
#: x : int
if y:
    x = 3
---
#: x : int
if y > 0:
    x = 0
---
#: x : int
if x > 0:
    #: y : int
    y = 3
x = y
---
#: x : int
if x > 0:
    #: y : int
    y = 3
else:
    y = 4
---

