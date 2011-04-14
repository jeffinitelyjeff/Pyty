import re
from lepl import *

"""
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

"""

def better_sexpr_to_tree(a):
    if type(a) == str:
        return a
    else:
        return sexpr_to_tree(a)
    

class Lst(Node): pass
class Tup(List): pass
class Dct(Node): pass
class Fun(Node): pass

def make_unit(toks):
    if toks[0] == "(" and toks[1] == ")":
        return "unit" 

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

    tight_typ = Delayed()
    typ = Delayed()

    base_typ = int_tok | float_tok | bool_tok | str_tok

    lst = ~list_start & typ & ~list_end > Lst

    tup_component = ~tuple_div & typ
    tup = ~tuple_start & typ & (~tuple_div | tup_component[1:]) & ~tuple_end > Tup

    dct = ~dict_start & typ & ~dict_div & typ & ~dict_end > Dct

    unit = tuple_start & tuple_end > make_unit
    fun = (unit | tight_typ) & ~fn_div & typ > Fun

    parens = ~tuple_start & typ & ~tuple_end
    tight_typ += base_typ | lst | tup | dct | parens
    typ += fun | tight_typ
    
    @staticmethod
    def parse(s):
        return better_sexpr_to_tree(TypeSpecParser.typ.parse(s)[0])

def p(s):
    return TypeSpecParser.parse(s)
