import unittest
from lepl import *

from pyty_types import *

parse = TypeSpecParser.parse

class TypeSpecTests(unittest.TestCase):
    def test_base_types(self):
        self.assertEqual(parse('int'),   List(['int']))
        self.assertEqual(parse('float'), List(['float']))
        self.assertEqual(parse('bool'),  List(['bool']))
        self.assertEqual(parse('str'),   List(['str']))

    def test_list(self):
        self.assertEqual(parse('list of int'),
                         List(['list', List(['int'])]))
        self.assertEqual(parse('list of bool'),
                         List(['list', List(['bool'])]))
        self.assertEqual(parse('list of list of float'),
                         List(['list', List(['list', List(['float'])])]))
        self.assertEqual(parse('list of list of list of str'),
                         List(['list',
                               List(['list',
                                     List(['list',
                                           List(['str']) ]) ]) ]) )

    def test_tuple(self):
        self.assertEqual(parse('tuple of int'),
                         List(['tuple', List(['int'])]))
        self.assertEqual(parse('tuple of bool * float'),
                         List(['tuple', List(['bool', 'float'])]))
        self.assertEqual(parse('tuple of int * str * float'),
                         List(['tuple', List(['int', 'str', 'float'])]))
        self.assertEqual(parse('tuple of list of int'),
                         List(['tuple', List(['list', List(['int'])])])

if __name__ == '__main__':
    unittest.main
