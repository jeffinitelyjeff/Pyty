import re
from lepl import (List, Token, Delayed, RuntimeLexerError,
                  FullFirstMatchException, sexpr_to_tree)

from errors import TypeIncorrectlySpecifiedError


class PType:

    # Literals.
    INT = 0
    FLOAT = 1
    STRING = 2
    UNICODE = 3
    BOOL = 4
    UNIT = 5

    # Containers.
    LIST = 6
    SET = 7
    TUPLE = 8
    MAP = 9
    ARROW = 10

    # Polymorphism stuff.
    VAR = 11
    UNIV = 12

    def __init__(self, tag):
        assert type(tag) is int and 0 <= tag <= 12
        self.tag = tag

    ## Type constructor dispatchers.

    @staticmethod
    def from_str(s):
        """Create a PType object from a string."""

        parsed = TypeSpecParser.parse(s)
        return PType.from_type_ast(parsed)

    @staticmethod
    def from_type_ast(ast):
        """Create a PType object from a LEPL-generated type AST."""

        # shorthand.
        from_ast = PType.from_type_ast

        if type(ast) is str:
            if ast == "int":
                return PType.INT_T
            elif ast == "float":
                return PType.FLOAT_T
            elif ast == "str":
                return PType.STR_T
            elif ast == "unicode":
                return PType.UNICODE_T
            elif ast == "bool":
                return PType.BOOL_T
            elif ast == "unit":
                return PType.UNIT_T
            elif ast.index("'") == 0:
                return PType.var(ast)
            else:
                assert True, ast
        elif ast.__class__ == Lst:
            return PType.list(from_ast(ast.elt_t()))
        elif ast.__class__ == Stt:
            return PType.set(from_ast(ast.elt_t()))
        elif ast.__class__ == Tup:
            return PType.tuple([from_ast(t) for t in ast.elt_ts()])
        elif ast.__class__ == Mpp:
            return PType.map(from_ast(ast.key_t()), from_ast(ast.val_t()))
        elif ast.__class__ == Arr:
            return PType.arrow(from_ast(ast.domain_t()),
                               from_ast(ast.range_t()))
        else:
            # Note that there's no UNIV case; shouldn't be user-specifiable.
            assert True, ast.__class__.__name__

    ## Type constructors.

    @staticmethod
    def int():
        if not hasattr(PType, 'INT_T'):
            PType.INT_T = PType(PType.INT)
        return PType.INT_T

    @staticmethod
    def float():
        if not hasattr(PType, 'FLOAT_T'):
            PType.FLOAT_T = PType(PType.FLOAT)
        return PType.FLOAT_T

    @staticmethod
    def string():
        if not hasattr(PType, 'STR_T'):
            PType.STR_T = PType(PType.STRING)
        return PType.STR_T

    @staticmethod
    def unicode():
        if not hasattr(PType, 'UNICODE_T'):
            PType.UNICODE_T = PType(PType.UNICODE)
        return PType.UNICODE_T


    @staticmethod
    def bool():
        if not hasattr(PType, 'BOOL_T'):
            PType.BOOL_T = PType(PType.BOOL)
        return PType.BOOL_T

    @staticmethod
    def unit():
        if not hasattr(PType, 'UNIT_T'):
            PType.UNIT_T = PType(PType.UNIT)
        return PType.UNIT_T

    @staticmethod
    def list(elt):
        t = PType(PType.LIST)
        t.elt = elt
        return t

    @staticmethod
    def set(elt):
        t = PType(PType.SET)
        t.elt = elt
        return t

    @staticmethod
    def tuple(elts):
        t = PType(PType.TUPLE)
        t.elts = elts
        return t

    @staticmethod
    def map(dom, ran):
        t = PType(PType.MAP)
        t.dom = dom
        t.ran = ran
        return t

    @staticmethod
    def arrow(dom, ran):
        t = PType(PType.ARROW)
        t.dom = dom
        t.ran = ran
        return t

    @staticmethod
    def var(idn):
        t = PType(PType.VAR)
        t.idn = idn
        return t

    @staticmethod
    def univ(qnt, ovr):
        t = PType(PType.UNIV)
        t.qnt = qnt
        t.ovr = ovr
        return t

    ## Type tests.
    # Note these are unnecessary for the nullary type constructors becasue those
    # are singletons and can be compared with object equality.

    def is_base(self):
        return self.tag <= PType.UNIT

    def is_list(self):
        return self.tag == PType.LIST

    def is_set(self):
        return self.tag == PType.SET

    def is_tuple(self):
        return self.tag == PType.TUPLE

    def is_map(self):
        return self.tag == PType.MAP

    def is_arrow(self):
        return self.tag == PType.ARROW

    def is_var(self):
        return self.tag == PType.VAR

    def is_univ(self):
        return self.tag == PType.UNIV

    ## Basic methods.

    def __repr__(self):

        if self.tag == PType.INT:
            return "int"
        elif self.tag == PType.FLOAT:
            return "float"
        elif self.tag == PType.STRING:
            return "str"
        elif self.tag == PType.UNICODE:
            return "unicode"
        elif self.tag == PType.BOOL:
            return "bool"
        elif self.tag == PType.UNIT:
            return "unit"

        elif self.is_list():
            return "[" + self.elt.__repr__() + "]"
        elif self.is_set():
            return "{" + self.elt.__repr__() + "}"
        elif self.is_tuple():
            return "(" + ", ".join(elt.__repr__() for elt in self.elts) + ")"
        elif self.is_map():
            return "{" + self.dom.__repr__() + ": " + self.ran.__repr__() + "}"
        elif self.is_arrow():
            return self.dom.__repr__() + " -> " + self.ran.__repr__()

        elif self.is_var():
            return self.idn
        elif self.is_univ():
            return "V" + self.qnt.__repr__() + "." + self.ovr.__repr__()

        else:
            assert True, self.tag

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    def __ne__(self, other):
        return not self.__eq__(other)

    ## Special methods.

    def tuple_slice(self, start=0, end=None, step=1):

        assert self.is_tuple()

        if end is None:
            end = len(self.elts)

        return PType.tuple(self.elts[start:end:step])

    def free_type_vars(self):

        if self.is_base():
            return {}
        elif self.is_list():
            return self.elt.free_type_vars()
        elif self.is_set():
            return self.elt.free_type_vars()
        elif self.is_tuple():
            return set().union(*[elt.free_type_vars() for elt in self.elts])
        elif self.is_map():
            return self.dom.free_type_vars() | self.ran.free_type_vars()
        elif self.is_arrow():
            return self.dom.free_type_vars() | self.ran.free_type_vars()

        elif self.is_var():
            return {self}
        elif self.is_univ():
            return self.ovr.free_type_vars() - {self.qnt}

        else:
            assert True, self.tag

    def quantify(self):

        quant = self

        for v in self.free_type_vars():
            quant = PType.univ(v, quant)

        return quant


def better_sexpr_to_tree(a):
    if type(a) == str:
        return a
    else:
        return sexpr_to_tree(a)

class Lst(List):
    def elt_t(self):
        return self[0]

class Stt(List):
    def elt_t(self):
        return self[0]

class Tup(List):
    def elt_ts(self):
        return [t for t in self]

class Mpp(List):
    def key_t(self):
        return self[0]

    def val_t(self):
        return self[1]

class Arr(List):
    def domain_t(self):
        return self[0]

    def range_t(self):
        return self[1]

class TypeSpecParser:
    int_tok = Token(r'int')
    float_tok = Token(r'float')
    str_tok = Token(r'str')
    unicode_tok = Token(r'unicode')
    bool_tok = Token(r'bool')
    unit_tok = Token(r'unit')
    var_tok = Token(r"'[a-zA-Z0-9]+")

    list_start = Token(r'\[')
    list_end = Token(r'\]')

    set_start = Token(r'\{')
    set_end = Token(r'\}')

    tuple_start = Token(r'\(')
    tuple_div = Token(r',')
    tuple_end = Token(r'\)')

    map_start = Token(r'\{')
    map_div = Token(r':')
    map_end = Token(r'\}')

    arrow_div = Token(r'\->')

    tight_typ = Delayed()
    typ = Delayed()

    num_typ = int_tok | float_tok # | long_tok | complex_tok
    str_typ = str_tok | unicode_tok
    base_typ = num_typ | str_typ | bool_tok | unit_tok | var_tok

    lst = ~list_start & typ & ~list_end > Lst
    stt = ~set_start & typ & ~set_end > Stt

    empty_tup = ~tuple_start & ~tuple_end > Tup
    comma_tup = ~tuple_start & (typ & ~tuple_div)[1:] & ~tuple_end > Tup
    no_comma_tup = ~tuple_start & (typ & ~tuple_div)[1:] & typ & ~tuple_end > Tup
    tup = empty_tup | comma_tup | no_comma_tup

    mpp = ~map_start & typ & ~map_div & typ & ~map_end > Mpp

    arr = tight_typ & ~arrow_div & typ > Arr

    parens = ~tuple_start & typ & ~tuple_end
    tight_typ += base_typ | lst | stt | tup | mpp | parens
    typ += arr | tight_typ

    @staticmethod
    def parse(s):
        try:
            return TypeSpecParser.typ.parse(s)[0]
        except (RuntimeLexerError, FullFirstMatchException):
            raise TypeIncorrectlySpecifiedError(s)


    @staticmethod
    def print_parse(s):
        try:
            return better_sexpr_to_tree(TypeSpecParser.typ.parse(s)[0])
        except (RuntimeLexerError, FullFirstMatchException):
            raise TypeIncorrectlySpecifiedError(s)
