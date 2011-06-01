spec mode: expr
expr type: Subscript

----pass----
(1,2,3)[0] : int
(1,2,3)[1] : float
(1.0, 2, True)[0] : float
(1.0, 2, True)[1] : int
(1.0, 2, True)[1] : float
(1.0, 2, True)[2] : bool
[1, 2][0] : int
[1, 2][0] : float
[1, 2.0, 3.0][0] : float
[1, 2.0, 3.0][1] : float
[1, 2.0, 3.0][5+3-2*2] : float
[(True, False), (False, False), (True, True)][0] : (bool, bool)
[(True, False), (False, False), (True, True)][0][1] : bool
[(True, 4), (False, 1), (True, 9)][2][0] : bool
[(True, 4), (False, 1), (True, 9)][2][1] : int
[1, 2, 3][1.0] : int # this should typecheck, though it will not run
(1,)[0] : int
(1,)[0] : float
(1.0,)[0] : float

----fail----
[1, 2.0, 3.0][0] : int
[1, 2.0, 3.0][1] : int
[1, 2.0, 3.0][5+3-2*2] : int
(1, 2, 3)[5-4] : int
[(True, False), (False, False), (True, True)][1][0+1] : bool
[(True, False), (False, False), (True, True)][0+1][0+1] : bool
(1, 2, 3)[1.0] : int

----TypeIncorrectlySpecifiedError----
[(True, False), (False, False)][0] : ()