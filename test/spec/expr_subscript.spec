spec mode: expr
expr type: Subscript

----pass----
## String indexing
"test string"[3] : str
"test string"[0] : str
r"test string"[-3] : str
ur"test string"[3] : unicode
u"test string"[3] : unicode
ur"test string"[3] : unicode

## String slicing
"test string"[1:10:3] : str
"test string"[:10:3] : str
"test string"[1::3] : str
"test string"[1:10:] : str
"test string"[1::] : str
"test string"[:10:] : str
"test string"[::3] : str
"test string"[::] : str

## List indexing
[1, 2, 3][3] : int
[1.0, 2.0, 3.0][4] : float
[True, False, False][-3] : bool
["1", "2", "3"][0] : str
[u"1.0", u"2.0", u"3.0"][0] : unicode
[None, None, None][3] : unit

## List slicing
[0, 1, 2, 3, 4, 5, 6][1:10:3] : [int]
[0, 1, 2, 3, 4, 5, 6][:10:3] : [int]
[0, 1, 2, 3, 4, 5, 6][1::3] : [int]
[0, 1, 2, 3, 4, 5, 6][1:10:] : [int]
[0, 1, 2, 3, 4, 5, 6][1::] : [int]
[0, 1, 2, 3, 4, 5, 6][:10:] : [int]
[0, 1, 2, 3, 4, 5, 6][::3] : [int]
[0, 1, 2, 3, 4, 5, 6][::] : [int]

## Tuple indexing
(1, 2, 3)[2] : int
(1.0, 2.0, 3.0)[1] : float
(True, False, False)[-3] : bool
("1", "2", "3")[0] : str
(u"1.0", u"2.0", u"3.0")[0] : unicode
(None, None, None)[2] : unit
(None, 5, None)[2] : unit
(True, 3.0, None)[2] : unit

## Tuple slicing
(0, 1, 2, 3, 4, 5, 6)[1:4:2] : (int, int)
(0, 1, 2, 3, 4, 5, 6)[:3:2] : (int, int)
(0, 1, 2, 3, 4, 5, 6)[1::3] : (int, int)
(0, 1, 2, 3, 4, 5, 6)[1:5:] : (int, int, int, int)
(0, 1, 2, 3, 4, 5, 6)[1::] : (int, int, int, int, int, int)
(0, 1, 2, 3, 4, 5, 6)[:5:] : (int, int, int, int, int)
(0, 1, 2, 3, 4, 5, 6)[::3] : (int, int, int)
(0, 1, 2, 3, 4, 5, 6)[::] : (int, int, int, int, int, int, int)
(True, "1", u'1.0', 5.0, None)[-500:] : (bool, str, unicode, float, unit)
(True, "1", u'1.0', 5.0, None)[-500:-1] : (bool, str, unicode, float)
(True, "1", u'1.0', 5.0, None)[-500:-1:-1] : (float, unicode, str, bool)

## Nested collections
[(1, 2, 3), (4, 5, 6), (7, 8, 9)][0] : (int, int, int)
([1.0, 2.0], [3.0, 4.0])[-1] : [float]
[(True, False), (False, False), (True, True)][0] : (bool, bool)
[(True, 4), (False, 1), (True, 9)][2] : (bool, int)
[(["a", "b"], ["c", "d"]), (["e", "f"], ["g", "h"])][0] : ([str], [str])

## Nested operations
[(1, 2, 3), (4, 5, 6), (7, 8, 9)][0][2] : int
([1.0, 2.0], [3.0, 4.0])[-1][0] : float
[(True, False), (False, False), (True, True)][0][1] : bool
[(True, 4), (False, 1), (True, 9)][2][0] : bool
[(True, 4), (False, 1), (True, 9)][2][1] : int
[(["a", "b"], ["c", "d"]), (["e", "f"], ["g", "h"])][0][1] : [str]
[(["a", "b"], ["c", "d"]), (["e", "f"], ["g", "h"])][0][1][-1] : str
"hello"[0][0][0] : str
u"hell"[0][0][0] : unicode
[(1, 2, 3), (4, 5, 6), (7, 8, 9)][:3:2][2] : (int, int, int)
([1.0, 2.0], [3.0, 4.0])[-1][:1:2] : [float]
[(True, False), (False, False), (True, True)][1::2][1][0] : bool
[(True, 4), (False, 1), (True, 9)][2][0:] : (bool, int)
[(True, 4), (False, 1), (True, 9)][2][-1::2] : (int,)
"hello"[0][0][0] : str
u"hell"[0][0][0] : unicode


----fail----
## String indexing
u"test string"[3] : str
u"test string"[0] : str
ur"test string"[-3] : str
r"test string"[3] : unicode
"test string"[3] : unicode
r"test string"[3] : unicode

## String slicing
u"test string"[1:10:3] : str
"test string"[:10:3] : unicode
u"test string"[1::3] : str
"test string"[1:10:] : unicode
u"test string"[1::] : str
"test string"[:10:] : unicode
u"test string"[::3] : str
"test string"[::] : unicode

## List indexing
[1.0, 2, 3][3] : int
[1, 2, 3][3.0] : int
[1.0, 2.0, 3.0][4.3] : float
[1.0, 2, 3.0][4] : float
[True, 0, False][-3] : bool
["1", u"2", "3"][0] : str
["1", u"2", "3"][9.1] : str
[u"1.0", u"2.0", "3.0"][0] : unicode
[u"1.0", u"2.0", u"3.0"][0.0] : unicode
[None, None, 4][3] : unit
[None, None, 4][3.1] : unit

## List slicing
[0.0, 1, 2, 3, 4, 5, 6][1:10:3] : [int]
[0, 1.0, 2, 3, 4, 5, 6][:10:3] : [int]
[0, 1, 2.0, 3, 4, 5, 6][1::3] : [int]
[0, 1, 2, 3.0, 4, 5, 6][1.0:10:] : [int]
[0, 1, 2, 3, 4, 5.0, 6][1::] : [int]
[0, 1, 2, 3, 4, 5, 6][:10.0:] : [int]
[0, 1.0, 2.0, 3, 4, 5, 6][::3] : [int]
[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0][3.0:9.0:1.0] : [int]


## Tuple indexing
(1, 2, 3)[-10] : int
(1.0, 2.0, 3.0)[3] : float
(True, False, False)[-5] : bool
("1", "2", "3")[100] : str
("1.0", u"2.0", u"3.0")[0] : unicode
(None, 6.0, 5)[1] : unit
(True, "1", u'1.0', 5.0, None)[-500] : unit
(True, "1", u'1.0', 5.0, None)[-500] : bool
(True, "1", u'1.0', 5.0, None)[-500] : str
(True, "1", u'1.0', 5.0, None)[-500] : unicode
(True, "1", u'1.0', 5.0, None)[-500] : float

## Tuple slicing
(0.0, 1, 2, 3, 4, 5, 6)[1:10:3] : [int]
(0, 1.0, 2, 3, 4, 5, 6)[:10:3] : [int]
(0, 1, 2.0, 3, 4, 5, 6)[1::3] : [int]
(0, 1, 2, 3.0, 4, 5, 6)[1.0:10:] : [int]
(0, 1, 2, 3, 4, 5.0, 6)[1::] : [int]
(0, 1, 2, 3, 4, 5, 6)[:10.0:] : [int]
(0, 1.0, 2.0, 3, 4, 5, 6)[::3] : [int]
(0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0)[3.0:9.0:1.0] : [int]
(0, 1, 2, 3, 4, 5, 6)[1:10:3] : [int] # indices out of range
(0, 1, 2, 3, 4, 5, 6)[:10:3] : [int] # indices out of range
(0, 1, 2, 3, 4, 5, 6)[1::3] : [int] #
(0, 1, 2, 3, 4, 5, 6)[1:10:] : [int]
(0, 1, 2, 3, 4, 5, 6)[1::] : [int]
(0, 1, 2, 3, 4, 5, 6)[:10:] : [int]
(0, 1, 2, 3, 4, 5, 6)[::3] : [int]
(0, 1, 2, 3, 4, 5, 6)[::] : [int]


## Nested collections
[(1, 2, 3), (4, 5, 6.0), (7, 8, 9)][0] : (int, int, int)
([1.0, 2.0], [3, 4.0])[-1] : [float]

## Nested operations
[(1, 2.0, 3), (4, 5, 6), (7, 8, 9)][0][2] : int
([1.0, 2.0], [3.0, 4])[-1][0] : float
[(True, False), (False, False), (True, True)][0.0][1.0] : bool
[(True, 4), (False, 1), (True, 9)][2.0][0] : bool
[(True, 4), (False, 1), (True, 9.0)][2][1] : int
[(["a", "b"], ["c", "d"]), (["e", "f"], ["g", "h"])][0][1.0] : [str]
[(["a", "b"], ["c", "d"]), (["e", "f"], ["g", "h"])][0][1.0][-1] : str
[(1, 2, 3), (4, 5, 6), (7, 8, 9)][2][4] : int
([1.0, 2.0], [3.0, 4.0])[-1][:1:2] : float
[(True, False), (False, False), (True, True)][1::2][1] : bool
[(True, 4), (False, 1), (True, 9)][2][0:-1] : bool
[(True, 4), (False, 1), (True, 9)][2][-1::2] : int


