spec mode: expr
expr type: Name

These expression unit tests aren't as helpful as most, since the only
the Name expressions we can use without environments are booleans

----pass----
True : bool
False : bool
----TypeUnspecifiedError----
a : int
true : bool
false : int
