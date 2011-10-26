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
        if typ is None:
            self.t = TypeSpecParser.parse("_")
        elif type(typ) is str:
            self.t = TypeSpecParser.parse(typ)
        else:
            self.t = typ

    def __repr__(self):
        return reverse_parse(self.t)

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    @staticmethod
    def list_of(t):
        """Creates a PType object which represents a list of elements which
        have type C{t}.

        @type t: L{PType}
        """

        return PType(Lst([t.t]))

        # # t is a PType object, but in order to pass it as a child of a Lst
        # # node, we need to get the actual type AST, not the PType wrapper.
        # p = PType()
        # p.t = Lst(t.t)
        # return p

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

        # ts are PType objects, but in order to pass them as members of a Tup
        # List, we need to get the actual type ASTs of each.
        p = PType()
        p.t = Tup([t.t for t in ts])
        return p

    @staticmethod
    def dict_of(t0, t1):
        """Creates a PType object which represents a dictionary mapping
        elements of type C{t0} to elements of type C{t1}.

        @type t0: L{PType}
        @type t1: L{PType}
        """

        # t0 and t1 are PType objects, but in order to pass them as children
        # of a Dct node, we need to get the actual type ASTs of each.
        p = PType()
        p.t = Dct([t0.t, t1.t])
        return p


    def is_bool(self):
        return self.t == "bool"

    def is_int(self):
        return self.t == "int"

    def is_float(self):
        return self.t == "float"

    def is_str(self):
        return self.t == "str"

    def is_gen(self):
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
        assert self.is_list()
        return PType(self.t.elt_t())

    def tuple_ts(self):
        assert self.is_tuple()
        return [PType(x) for x in self.t.elt_ts()]

    def dict_ts(self):
        assert self.is_dict()
        return [PType(self.t.key_t()), PType(self.t.val_t())]

    def function_ts(self):
        assert self.is_function()
        return [PType(self.t.in_t()), PType(self.t.out_t())]

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
gen_t = PType('_')
