spec mode: expr
expr type: Str

----pass----
"hello" : str
"""hello""" : str
'hello' : str
'''hello''' : str
r"hello" : str
r"""hello""" : str
r'hello' : str
r'''hello''' : str
u"hello" : unicode
u"""hello""" : unicode
u'hello' : unicode
u'''hello''' : unicode
ur"hello" : unicode
ur"""hello""" : unicode
ur'hello' : unicode
ur'''hello''' : unicode

----fail----
"hello" : unicode
"""hello""" : unicode
'hello' : unicode
'''hello''' : unicode
r"hello" : unicode
r"""hello""" : unicode
r'hello' : unicode
r'''hello''' : unicode
u"hello" : str      # SUBTYPING
u"""hello""" : str  # SUBTYPING
u'hello' : str      # SUBTYPING
u'''hello''' : str  # SUBTYPING
ur"hello" : str     # SUBTYPING
ur"""hello""" : str # SUBTYPING
ur'hello' : str     # SUBTYPING
ur'''hello''' : str # SUBTYPING

----AssertionError----
# assertion errors because they're not str expressions
5 : str
5.0 : str
True : str
None : str


