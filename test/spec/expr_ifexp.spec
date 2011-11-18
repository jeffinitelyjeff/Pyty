spec mode: expr
expr type: IfExp

----pass----
1 if True else 0 : int
1.0 if True else 0.0 : float
True if True else False : bool
[1, 1, 1] if False else [0, 0, 0] : [int]
[1] if 5 > 2 else [1, 2, 3] : [int]
(1, 2, 3) if 5 is True else (0, 0, 0) : (int, int, int)
(1.0 if True else 1.1) if False else (0.0 if True else 0.1) : float
(1 if True else 2) if False else (0 if True else 1) : int
----fail----
(1.0 if True else 1) if False else (0.0 if True else 1) : float
(1.0 if True else 1) if False else (0.0 if True else 1.0) : float
(1, 2, 3) if 5 is True else (0, 0, 0, 0) : (int, int, int)
(1, 2, 3) if 5 is True else (0, 0, 0, 0) : (int, int, int, int)
(1, 2, 3) if 5 is True else (0, 0.0, 0) : (int, int, int)
(1, 2, 3.0) if 5 is True else (0, 0, 0) : (int, int, int)
[1, 1, 1] if False else (0, 0, 0) : (int, int, int)
[1, 1, 1] if False else (0, 0, 0) : [int]
