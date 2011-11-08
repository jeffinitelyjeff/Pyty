spec mode: expr
expr type: Compare

----pass----
1 == 2 : bool
1.0 == 2.0 : bool
1 != 2 : bool
1.0 != 2.0 : bool
1 < 2 : bool
1.0 < 2.0 : bool
1 <= 2 : bool
1.0 <= 2.0 : bool
1 > 2 : bool
1.0 <= 2.0 : bool
1 >= 2 : bool
1.0 >= 2.0 : bool
1 > 2 < -3 == 0 != 4 : bool
5.8 > 6.2 < -5.3 == 0.0 != 3.9 : bool
----fail----
1 == 2.0 : bool # SUBTYPING
1 == 2.0 : bool # SUBTYPING
1.0 != 2 : bool # SUBTYPING
1 != 2.0 : bool # SUBTYPING
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
5 != False : bool
1 > 2.0 < -3 == 0 != True : bool
5.8 > 6.2 < False == 0.0 != 3.9 : bool
1.0 < True : int
5 != False : float
1 < 3 : int
1 < 3.0 : float
