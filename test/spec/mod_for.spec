spec mode: mod

----pass----

---
#: x : int
for x in [1,2,3]:
    print x
---
#: x : bool
for x in [True, False, True, True]:
    if x:
        print "Hi"
---
#: x : bool
for x in [True, False, True, True]:
    if x:
        print "Hi"
else:
		print "Bye"
---
#: x : (bool, float)
for x in [(True, 1.5), (False, 1.6), (True, 1.7)]:
    #: y : float
    if x[0]:
        y = x[1] + 5.0
---
#: x : bool
#: y : float
for (x, y) in [(True, 1.5), (False, 1.6), (True, 1.7)]:
    #: z : float
    if x:
        z = y + 5.0
---
