import sys
import unittest
from lepl import sexpr_to_tree

# Include src in the Python search path
sys.path.insert(0, '../src')

from ptype import (PType, TypeSpecParser, better_sexpr_to_tree, Lst, Stt, Tup,
                   Mpp, Arr)

int_t = PType.int()
float_t = PType.float()
str_t = PType.string()
unicode_t = PType.unicode()
bool_t = PType.bool()
unit_t = PType.unit()

base_ts = {"int": int_t, "float": float_t, "str": str_t, "unicode": unicode_t,
           "bool": bool_t, "unit": unit_t}

class PTypeTests(unittest.TestCase):

    def test_is_basetype(self):
        true = self.assertTrue
        true( int_t.is_base() )
        true( float_t.is_base() )
        true( str_t.is_base() )
        true( unicode_t.is_base() )
        true( bool_t.is_base() )
        true( unit_t.is_base() )

        equal = self.assertEqual
        equal( PType.int(), int_t )
        equal( PType.float(), float_t )
        equal( PType.string(), str_t )
        equal( PType.unicode(), unicode_t )
        equal( PType.bool(), bool_t )
        equal( PType.unit(), unit_t )
        all(equal(PType.from_str(k), v) for (k,v) in base_ts.iteritems())

    def test_is_list(self):
        true = self.assertTrue
        true( PType.from_str("[int]").is_list() )
        true( PType.from_str("[float]").is_list() )
        true( PType.from_str("[{float:str}]").is_list() )

    def test_is_set(self):
        true = self.assertTrue
        true( PType.from_str("{bool}").is_set() )
        true( PType.from_str("{unit}").is_set() )
        true( PType.from_str("{(int, bool, float)}").is_set() )
        true( PType.from_str("{ int -> bool }").is_set() )
        true( PType.from_str("{{str: bool}}").is_set() )

    def test_is_tuple(self):
        true = self.assertTrue
        true( PType.from_str("(float,bool,int)").is_tuple() )
        true( PType.from_str("(bool,)").is_tuple() )
        true( PType.from_str("(bool,float,int,bool)").is_tuple() )
        true( PType.from_str("([int],[bool])").is_tuple() )
        true( PType.from_str("({int:float},{float:int})").is_tuple() )

    def test_is_map(self):
        true = self.assertTrue
        true( PType.from_str("{int:float}").is_map() )
        true( PType.from_str("{float -> str:int}").is_map() )
        true( PType.from_str("{int:unicode}").is_map() )
        true( PType.from_str("{(int,int):float}").is_map() )

    def test_is_arrow(self):
        true = self.assertTrue
        true( PType.from_str("int -> float").is_arrow() )
        true( PType.from_str("unicode -> {int:float}").is_arrow() )
        true( PType.from_str("unicode -> str -> int").is_arrow() )
        true( PType.from_str("(unicode -> str) -> int").is_arrow() )

    def test_is_var(self):
        true = self.assertTrue
        true( PType.from_str("'a").is_var() )
        true( PType.from_str("'alpha").is_var() )
        true( PType.from_str("'Yothere").is_var() )
        true( PType.from_str("'hiB9").is_var() )

    def test_free_vars(self):
        equal = self.assertEqual

        alpha = PType.from_str("'a")
        beta = PType.from_str("'b")
        gamma = PType.from_str("'g")

        equal( PType.from_str("'a").free_type_vars(), {alpha} )
        equal( PType.from_str("'a -> 'a").free_type_vars(), {alpha} )
        equal( PType.from_str("'a -> 'b").free_type_vars(), {alpha, beta} )
        equal( PType.from_str("{'g : ('a, int)}").free_type_vars(), {alpha, gamma} )

class TypeSpecTests(unittest.TestCase):

    def spec_has_repr(self, spec, repr):
        """
        Asserts that `spec`, a string representing a PType, has the structure
        specified by `repr`.
        """

        self.assertEqual(TypeSpecParser.print_parse(spec),
                         better_sexpr_to_tree(repr))


    def test_parse_tree(self):

        # FIXME this should probably be more comprehensive; these current tests
        # are desigend to catch a specific error.
        s = better_sexpr_to_tree

        for t0 in base_ts.keys():

            self.assertEqual( s(Lst([t0])), "Lst\n `- '%s'" % t0 )
            self.assertEqual( s(Tup([t0])), "Tup\n `- '%s'" % t0 )

            for t1 in base_ts:

                self.assertEqual( s(Tup([t0,t1])),
                                  "Tup\n +- '%s'\n `- '%s'" % (t0, t1) )
                self.assertEqual( s(Lst([Tup([t0,t1])])),
                                  "Lst\n `- Tup\n     +- '%s'\n     `- '%s'" %
                                  (t0, t1) )


    def test_base_types(self):
        for base_t in base_ts.keys():
            self.spec_has_repr(base_t, base_t)

    def test_list(self):

        for t in base_ts.keys():
            self.spec_has_repr("[%s]" % t, Lst([t]))
            self.spec_has_repr("[   %s]" % t, Lst([t]))
            self.spec_has_repr("[ %s  ]" % t, Lst([t]))
            self.spec_has_repr("[%s   ]" % t, Lst([t]))

    def test_tuple(self):

        for t0 in base_ts.keys():

            self.spec_has_repr("(%s,)" % t0, Tup([t0]))
            self.spec_has_repr("(%s,   )" % t0, Tup([t0]))
            self.spec_has_repr("(%s   ,)" % t0, Tup([t0]))
            self.spec_has_repr("(  %s, )" % t0, Tup([t0]))
            self.spec_has_repr("(  %s ,)" % t0, Tup([t0]))
            self.spec_has_repr("(   %s,)" % t0, Tup([t0]))

            for t1 in base_ts.keys():

                self.spec_has_repr("(%s, %s)" % (t0, t1), Tup([t0, t1]))
                self.spec_has_repr("(%s,   %s)" % (t0, t1), Tup([t0, t1]))
                self.spec_has_repr("(%s  , %s)" % (t0, t1), Tup([t0, t1]))
                self.spec_has_repr("(%s   ,%s)" % (t0, t1), Tup([t0, t1]))
                self.spec_has_repr("(%s, %s,)" % (t0, t1), Tup([t0, t1]))

                for t2 in base_ts.keys():

                    self.spec_has_repr("(%s, %s, %s)" % (t0, t1, t2),
                                       Tup([t0, t1, t2]))
                    self.spec_has_repr("(%s, %s, %s,)" % (t0, t1, t2),
                                       Tup([t0, t1, t2]))

                    for t3 in base_ts.keys():

                        self.spec_has_repr("(%s, %s, %s, %s)" % (t0, t1, t2, t3),
                                           Tup([t0, t1, t2, t3]))
                        self.spec_has_repr("(%s, %s, %s, %s,)" % (t0, t1, t2, t3),
                                           Tup([t0, t1, t2, t3]))

    def test_map(self):

        for t0 in base_ts.keys():

            for t1 in base_ts.keys():

                self.spec_has_repr("{%s: %s}" % (t0, t1), Mpp([t0, t1]))
                self.spec_has_repr("{%s :%s}" % (t0, t1), Mpp([t0, t1]))
                self.spec_has_repr("{%s : %s}" % (t0, t1), Mpp([t0, t1]))
                self.spec_has_repr("{  %s:%s}" % (t0, t1), Mpp([t0, t1]))
                self.spec_has_repr("{ %s:%s  }" % (t0, t1), Mpp([t0, t1]))
                self.spec_has_repr("{  %s :%s}" % (t0, t1), Mpp([t0, t1]))

    def test_arr(self):

        for t0 in base_ts.keys():
            for t1 in base_ts.keys():

                self.spec_has_repr("%s->%s" % (t0, t1), Arr([t0, t1]))
                self.spec_has_repr("%s-> %s" % (t0, t1), Arr([t0, t1]))
                self.spec_has_repr("%s -> %s" % (t0, t1), Arr([t0, t1]))
                self.spec_has_repr(" %s   ->  %s" % (t0, t1), Arr([t0, t1]))

    def test_nesting(self):

        rep = self.spec_has_repr

        for t0 in base_ts.keys():

            rep("[(%s,)]" % t0, Lst([Tup([t0])]))
            rep("([%s],)" % t0, Tup([Lst([t0])]))

            for t1 in base_ts.keys():

                rep("[(%s, %s)]" % (t0, t1), Lst([Tup([t0, t1])]))
                rep("[{%s: %s}]" % (t0, t1), Lst([Mpp([t0, t1])]))
                rep("[%s -> %s]" % (t0, t1), Lst([Arr([t0, t1])]))
                rep("([%s], [%s])" % (t0, t1), Tup([Lst([t0]), Lst([t1])]))
                rep("((%s,), (%s,))" % (t0, t1), Tup([Tup([t0]), Tup([t1])]))
                rep("{[%s]: [%s]}" % (t0, t1), Mpp([Lst([t0]), Lst([t1])]))
                rep("{(%s,): (%s,)}" % (t0, t1), Mpp([Tup([t0]), Tup([t1])]))
                rep("[%s] -> [%s]" % (t0, t1), Arr([Lst([t0]), Lst([t1])]))
                rep("(%s,) -> (%s,)" % (t0, t1), Arr([Tup([t0]), Tup([t1])]))

                # These take forever to run, and are probably redundant.
                # for t2 in base_ts.keys():

                #     rep("[(%s, %s, %s)]" % (t0, t1, t2),
                #         Lst([Tup([t0, t1, t2])]))
                #     rep("([%s], [%s], [%s])" % (t0, t1, t2),
                #         Tup([Lst([t0]), Lst([t1]), Lst([t2])]))
                #     rep("((%s,), (%s,), (%s,))" % (t0, t1, t2),
                #         Tup([Tup([t0]), Tup([t1]), Tup([t2])]))

                #     rep("([(%s, %s)], %s)" % (t0, t1, t2),
                #         Tup([Lst([Tup([t0, t1])]), t2]))
                #     rep("([{%s: %s}], %s)" % (t0, t1, t2),
                #         Tup([Lst([Mpp([t0, t1])]), t2]))
                #     rep("([%s -> %s], %s)" % (t0, t1, t2),
                #         Tup([Lst([Arr([t0, t1])]), t2]))
                #     rep("(([%s], [%s]), %s)" % (t0, t1, t2),
                #         Tup([Tup([Lst([t0]), Lst([t1])]), t2]))
                #     rep("(((%s,), (%s,)), %s)" % (t0, t1, t2),
                #         Tup([Tup([Tup([t0]), Tup([t1])]), t2]))
                #     rep("({[%s]: [%s]}, %s)" % (t0, t1, t2),
                #         Tup([Mpp([Lst([t0]), Lst([t1])]), t2]))
                #     rep("({(%s,): (%s,)}, %s)" % (t0, t1, t2),
                #         Tup([Mpp([Tup([t0]), Tup([t1])]), t2]))
                #     rep("([%s] -> [%s], %s)" % (t0, t1, t2),
                #         Tup([Arr([Lst([t0]), Lst([t1])]), t2]))
                #     rep("((%s,) -> (%s,), %s)" % (t0, t1, t2),
                #         Tup([Arr([Tup([t0]), Tup([t1])]), t2]))

                #     # FIXME Should rethink this; dict keys can't be arbitrary
                #     # expressions
                #     rep("{[(%s, %s)]: %s}" % (t0, t1, t2),
                #         Mpp([Lst([Tup([t0, t1])]), t2]))
                #     rep("{[{%s: %s}]: %s}" % (t0, t1, t2),
                #         Mpp([Lst([Mpp([t0, t1])]), t2]))
                #     rep("{[%s -> %s]: %s}" % (t0, t1, t2),
                #         Mpp([Lst([Arr([t0, t1])]), t2]))
                #     rep("{([%s], [%s]): %s}" % (t0, t1, t2),
                #         Mpp([Tup([Lst([t0]), Lst([t1])]), t2]))
                #     rep("{((%s,), (%s,)): %s}" % (t0, t1, t2),
                #         Mpp([Tup([Tup([t0]), Tup([t1])]), t2]))
                #     rep("{{[%s]: [%s]}: %s}" % (t0, t1, t2),
                #         Mpp([Mpp([Lst([t0]), Lst([t1])]), t2]))
                #     rep("{{(%s,): (%s,)}: %s}" % (t0, t1, t2),
                #         Mpp([Mpp([Tup([t0]), Tup([t1])]), t2]))
                #     rep("{[%s] -> [%s]: %s}" % (t0, t1, t2),
                #         Mpp([Arr([Lst([t0]), Lst([t1])]), t2]))
                #     rep("{(%s,) -> (%s,): %s}" % (t0, t1, t2),
                #         Mpp([Arr([Tup([t0]), Tup([t1])]), t2]))

                #     rep("[(%s, %s)] -> %s" % (t0, t1, t2),
                #         Arr([Lst([Tup([t0, t1])]), t2]))
                #     rep("[{%s: %s}] -> %s" % (t0, t1, t2),
                #         Arr([Lst([Mpp([t0, t1])]), t2]))
                #     rep("[%s -> %s] -> %s" % (t0, t1, t2),
                #         Arr([Lst([Arr([t0, t1])]), t2]))
                #     rep("([%s], [%s]) -> %s" % (t0, t1, t2),
                #         Arr([Tup([Lst([t0]), Lst([t1])]), t2]))
                #     rep("((%s,), (%s,)) -> %s" % (t0, t1, t2),
                #         Arr([Tup([Tup([t0]), Tup([t1])]), t2]))
                #     rep("{[%s]: [%s]} -> %s" % (t0, t1, t2),
                #         Arr([Mpp([Lst([t0]), Lst([t1])]), t2]))
                #     rep("{(%s,): (%s,)} -> %s" % (t0, t1, t2),
                #         Arr([Mpp([Tup([t0]), Tup([t1])]), t2]))
                #     rep("([%s] -> [%s]) -> %s" % (t0, t1, t2),
                #         Arr([Arr([Lst([t0]), Lst([t1])]), t2]))
                #     rep("((%s,) -> (%s,)) -> %s" % (t0, t1, t2),
                #         Arr([Arr([Tup([t0]), Tup([t1])]), t2]))

                #     # rep("[%s] -> ([%s] -> %s)" % (t0, t1, t2),
                #     #     Arr(Arr(Lst(t0), Lst(t1)), t2))
                #     # rep("(%s,) -> ((%s,) -> %s)" % (t0, t1, t2),
                #     #     Arr(Arr(Tup([t0]), Tup([t1])), t2))


if __name__ == '__main__':
    unittest.main()
