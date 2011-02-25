spec mode: expr
expr type: Num

----pass----
1 : int
0 : int
-2.3 : float
-4 : int
-0 : int
-10.31 : float

----fail----
True : int
4*3 : int
-4*2.3 : float
True*2 : int
