import re
from lepl import *

from errors import TypeIncorrectlySpecifiedError


class PytyType:
    """PytyType is an outside wrapper for the Type AST returned by the parser
    generator. Methods are provided to access element types, which are only
    wrapped into PytyTypes once they are accessed.
    """
    
    def __init__(self, typ = None):
        if typ is not None:
            self.t = typ
        else:
            self.t = "PytyType"
    
    def __repr__(self):
        return reverse_parse(self.t)

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    def is_bool(self):
        return self.t == "bool"

    def is_int(self):
        return self.t == "int"

    def is_float(self):
        return self.t == "float"

    def is_str(self):
        return self.t == "str"

    def is_gen_type(self):
        return self.t == "_"

    def is_list(self):
        return self.t.__class__ == Lst

    def is_tuple(self):
        return self.t.__class__ == Tup

    def is_dict(self):
        return self.t.__class__ == Dct

    def is_function(self):
        return self.t.__class__ == Fun

    def list_t(self):
        assert(self.is_list())
        return PytyType(self.t.elt_t())

    def tuple_ts(self):
        assert(self.is_tuple())
        return [PytyType(x) for x in self.t.elt_ts()]

    def dict_ts(self):
        assert(self.is_dict())
        return [PytyType(self.t.key_t()), PytyType(self.t.val_t())]

    def function_ts(self):
        assert(self.is_function())
        return [PytyType(self.t.in_t()), PytyType(self.t.out_t())]

    def is_subtype(self, other_t):
        return other_t.is_gen_type() or \
               self == other_t or \
               (self.is_int() and other_t.is_float())

def reverse_parse(type_ast):
    if type(type_ast) == str:
        return type_ast
    elif type_ast.__class__.__name__ == "Lst":
        recurse = reverse_parse(type_ast.elt_t())
        return "[" + recurse + "]"
    elif type_ast.__class__.__name__ == "Tup":
        recurses = [reverse_parse(t) for t in type_ast.elt_ts()]
        if len(type_ast.elt_ts()) == 1:
            return "(" + recurses[0] + ",)"
        else:
            return "(" + ", ".join([str(x) for x in recurses])
    elif type_ast.__class__.__name__ == "Dct":
        recurse0 = reverse_parse(type_ast.key_t())
        recurse1 = reverse_parse(type_ast.val_t())
        return "{" + recurse0 + " : " + recurse1 + "}"
    elif type_ast.__class__.__name__ == "Fun":
        recurse0 = reverse_parse(type_ast.in_t())
        recurse1 = reverse_parse(type_ast.out_t())
        return recurse0 + " -> " + recurse1
    else:
        # This should be a disjoint sum.
        assert(False)
    
def better_sexpr_to_tree(a):
    if type(a) == str:
        return a
    else:
        return sexpr_to_tree(a)

class Lst(Node):
    def elt_t(self):
        return self._Node__children[0]
    
class Tup(List):
    def elt_ts(self):
        return [t for t in self]

class Dct(Node):
    def key_t(self):
        return self._Node__children[0]

    def val_t(self):
        return self._Node__children[1]
    
class Fun(Node):
    def in_t(self):
        return self._Node__children[0]

    def out_t(self):
        return self._Node__children[0]

def make_unit(toks):
    if toks[0] == "(" and toks[1] == ")":
        return "unit" 

class TypeSpecParser:
    int_tok = Token(r'int')
    float_tok = Token(r'float')
    bool_tok = Token(r'bool')
    str_tok = Token(r'str')
    gen_tok = Token(r'_')

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

    base_typ = int_tok | float_tok | bool_tok | str_tok | gen_tok

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
        try:
            parsed_type = TypeSpecParser.typ.parse(s)[0]
            return PytyType(parsed_type)
        except (RuntimeLexerError, FullFirstMatchException):
            raise TypeIncorrectlySpecifiedError()
        

    @staticmethod
    def print_parse(s):
        try:
            return better_sexpr_to_tree(TypeSpecParser.typ.parse(s)[0])
        except (RuntimeLexerError, FullFirstMatchException):
            raise TypeIncorrectlySpecifiedError()
        

# NOTE this is a little bit hacky; we're passing the parsed type because we know
# what it should be.
int_t = PytyType('int')
float_t = PytyType('float')
bool_t = PytyType('bool')
str_t = PytyType('str')
gen_t = PytyType('_')
