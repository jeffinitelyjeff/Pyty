import re
from lepl import (List, Token, Delayed, RuntimeLexerError,
                  FullFirstMatchException, sexpr_to_tree)

from errors import TypeIncorrectlySpecifiedError


class PType:
    """PType is an outside wrapper for the Type AST returned by the parser
    generator. Methods are provided to access element types, which are only
    wrapped into PTypes once they are accessed.
    """

    def __init__(self, typ):
        """
        Create new `PType` from a specified type.

        Pre-condition: `typ` is a string or PType AST.
        """

        if type(typ) is str:
            self.t = TypeSpecParser.parse(typ)
        elif typ.__class__ in [Lst, Tup, Dct, Fun]:
            self.t = typ
        else:
            assert False, "PType must be constructed with string or PType"

    def __repr__(self):
        return reverse_parse(self.t)

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def list_of(t):
        """Create a PType representing a list of elements of PType `t`."""

        if t is None:
            return None
        else:
            return PType(Lst([t.t]))

    @staticmethod
    def tuple_of(ts):
        """Create a PType representing a tuple of the list of PTypes `ts`."""

        if any(t is None for t in ts):
            return None
        else:
            return PType(Tup([t.t for t in ts]))

    @staticmethod
    def dict_of(t0, t1):
        """Create a PType representing a dictionary mapping PType `t0` to PType
        `t1`."""

        if t0 is None or t1 is None:
            return None
        else:
            return PType(Dct([t0.t, t1.t]))

    def is_list(self):
        """Return if `self` is a `list` PType."""
        return self.t.__class__ == Lst

    def is_tuple(self):
        """Return if `self` is a `tuple` PType."""
        return self.t.__class__ == Tup

    def is_uniform_tuple(self):
        """Return if `self` is a uniform `tuple` PType."""
        return (self.is_tuple() and
                all(t == self.tuple_ts()[0] for t in self.tuple_ts()[1:]))

    def is_dict(self):
        """Return if `self` is a `dict` PType."""
        return self.t.__class__ == Dct

    def is_function(self):
        """Return if `self` is a `function` PType."""
        return self.t.__class__ == Fun

    def list_t(self):
        """
        Get the PType which `self` is a list of.

        Pre-condition: `self.is_list()`
        """

        assert self.is_list()
        return PType(self.t.elt_t())

    def tuple_ts(self):
        """
        Get the PTypes which `self` is a tuple of.

        Pre-condition: `self.is_tuple()`
        """

        assert self.is_tuple()
        return [PType(x) for x in self.t.elt_ts()]

    def tuple_ts_slice(self, start=0, end=None, step=1):
        """
        Get a slice of the PTypes which `self` is a tuple of.

        Pre-condition: `self.is_tuple()`
        """

        assert self.is_tuple()

        if end is None:
            end = len(self.tuple_ts())

        return PType.tuple_of(self.tuple_ts()[start:end:step])

    def key_t(self):
        """
        Get the PType of keys which `self` maps from.

        Pre-condition: `self.is_dict()`
        """

        assert self.is_dict()
        return PType(self.t.key_t())

    def val_t(self):
        """
        Get the PType of values which `self` maps to.

        Pre-condition: `self.is_dict()`
        """

        assert self.is_dict()
        return PType(self.t.val_t())

    def dict_ts(self):
        """
        Get the PTypes which `self` maps.

        Pre-condition: `self.is_dict()`
        """

        return [self.key_t(), self.val_t()]

    def domain_t(self):
        """
        Get the PType which `self` maps from.

        Pre-condition: `self.is_function()`
        """

        assert self.is_function()
        return PType(self.t.domain_t())

    def range_t(self):
        """
        Get the PType which `self` maps to.

        Pre-condition: `self.is_function()`
        """

        assert self.is_function()
        return PType(self.t.range_t())

    def function_ts(self):
        """
        Get the PTypes which `self` maps.

        Pre-condition: `self.is_function()`
        """

        assert self.is_function()
        return [self.domain_t(), self.range_t()]

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
        recurse0 = reverse_parse(type_ast.domain_t())
        recurse1 = reverse_parse(type_ast.range_t())
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
    def domain_t(self):
        return self[0]

    def range_t(self):
        return self[1]

class TypeSpecParser:
    int_tok = Token(r'int')
    float_tok = Token(r'float')
    bool_tok = Token(r'bool')
    str_tok = Token(r'str')
    unicode_tok = Token(r'unicode')
    unit_tok = Token(r'unit')

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

    num_typ = int_tok | float_tok # | long_tok | complex_tok
    str_typ = str_tok | unicode_tok
    base_typ = num_typ | str_typ | bool_tok | unit_tok

    lst = ~list_start & typ & ~list_end > Lst

    tup_component = ~tuple_div & typ
    tup = ~tuple_start & typ & (~tuple_div | tup_component[1:]) & ~tuple_end > Tup

    dct = ~dict_start & typ & ~dict_div & typ & ~dict_end > Dct

    fun = tight_typ & ~fn_div & typ > Fun

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

int_t = PType('int')
float_t = PType('float')
bool_t = PType('bool')
str_t = PType('str')
unicode_t = PType('unicode')
unit_t = PType('unit')
