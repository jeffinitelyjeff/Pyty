spec mode: expr
expr type: Compare

----pass----
1 == 2 : bool
1.0 == 2.0 : bool
1 != 2 : bool
1.0 != 2.0 : bool
1 is 2 : bool
1.0 is 2.0 : bool
1 is not 2 : bool
1.0 is not 2.0 : bool
1.0 is 2 : bool
1 is 2.0 : bool
1.0 is not 2 : bool
1 is not 2.0 : bool
True is 2 : bool
1.0 is True : bool
1 is not False : bool
False is not 2.0 : bool
1 < 2 : bool
1.0 < 2.0 : bool
1 <= 2 : bool
1.0 <= 2.0 : bool
1 > 2 : bool
1.0 <= 2.0 : bool
1 >= 2 : bool
1.0 >= 2.0 : bool
1 > 2 < -3 >= 0 <= 4 : bool
1 is 2 is not-3 == 0 != 4 : bool
5.8 > 6.2 < -5.3 == 0.0 != 3.9 : bool
5.8 is 6.2 != -5.3 == 0.0 is not 3.9 : bool
1 > 2 < -3 is not 0 is 4 : bool
1 > 2 is not 2.0 == 3.1 : bool
1 < 2 == 2.0 < 2.1 : bool
----fail----
1.0 < 2 : bool # SUBTYPING
1 < 2.0 : bool # SUBTYPING
1.0 <= 2 : bool # SUBTYPING
1 <= 2.0 : bool # SUBTYPING
1.0 > 2 : bool # SUBTYPING
1 <= 2.0 : bool # SUBTYPING
1.0 >= 2 : bool # SUBTYPING
1 >= 2.0 : bool # SUBTYPING
1 > 2.0 < -3 == 0 != 4 : bool # SUBTYPING
5.8 > 6.2 < -5 == 0.0 != 3.9 : bool # SUBTYPING
1.0 < True : bool
1 > 2.0 < -3 == 0 != True : bool
5.8 > 6.2 < False == 0.0 != 3.9 : bool
1.0 < True : int
5 != False : float
5 is True : int
5 is not False : float
1 < 3 : int
1 < 3.0 : float
1 > 2.0 is not 2 == 3.1 : bool
1 < 2 < 2.0 < 2.1 : bool
