import re
from lepl import *

from errors import TypeIncorrectlySpecifiedError

def better_sexpr_to_tree(a):
    if type(a) == str:
        return a
    else:
        return sexpr_to_tree(a)

class PytyType: pass

class Lst(Node, PytyType): pass
class Tup(List, PytyType): pass
class Dct(Node, PytyType): pass
class Fun(Node, PytyType): pass

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
        return TypeSpecParser.typ.parse(s)[0]

    @staticmethod
    def print_parse(s):
        try:
            return better_sexpr_to_tree(TypeSpecParser.typ.parse(s)[0])
        except RuntimeLexerError, FullFirstMatchException:
            raise TypeIncorrectlySpecifiedError()



int_t = TypeSpecParser.parse('int')
float_t = TypeSpecParser.parse('float')
bool_t = TypeSpecParser.parse('bool')
str_t = TypeSpecParser.parse('str')
        

