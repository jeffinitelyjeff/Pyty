import re
from lepl import *

class ListSpec(List):
    def __init__(self, t):
        self.t = t
        return List(['list', t])

    def typ(self):
        return self.t

class TupleSpec(List):
    def __init__(self, ts):
        self.ts = ts
        lst = ['tuple']
        lst.extend(ts)
        return List(lst)

    def typ(self, i):
        return self.ts[i]

    def typs(self):
        return self.ts

class DictSpec(List):
    def __init__(self, key_t, val_t):
        self.key_t = key_t
        self.val_t = val_t
        return List(['dict', key_t, val_t])

    def key_typ(self):
        return self.key_t

    def val_typ(self):
        return self.val_t

class FuncSpec(List):
    def __init__(self, par_t, ret_t):
        self.par_t = par_t
        self.ret_t = ret_t
        return List(['fun', par_t, ret_t])

    def par_typ(self):
        return self.par_t

    def ret_typ(self):
        return self.ret_t

class TypeSpecParser:
    int_tok = Token('int')
    float_tok = Token('float')
    bool_tok = Token('bool')
    str_tok = Token('str')

    list_start = Token('\[')
    list_end = Token('\]')

    tuple_start = Token('\(')
    tuple_div = Token(',')
    tuple_end = Token('\)')

    dict_start = Token('\{')
    dict_div = Token('\:')
    dict_end = Token('\}')

    fn_div = Token('\->')

    typ = Delayed()

    base_typ = int_tok | float_tok | bool_tok | str_tok

    lst = ~list_start & typ & ~list_end

    tup_comp = Delayed()
    tup_comp += tup_div & typ & Optional(tup_comp)
    tup = tup_start & typ & tup_comp & tup_end

    dct = dict_start & typ & dict_div & dict_end

    fun = tup & fn_div & typ

    typ += base_type | lst | tup | dct | fun
    
    @staticmethod
    def parse(s):
        return sexpr_to_tree(TypeSpecParser.typ.parse(s)[0])

class T:
    @staticmethod
    def p(s):
        return TypeSpecParser.parse(s)
    

