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
        self.assertTrue(PytyType("bool").is_bool())
        self.assertTrue(PytyType("int").is_int())
        self.assertTrue(PytyType("float").is_float())
        self.assertTrue(PytyType("str").is_str())
        self.assertTrue(PytyType("_").is_gen())
        self.assertTrue(PytyType().is_gen())

    def test_is_list(self):
        self.assertTrue(PytyType("[int]").is_list())
        self.assertTrue(PytyType("[float]").is_list())
        self.assertTrue(PytyType("[_]").is_list())
        self.assertTrue(PytyType("[{float:str}]").is_list())

    def test_is_tuple(self):
        self.assertTrue(PytyType("(float,bool,int)").is_tuple())
        self.assertTrue(PytyType("(bool,)").is_tuple())
        self.assertTrue(PytyType("(bool,float,_,int,bool)").is_tuple())
        self.assertTrue(PytyType("([int],[bool])").is_tuple())
        self.assertTrue(PytyType("({int:float},{float:int})").is_tuple())

    def test_is_dict(self):
        self.assertTrue(PytyType("{int:float}").is_dict())
        self.assertTrue(PytyType("{_:int}").is_dict())
        self.assertTrue(PytyType("{int:_}").is_dict())
        self.assertTrue(PytyType("{(int,int):float}").is_dict())

class TypeSpecTests(unittest.TestCase):
    def test_base_types(self):
        self.assertEqual(p('int'),   'int')
        self.assertEqual(p('float'), 'float')
        self.assertEqual(p('bool'),  'bool')
        self.assertEqual(p('str'),   'str')

    def test_list(self):
        self.assertEqual(p('[int]'),
                         s(Lst('int')))
        self.assertEqual(p('[ str ]'), p('[str]'))
        self.assertEqual(p('[    float]'), p('[float     ]'))
        self.assertEqual(p('[bool]'),
                         s(Lst('bool')))
        self.assertEqual(p('[[float]]'),
                         s(Lst(Lst('float'))))
        self.assertEqual(p('[[[str]]]'),
                         s(Lst(Lst(Lst('str')))))
        self.assertEqual(p('[(int,{float:str})]'),
                         s(Lst(Tup(['int', Dct('float', 'str')]))))
        self.assertEqual(p('[(int,{float:str})]'),
                         p('[(int, {float: str})]'))

    def test_tuple(self):
        self.assertEqual(p('(int,)'),
                         s(Tup(['int'])))
        self.assertEqual(p('(  int, )'), p('(int,)'))
        self.assertEqual(p('( bool,   str , float  , int )'),
                         p('(bool,str,float,int)'))
        self.assertEqual(p('(bool,str,float,int)'),
                         p('(bool, str, float, int)'))
        self.assertEqual(p('(bool, float)'),
                         s(Tup(['bool', 'float'])))
        self.assertEqual(p('(int, str, float)'),
                         s(Tup(['int', 'str', 'float'])))
        self.assertEqual(p('([int],)'),
                         s(Tup([Lst('int')])))
        self.assertEqual(p('([bool], [str])'),
                         s(Tup([Lst('bool'), Lst('str')])))
        self.assertEqual(p('(int, {float:str})'),
                         s(Tup(['int', Dct('float', 'str')])))

    def test_dict(self):
        self.assertEqual(p('{int: float}'), s(Dct('int', 'float')))
        self.assertEqual(p('{str: int}'), p('{ str : int }'))
        self.assertEqual(p('{str: int}'), p('{str:int}'))
        self.assertEqual(p('{str: [float]}'),
                         s(Dct('str', Lst('float'))))
        self.assertEqual(p('{float: (int, [str], bool)}'),
                         s(Dct('float',
                                  Tup(['int', Lst('str'), 'bool']))))

    def test_func(self):
        self.assertEqual(p('(int,) -> float'),
                         s(Fun(Tup(['int']), 'float')))
        self.assertEqual(p('int ->float '), p('(int) -> float'))
        self.assertEqual(p('() -> int'),
                         s(Fun('unit', 'int')))
        self.assertEqual(p('([float],) -> int'),
                         s(Fun(Tup([Lst('float')]), 'int')))

if __name__ == '__main__':
    unittest.main()
