import sys
import unittest
from lepl import *

# Include src in the Python search path
sys.path.insert(0, '../src')

from parse_type import *

p = TypeSpecParser.print_parse
s = better_sexpr_to_tree

class PytyTypeTests(unittest.TestCase):
    def test_is_basetype(self):
        true = self.assertTrue

        true( PytyType("bool").is_bool() )
        true( PytyType("int").is_int() )
        true( PytyType("float").is_float() )
        true( PytyType("str").is_str() )
        true( PytyType("_").is_gen() )
        true( PytyType().is_gen() )

    def test_is_list(self):
        true = self.assertTrue

        true( PytyType("[int]").is_list() )
        true( PytyType("[float]").is_list() )
        true( PytyType("[_]").is_list() )
        true( PytyType("[{float:str}]").is_list() )

    def test_is_tuple(self):
        true = self.assertTrue

        true( PytyType("(float,bool,int)").is_tuple() )
        true( PytyType("(bool,)").is_tuple() )
        true( PytyType("(bool,float,_,int,bool)").is_tuple() )
        true( PytyType("([int],[bool])").is_tuple() )
        true( PytyType("({int:float},{float:int})").is_tuple() )

    def test_is_dict(self):
        true = self.assertTrue

        true( PytyType("{int:float}").is_dict() )
        true( PytyType("{_:int}").is_dict() )
        true( PytyType("{int:_}").is_dict() )
        true( PytyType("{(int,int):float}").is_dict() )

class TypeSpecTests(unittest.TestCase):
    def test_base_types(self):
        eq = self.assertEqual

        eq( p('int'), 'int' )
        eq( p('float'), 'float' )
        eq( p('bool'), 'bool' )
        eq( p('str'), 'str' )

    def test_list(self):
        eq = self.assertEqual

        eq( p('[int]'),
            s(Lst('int')) )

        eq( p('[ str ]'),
            p('[str]') )

        eq( p('[    float]'),
            p('[float     ]') )

        eq( p('[bool]'),
            s(Lst('bool')) )

        eq( p('[[float]]'),
            s(Lst(Lst('float'))) )

        eq( p('[[[str]]]'),
            s(Lst(Lst(Lst('str')))) )


        # self.assertEqual(p('[(int,{float: str})]'),
        #                  s(Lst(Tup(['int', Dct('float', 'str')]))))
        # self.assertEqual(p('[(int,{float:str})]'),
        #                  p('[(int, {float: str})]'))

    def test_tuple(self):
        eq = self.assertEqual

        eq( p('(int,)'),
            s(Tup(['int'])) )

        eq( p('(  int, )'),
            p('(int,)') )

        eq( p('( bool,   str , float  , int )'),
            p('(bool,str,float,int)') )

        eq( p('(bool,str,float,int)'),
            p('(bool, str, float, int)') )

        eq( p('(bool, float)'),
            s(Tup(['bool', 'float'])) )

        eq( p('(int, str, float)'),
            s(Tup(['int', 'str', 'float'])) )

        eq( p('([int],)'),
            s(Tup([Lst('int')])) )

        eq( p('([bool], [str])'),
            s(Tup([Lst('bool'), Lst('str')])) )

        eq( p('(int, {float:str})'),
            s(Tup(['int', Dct('float', 'str')])) )

    def test_dict(self):
        eq = self.assertEqual

        eq( p('{int: float}'),
            s(Dct('int', 'float')) )

        eq( p('{str: int}'),
            p('{ str : int }') )

        eq( p('{str: int}'),
            p('{str:int}') )

        eq( p('{str: [float]}'),
            s(Dct('str', Lst('float'))) )

        eq( p('{float: (int, [str], bool)}'),
            s(Dct('float', Tup(['int', Lst('str'), 'bool']))) )

    def test_func(self):
        eq = self.assertEqual

        eq( p('(int,) -> float'),
            s(Fun(Tup(['int']), 'float')) )

        eq( p('int ->float '),
            p('(int) -> float') )

        eq( p('() -> int'),
            s(Fun('unit', 'int')) )

        eq( p('([float],) -> int'),
            s(Fun(Tup([Lst('float')]), 'int')) )

if __name__ == '__main__':
    unittest.main()
