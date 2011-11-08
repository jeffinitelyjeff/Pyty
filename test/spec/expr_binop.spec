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
[1, 2] + [3, 4] : [int]
[1.0, 2.0] + [3.0, 4.0] : [float]
[True, False] + [False, True] : [bool]
[1, 2] * 3 : [int]
[1.0, 2.0] * 7 : [float]
[True, False] * 4 : [bool]
3 * [1, 2] : [int]
7 * [1.0, 2.0] : [float]
4 * [True, False] : [bool]
(1, 2) + (3, 4) : (int, int, int, int)
(True,) + (False,) : (bool, bool)
(1.0,) + (2.0,) : (float, float)
(True, True, False) * 3 : (bool, bool, bool, bool, bool, bool)
2 * (True, True, False) : (bool, bool, bool, bool)
(1, 2) * 4 : (int, int, int, int, int, int, int, int)
3 * (1, 2) : (int, int, int, int, int, int)
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
[1, 2] + [3.0, 4] : [int]
[1.0, 2] + [3.0, 4.0] : [float] # SUBTYPING
[True, 1] + [False, 1] : [bool]
[1, 2] * 3.0 : [int]
[1.0, 2.0] * 7.0 : [float]
[True, 1] * 4 : [bool]
3.0 * [1, 2] : [int]
7.9 * [1.0, 2.0] : [float]
4.0 * [True, False] : [bool]
(True, True, False) * 3.0 : (bool, bool, bool, bool, bool, bool)
2.0 * (True, True, False) : (bool, bool, bool, bool)
(1, 2) * 4.0 : (int, int, int, int, int, int, int, int)
3.0 * (1, 2) : (int, int, int, int, int, int)

