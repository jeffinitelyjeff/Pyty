spec mode: expr
expr type: UnaryOp

----pass----
-(5) : int
-(4.5) : float
~5 : int
~439 : int
-(~43) : int
-(~43) : float
+4.94 : float
not True : bool
not False : bool
----fail----
-True : int
~3.34 : float
-(3.5) : int
not 5 : bool
not 0 : bool
not 5 : int
not 0 : int
