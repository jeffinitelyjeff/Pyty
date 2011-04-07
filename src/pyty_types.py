import re
from lepl import *

class TypeSpecParser:
    int_tok = Token('int')
    float_tok = Token('float')
    bool_tok = Token('bool')
    str_tok = Token('str')
    
    list_tok = Token('list')
    tuple_tok = Token('tuple')
    dict_tok = Token('dict')
    
    of_tok = ~Token('of')
    cross_tok= ~Token('\*')
    col_tok = ~Token(':')
    arrow_tok = ~Token('\->')
    lpar_tok = ~Token('\(')
    rpar_tok = ~Token('\)')
    
    typ = Delayed()
    
    parens = lpar_tok & typ & rpar_tok
    parens_typ = parens | typ

    base_typ = int_tok | float_tok | bool_tok | str_tok > List

    lst = list_tok & of_tok & typ >> List

    tup_comp = typ & cross_tok & typ[:] >> List
    tup = tuple_tok & of_tok & tup_comp >> List

    dct_comp = typ & col_tok & typ >> List
    dct = dict_tok & of_tok & dct_comp >> List

    fun = typ & arrow_tok & typ >> List

    typ += base_typ | lst | tup | dct | fun | parens_typ

    @staticmethod
    def parse(s):
        return TypeSpecParser.typ.parse(s)

