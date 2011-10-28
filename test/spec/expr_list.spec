spec mode: expr
expr type: List

----pass----
[1,2,3] : [int]
[1] : [int]
[3.0, 4.0] : [float]
[True, False, True] : [bool]
[[True, False], [False, True]] : [[bool]]

----fail----
[5.0, 3.0, 4] : [float] # SUBTYPING
[1.0, 2] : [int]
[1.0, 2.0, True] : [int]
[1.0, 2.0, True] : [float]
[True, 2] : [int]
[True, 2] : [float]
[[True, False], [False, 0]] : [[bool]]

----TypeIncorrectlySpecifiedError----
[[True, False], [False, 0]] : [ [] ]
