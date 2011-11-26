import re
from lepl import (List, Token, Delayed, RuntimeLexerError,
                  FullFirstMatchException, sexpr_to_tree)

from errors import TypeIncorrectlySpecifiedError


class PType:
    """PType is an outside wrapper for the Type AST returned by the parser
    generator. Methods are provided to access element types, which are only
    wrapped into PTypes once they are accessed.
    """

    def __init__(self, typ = None):
        assert typ is not None
        if type(typ) is str:
            if typ == "unit":
                self.t = TypeSpecParser.parse("()")
            else:
                self.t = TypeSpecParser.parse(typ)
        else:
            self.t = typ

    def __repr__(self):
        return reverse_parse(self.t)

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def list_of(t):
        """Creates a PType object which represents a list of elements which
        have type C{t}.

        @type t: L{PType}
        """

        return PType(Lst([t.t]))

    @staticmethod
    def any_list():
        """Creates a PType object which represents a list of any type.
        """

        return PType('[_]')

    @staticmethod
    def tuple_of(ts):
        """Creates a PType object which represents a list of elements which
        have types C{ts}.

        @type ts: [L{PType}]
        """

        return PType(Tup([t.t for t in ts]))

    @staticmethod
    def dict_of(t0, t1):
        """Creates a PType object which represents a dictionary mapping
        elements of type C{t0} to elements of type C{t1}.

        @type t0: L{PType}
        @type t1: L{PType}
        """

        return PType(Dct([t0.t, t1.t]))

    def is_bool(self):
        return self.t == "bool"

    def is_int(self):
        return self.t == "int"

    def is_float(self):
        return self.t == "float"

    def is_str(self):
        return self.t == "str"

    def is_unit(self):
        return self.t == "unit"

    def is_list(self):
        return self.t.__class__ == Lst

    def is_tuple(self):
        return self.t.__class__ == Tup

    def is_dict(self):
        return self.t.__class__ == Dct

    def is_function(self):
        return self.t.__class__ == Fun

    def list_t(self):
        assert self.is_list()
        return PType(self.t.elt_t())

    def tuple_ts(self):
        assert self.is_tuple()
        return [PType(x) for x in self.t.elt_ts()]

    def tuple_ts_slice(self, start=0, end=None, step=1):
        assert self.is_tuple()

        if end is None:
            end = len(self.tuple_ts())

        return PType.tuple_of(self.tuple_ts()[start:end:step])

    def dict_ts(self):
        assert self.is_dict()
        return [PType(self.t.key_t()), PType(self.t.val_t())]

    def function_ts(self):
        assert self.is_function()
        return [PType(self.t.in_t()), PType(self.t.out_t())]

    def domain_t(self):
        assert self.is_function()
        return PType(self.t.in_t())

    def range_t(self):
        assert self.is_function()
        return PType(self.t.out_t())

    def is_subtype(self, other_t):
        return other_t.is_gen() or \
               self == other_t or \
               (self.is_int() and other_t.is_float())

def reverse_parse(type_ast):
    if type(type_ast) == str:
        return type_ast
    elif type_ast.__class__ == Lst:
        recurse = reverse_parse(type_ast.elt_t())
        return "[" + recurse + "]"
    elif type_ast.__class__ == Tup:
        recurses = [reverse_parse(t) for t in type_ast.elt_ts()]
        if len(type_ast.elt_ts()) == 1:
            return "(" + recurses[0] + ",)"
        else:
            return "(" + ", ".join([str(x) for x in recurses]) + ")"
    elif type_ast.__class__ == Dct:
        recurse0 = reverse_parse(type_ast.key_t())
        recurse1 = reverse_parse(type_ast.val_t())
        return "{" + recurse0 + " : " + recurse1 + "}"
    elif type_ast.__class__ == Fun:
        recurse0 = reverse_parse(type_ast.in_t())
        recurse1 = reverse_parse(type_ast.out_t())
        return recurse0 + " -> " + recurse1
    else:
        assert False, "Weird type_ast class name: " + str(type_ast.__class__)

def better_sexpr_to_tree(a):
    if type(a) == str:
        return a
    else:
        return sexpr_to_tree(a)

class Lst(List):
    def elt_t(self):
        return self[0]

class Tup(List):
    def elt_ts(self):
        return [t for t in self]

class Dct(List):
    def key_t(self):
        return self[0]

    def val_t(self):
        return self[1]

class Fun(List):
    def in_t(self):
        return self[0]

    def out_t(self):
        return self[1]

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

    unit = tuple_start & tuple_end > make_unit

    base_typ = int_tok | float_tok | bool_tok | str_tok | unit

    lst = ~list_start & typ & ~list_end > Lst

    tup_component = ~tuple_div & typ
    tup = ~tuple_start & typ & (~tuple_div | tup_component[1:]) & ~tuple_end > Tup

    dct = ~dict_start & typ & ~dict_div & typ & ~dict_end > Dct

    fun = (unit | tight_typ) & ~fn_div & (unit | typ) > Fun

    parens = ~tuple_start & typ & ~tuple_end
    tight_typ += base_typ | lst | tup | dct | parens
    typ += fun | tight_typ

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


# NOTE this is a little bit hacky; we're passing the parsed type because we know
# what it should be.
int_t = PType('int')
float_t = PType('float')
bool_t = PType('bool')
str_t = PType('str')
unit_t = PType('()')
