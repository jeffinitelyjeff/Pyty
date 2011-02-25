spec mode: expr
expr type: BinOp

----pass----
5+4 : int
5.2*3.1 : float
3 / 7 : int
3.0 / 7.0 : float
8 % 3 : int
8.3 % 3.0 : float
3 - 9 : int
3.1 - 9.2 : float
----fail----
False + True : bool
False + 0 : bool
False + 3 : int
False + 3.2 : float
False / True : bool
True * True : bool
False % False : bool
False % 1 : int
False % 1.0 : float


