import re
from lepl import *

class ListSpec(List):
    def __init__(self, t):
        self.t = t
        super(List, self).__init__([t])

    def typ(self):
        return self.t

class TupleSpec(List):
    def __init__(self, ts):
        self.ts = ts
        super(List, self).__init__(ts)

    def typ(self, i):
        return self.ts[i]

    def typs(self):
        return self.ts

class DictSpec(List):
    def __init__(self, key_t, val_t):
        self.key_t = key_t
        self.val_t = val_t
        super(List, self).__init__([key_t, val_t])

    def key_typ(self):
        return self.key_t

    def val_typ(self):
        return self.val_t

class FuncSpec(List):
    def __init__(self, par_t, ret_t):
        self.par_t = par_t
        self.ret_t = ret_t
        super(List, self).__init__([par_t, ret_t])

    def par_typ(self):
        return self.par_t

    def ret_typ(self):
        return self.ret_t

class TypeSpecParser:
    int_tok = Token(r'int')
    float_tok = Token(r'float')
    bool_tok = Token(r'bool')
    str_tok = Token(r'str')

    list_start = Token(r'\[')
    list_end = Token(r'\]')

    tuple_start = Token(r'\(')
    tuple_div = Token(r',')
    tuple_end = Token(r'\)')

    dict_start = Token(r'\{')
    dict_div = Token(r':')
    dict_end = Token(r'\}')

    fn_div = Token(r'\->')

    typ = Delayed()

    base_typ = int_tok | float_tok | bool_tok | str_tok

    lst = ~list_start & typ & ~list_end > ListSpec

    tup_comp = Delayed()
    tup_comp += tuple_div & typ & Optional(tup_comp)
    tup = tuple_start & typ & tup_comp & tuple_end > TupleSpec

    dct = dict_start & typ & dict_div & dict_end > DictSpec

    fun = tup & fn_div & typ > FuncSpec

    typ += base_typ | lst | tup | dct | fun
    
    @staticmethod
    def parse(s):
        return sexpr_to_tree(TypeSpecParser.typ.parse(s))

class T:
    @staticmethod
    def p(s):
        return TypeSpecParser.parse(s)
