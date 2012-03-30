import sys
import unittest
from lepl import sexpr_to_tree

# Include src in the Python search path
sys.path.insert(0, '../src')

from ptype import (PType, TypeSpecParser, better_sexpr_to_tree, Lst, Stt, Tup,
                   Mpp, Arr)

int_t = PType.int()
flt_t = PType.float()
str_t = PType.string()
unicode_t = PType.unicode()
bool_t = PType.bool()
unit_t = PType.unit()
base_ts = {int_t, flt_t, str_t, unicode_t, bool_t, unit_t}

class PTypeTests(unittest.TestCase):

    def test_is_basetype(self):
        true = self.assertTrue
        true( int_t.is_base() )
        true( flt_t.is_base() )
        true( str_t.is_base() )
        true( unicode_t.is_base() )
        true( bool_t.is_base() )
        true( unit_t.is_base() )

        equal = equal
        equal( PType.int(), int_t )
        equal( PType.float(), flt_t )
        equal( PType.string(), str_t )
        equal( PType.unicode(), unicode_t )
        equal( PType.bool(), bool_t )
        equal( PType.unit(), unit_t )

    def test_is_list(self):
        true = self.assertTrue

        true( PType("[int]").is_list() )
        true( PType("[float]").is_list() )
        true( PType("[_]").is_list() )
        true( PType("[{float:str}]").is_list() )

    def test_is_tuple(self):
        true = self.assertTrue

        true( PType("(float,bool,int)").is_tuple() )
        true( PType("(bool,)").is_tuple() )
        true( PType("(bool,float,_,int,bool)").is_tuple() )
        true( PType("([int],[bool])").is_tuple() )
        true( PType("({int:float},{float:int})").is_tuple() )

    def test_is_dict(self):
        true = self.assertTrue

        true( PType("{int:float}").is_dict() )
        true( PType("{_:int}").is_dict() )
        true( PType("{int:_}").is_dict() )
        true( PType("{(int,int):float}").is_dict() )

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

        for t0 in base_ts:

            self.assertEqual( s(Lst([t0])), "Lst\n `- '%s'" % t0 )
            self.assertEqual( s(Tup([t0])), "Tup\n `- '%s'" % t0 )

            for t1 in base_ts:

                self.assertEqual( s(Tup([t0,t1])),
                                  "Tup\n +- '%s'\n `- '%s'" % (t0, t1) )
                self.assertEqual( s(Lst([Tup([t0,t1])])),
                                  "Lst\n `- Tup\n     +- '%s'\n     `- '%s'" %
                                  (t0, t1) )


    def test_base_types(self):
        for base_t in base_ts:
            self.spec_has_repr(base_t, base_t)

    def test_list(self):

        for t in base_ts:
            self.spec_has_repr("[%s]" % t, Lst([t]))
            self.spec_has_repr("[   %s]" % t, Lst([t]))
            self.spec_has_repr("[ %s  ]" % t, Lst([t]))
            self.spec_has_repr("[%s   ]" % t, Lst([t]))

    def test_tuple(self):

        for t0 in base_ts:

            self.spec_has_repr("(%s,)" % t0, Tup([t0]))
            self.spec_has_repr("(%s,   )" % t0, Tup([t0]))
            self.spec_has_repr("(%s   ,)" % t0, Tup([t0]))
            self.spec_has_repr("(  %s, )" % t0, Tup([t0]))
            self.spec_has_repr("(  %s ,)" % t0, Tup([t0]))
            self.spec_has_repr("(   %s,)" % t0, Tup([t0]))

            for t1 in base_ts:

                self.spec_has_repr("(%s, %s)" % (t0, t1), Tup([t0, t1]))
                self.spec_has_repr("(%s,   %s)" % (t0, t1), Tup([t0, t1]))
                self.spec_has_repr("(%s  , %s)" % (t0, t1), Tup([t0, t1]))
                self.spec_has_repr("(%s   ,%s)" % (t0, t1), Tup([t0, t1]))
                self.spec_has_repr("(%s, %s,)" % (t0, t1), Tup([t0, t1]))

                for t2 in base_ts:

                    self.spec_has_repr("(%s, %s, %s)" % (t0, t1, t2),
                                       Tup([t0, t1, t2]))
                    self.spec_has_repr("(%s, %s, %s,)" % (t0, t1, t2),
                                       Tup([t0, t1, t2]))

                    for t3 in base_ts:

                        self.spec_has_repr("(%s, %s, %s, %s)" % (t0, t1, t2, t3),
                                           Tup([t0, t1, t2, t3]))
                        self.spec_has_repr("(%s, %s, %s, %s,)" % (t0, t1, t2, t3),
                                           Tup([t0, t1, t2, t3]))

    def test_dict(self):

        for t0 in base_ts:

            for t1 in base_ts:

                self.spec_has_repr("{%s: %s}" % (t0, t1), Dct([t0, t1]))
                self.spec_has_repr("{%s :%s}" % (t0, t1), Dct([t0, t1]))
                self.spec_has_repr("{%s : %s}" % (t0, t1), Dct([t0, t1]))
                self.spec_has_repr("{  %s:%s}" % (t0, t1), Dct([t0, t1]))
                self.spec_has_repr("{ %s:%s  }" % (t0, t1), Dct([t0, t1]))
                self.spec_has_repr("{  %s :%s}" % (t0, t1), Dct([t0, t1]))

    def test_func(self):

        for t0 in base_ts:

            self.spec_has_repr("()->%s" % t0, Fun(['unit', t0]))
            self.spec_has_repr("()-> %s" % t0, Fun(['unit', t0]))
            self.spec_has_repr("() -> %s" % t0, Fun(['unit', t0]))
            # FIXME
            # self.spec_has_repr("%s->()" % t0, Fun([t0, 'unit']))
            # self.spec_has_repr("%s-> ()" % t0, Fun([t0, 'unit']))
            # self.spec_has_repr("%s -> ()" % t0, Fun([t0, 'unit']))

            for t1 in base_ts:

                self.spec_has_repr("%s->%s" % (t0, t1), Fun([t0, t1]))
                self.spec_has_repr("%s-> %s" % (t0, t1), Fun([t0, t1]))
                self.spec_has_repr("%s -> %s" % (t0, t1), Fun([t0, t1]))
                self.spec_has_repr(" %s   ->  %s" % (t0, t1), Fun([t0, t1]))

    def test_nesting(self):

        for t0 in base_ts:

            self.spec_has_repr("[(%s,)]" % t0, Lst([Tup([t0])]))
            self.spec_has_repr("([%s],)" % t0, Tup([Lst([t0])]))

            for t1 in base_ts:

                self.spec_has_repr("[(%s, %s)]" % (t0, t1),
                                   Lst([Tup([t0, t1])]))
                self.spec_has_repr("[{%s: %s}]" % (t0, t1),
                                   Lst([Dct([t0, t1])]))
                self.spec_has_repr("[%s -> %s]" % (t0, t1),
                                   Lst([Fun([t0, t1])]))
                self.spec_has_repr("([%s], [%s])" % (t0, t1),
                                   Tup([Lst([t0]), Lst([t1])]))
                self.spec_has_repr("((%s,), (%s,))" % (t0, t1),
                                   Tup([Tup([t0]), Tup([t1])]))
                self.spec_has_repr("{[%s]: [%s]}" % (t0, t1),
                                   Dct([Lst([t0]), Lst([t1])]))
                self.spec_has_repr("{(%s,): (%s,)}" % (t0, t1),
                                   Dct([Tup([t0]), Tup([t1])]))
                self.spec_has_repr("[%s] -> [%s]" % (t0, t1),
                                   Fun([Lst([t0]), Lst([t1])]))
                self.spec_has_repr("(%s,) -> (%s,)" % (t0, t1),
                                   Fun([Tup([t0]), Tup([t1])]))

                for t2 in base_ts:

                    self.spec_has_repr("[(%s, %s, %s)]" % (t0, t1, t2),
                                       Lst([Tup([t0, t1, t2])]))
                    self.spec_has_repr("([%s], [%s], [%s])" % (t0, t1, t2),
                                       Tup([Lst([t0]), Lst([t1]), Lst([t2])]))
                    self.spec_has_repr("((%s,), (%s,), (%s,))" % (t0, t1, t2),
                                       Tup([Tup([t0]), Tup([t1]), Tup([t2])]))

                    self.spec_has_repr("([(%s, %s)], %s)" % (t0, t1, t2),
                                       Tup([Lst([Tup([t0, t1])]), t2]))
                    self.spec_has_repr("([{%s: %s}], %s)" % (t0, t1, t2),
                                       Tup([Lst([Dct([t0, t1])]), t2]))
                    self.spec_has_repr("([%s -> %s], %s)" % (t0, t1, t2),
                                       Tup([Lst([Fun([t0, t1])]), t2]))
                    self.spec_has_repr("(([%s], [%s]), %s)" % (t0, t1, t2),
                                       Tup([Tup([Lst([t0]), Lst([t1])]), t2]))
                    self.spec_has_repr("(((%s,), (%s,)), %s)" % (t0, t1, t2),
                                       Tup([Tup([Tup([t0]), Tup([t1])]), t2]))
                    self.spec_has_repr("({[%s]: [%s]}, %s)" % (t0, t1, t2),
                                       Tup([Dct([Lst([t0]), Lst([t1])]), t2]))
                    self.spec_has_repr("({(%s,): (%s,)}, %s)" % (t0, t1, t2),
                                       Tup([Dct([Tup([t0]), Tup([t1])]), t2]))
                    self.spec_has_repr("([%s] -> [%s], %s)" % (t0, t1, t2),
                                       Tup([Fun([Lst([t0]), Lst([t1])]), t2]))
                    self.spec_has_repr("((%s,) -> (%s,), %s)" % (t0, t1, t2),
                                       Tup([Fun([Tup([t0]), Tup([t1])]), t2]))

                    # FIXME Should rethink this; dict keys can't be arbitrary
                    # expressions
                    self.spec_has_repr("{[(%s, %s)]: %s}" % (t0, t1, t2),
                                       Dct([Lst([Tup([t0, t1])]), t2]))
                    self.spec_has_repr("{[{%s: %s}]: %s}" % (t0, t1, t2),
                                       Dct([Lst([Dct([t0, t1])]), t2]))
                    self.spec_has_repr("{[%s -> %s]: %s}" % (t0, t1, t2),
                                       Dct([Lst([Fun([t0, t1])]), t2]))
                    self.spec_has_repr("{([%s], [%s]): %s}" % (t0, t1, t2),
                                       Dct([Tup([Lst([t0]), Lst([t1])]), t2]))
                    self.spec_has_repr("{((%s,), (%s,)): %s}" % (t0, t1, t2),
                                       Dct([Tup([Tup([t0]), Tup([t1])]), t2]))
                    self.spec_has_repr("{{[%s]: [%s]}: %s}" % (t0, t1, t2),
                                       Dct([Dct([Lst([t0]), Lst([t1])]), t2]))
                    self.spec_has_repr("{{(%s,): (%s,)}: %s}" % (t0, t1, t2),
                                       Dct([Dct([Tup([t0]), Tup([t1])]), t2]))
                    self.spec_has_repr("{[%s] -> [%s]: %s}" % (t0, t1, t2),
                                       Dct([Fun([Lst([t0]), Lst([t1])]), t2]))
                    self.spec_has_repr("{(%s,) -> (%s,): %s}" % (t0, t1, t2),
                                       Dct([Fun([Tup([t0]), Tup([t1])]), t2]))

                    self.spec_has_repr("[(%s, %s)] -> %s" % (t0, t1, t2),
                                       Fun([Lst([Tup([t0, t1])]), t2]))
                    self.spec_has_repr("[{%s: %s}] -> %s" % (t0, t1, t2),
                                       Fun([Lst([Dct([t0, t1])]), t2]))
                    self.spec_has_repr("[%s -> %s] -> %s" % (t0, t1, t2),
                                       Fun([Lst([Fun([t0, t1])]), t2]))
                    self.spec_has_repr("([%s], [%s]) -> %s" % (t0, t1, t2),
                                       Fun([Tup([Lst([t0]), Lst([t1])]), t2]))
                    self.spec_has_repr("((%s,), (%s,)) -> %s" % (t0, t1, t2),
                                       Fun([Tup([Tup([t0]), Tup([t1])]), t2]))
                    self.spec_has_repr("{[%s]: [%s]} -> %s" % (t0, t1, t2),
                                       Fun([Dct([Lst([t0]), Lst([t1])]), t2]))
                    self.spec_has_repr("{(%s,): (%s,)} -> %s" % (t0, t1, t2),
                                       Fun([Dct([Tup([t0]), Tup([t1])]), t2]))
                    self.spec_has_repr("([%s] -> [%s]) -> %s" % (t0, t1, t2),
                                       Fun([Fun([Lst([t0]), Lst([t1])]), t2]))
                    self.spec_has_repr("((%s,) -> (%s,)) -> %s" % (t0, t1, t2),
                                       Fun([Fun([Tup([t0]), Tup([t1])]), t2]))

                    # self.spec_has_repr("[%s] -> ([%s] -> %s)" % (t0, t1, t2),
                    #                    Fun(Fun(Lst(t0), Lst(t1)), t2))
                    # self.spec_has_repr("(%s,) -> ((%s,) -> %s)" % (t0, t1, t2),
                    #                    Fun(Fun(Tup([t0]), Tup([t1])), t2))


if __name__ == '__main__':
    unittest.main()
