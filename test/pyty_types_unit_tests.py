import unittest
from lepl import *

from pyty_types import *

parse = TypeSpecParser.parse

class TypeSpecTests(unittest.TestCase):
    def test_list_spec(self):
        self.assertEqual(ListSpec('int'), List(['list', 'int']))

    def test_tuple_spec(self):
        self.assertEqual(TupleSpec(['int', 'float']),
                         List(['tuple', 'int', 'float']))

    def test_dict_spec(self):
        self.assertEqual(DictSpec('int', 'float'),
                         List(['dict', 'int', 'float']))

    def test_func_spec(self):
        self.assertEqual(FuncSpec(TupleSpec(['int', 'int']), 'float'),
                         List(['func',
                               List(['tuple', 'int', 'int'])
                               'float']))
        self.assertEqual(FuncSpec(TupleSpec([]), 'str'),
                         List(['func', List([]), 'str']))
                         
    
    def test_base_types(self):
        self.assertEqual(parse('int'),   'int')
        self.assertEqual(parse('float'), 'float')
        self.assertEqual(parse('bool'),  'bool')
        self.assertEqual(parse('str'),   'str')

    def test_list(self):
        self.assertEqual(parse('[int]'),
                         ListSpec('int'))
        self.assertEqual(parse('[ str ]'), parse('[str]'))
        self.assertEqual(parse('[    float]'), parse('[float     ]'))
        self.assertEqual(parse('[bool]'),
                         ListSpec('bool'))
        self.assertEqual(parse('[[float]]'),
                         ListSpec(ListSpec('float')))
        self.assertEqual(parse('[[[str]]]'),
                         ListSpec(ListSpec(ListSpec('str'))))

    def test_tuple(self):
        self.assertEqual(parse('(int)'),
                         TupleSpec(['int'])
        self.assertEqual(parse('(  int )'), parse('(int)'))
        self.assertEqual(parse('( bool,   str , float  , int )'),
                         parse('(bool,str,float,int)'))
        self.assertEqual(parse('(bool,str,float,int)'),
                         parse('(bool, str, float, int)'))
        self.assertEqual(parse('(bool, float)'),
                         TupleSpec(['bool', 'float']))
        self.assertEqual(parse('(int, str, float)'),
                         TupleSpec(['int', 'str', 'float']))
        self.assertEqual(parse('([int])'),
                         TupleSpec([ListSpec('int')]))
        self.assertEqual(parse('([bool], [str])'),
                         TupleSpec([ListSpec('bool'), ListSpec('str')]))

    def test_dict(self):
        self.assertEqual(parse('{int: float}'), DictSpec('int', 'float'))
        self.assertEqual(parse('{str: int}'), parse('{ str : int }'))
        self.assertEqual(parse('{str: int}'), parse('{str:int}'))
        self.assertEqual(parse('{str: [float]}'),
                         DictSpec('str', ListSpec('float')))
        self.assertEqual(parse('{float: (int, [str], bool)}'),
                         DictSpec('float',
                                  TupleSpec(['int', ListSpec('str'), 'bool'])))

    def test_func(self):
        self.assertEqual(parse('(int) -> float'),
                         FuncSpec(TupleSpec(['int']), 'float'))
        self.assertEqual(parse('( int )->float '), parse('(int) -> float'))
        self.assertEqual(parse('() -> int')
                         FuncSpec(TupleSpec([]), 'int'))
        self.assertEqual(parse('([float]) -> int'),
                         FuncSpec(TupleSpec([ListSpec('float')]), 'int'))
                         

if __name__ == '__main__':
    unittest.main
