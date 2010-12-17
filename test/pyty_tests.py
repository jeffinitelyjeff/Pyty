import unittest
import ast
import sys

# Include src in the Python search path.
sys.path.insert(0, '../src')

from typecheck import typecheck, parse_type_declarations, debug
from pyty_types import PytyMod
from pyty_errors import TypeUnspecifiedError, TypeIncorrectlySpecifiedError

"""
This is just the core of the unit testing file. generate_tests.py must be run
to fill this file with the several unit tests (each of which tests one source
code file in the test_files directory).

Test file format:

### True|False|ErrorName

<Python code>
"""

class TestFileFormatError(Exception):
    """Exception subclass for error encountered when a test file is not
    specified correctly.

    @type msg: C{str}.
    @ivar msg: message specifying what in test file isn't specified correctly.
    """

    def __init__(self, msg):
       self.msg = msg

    def __str__(self):
        return self.msg

class PytyTests(unittest.TestCase):

    def setUp(self):
        self.pyty_mod_obj = PytyMod()

    def _check_file(self, filename):
        debug("Checking %s" % filename)

        with open(filename, 'r') as f:
            
            expected_str = f.readline().strip('###').strip()

            if expected_str == "TypeIncorrectlySpecifiedError":
                self.assertRaises(TypeIncorrectlySpecifiedError,   
                    parse_type_declarations, filename)
                return

            env = parse_type_declarations(filename)
            
            a = ast.parse(f.read())
            
            if expected_str == "True" or expected_str == "False":
                try:
                    # test if it's looking for a true or false value.
                    exp = ast.literal_eval(expected_str)

                    self.assertEqual(exp, typecheck(env, a, self.pyty_mod_obj))
                except TypeUnspecifiedError:
                    self.fail("A variable type was not specified, but the " +
                           "program is either supposed to typecheck or " +
                            "be checked with no errors.")

            elif expected_str == "TypeUnspecifiedError":
                # test if it's looking for a TypeUnspecifiedError. if
                # there end up being a lot of possible errors, might want to
                # generalize this, but if there are only going to be a couple,
                # might as well just include each case explicitly.
                self.assertRaises(TypeUnspecifiedError, typecheck,
                        env, a, self.pyty_mod_obj)

            else:
                raise TestFileFormatError("Expected test value or error " +
                        "specified improperly")


    ##### Generated unit tests will go below here
    def test_one_line_compliated6(self):
        self._check_file("test_files/one_line_compliated6.py")

    def test_one_line_assign5(self):
        self._check_file("test_files/one_line_assign5.py")

    def test_one_line_add7(self):
        self._check_file("test_files/one_line_add7.py")

    def test_one_line_assign3(self):
        self._check_file("test_files/one_line_assign3.py")

    def test_one_line_assign12(self):
        self._check_file("test_files/one_line_assign12.py")

    def test_one_line_mod6(self):
        self._check_file("test_files/one_line_mod6.py")

    def test_one_line_mod4(self):
        self._check_file("test_files/one_line_mod4.py")

    def test_one_line_div5(self):
        self._check_file("test_files/one_line_div5.py")

    def test_one_line_assign4(self):
        self._check_file("test_files/one_line_assign4.py")

    def test_one_line_div1(self):
        self._check_file("test_files/one_line_div1.py")

    def test_one_line7(self):
        self._check_file("test_files/one_line7.py")

    def test_one_line_add8(self):
        self._check_file("test_files/one_line_add8.py")

    def test_one_line_assign6(self):
        self._check_file("test_files/one_line_assign6.py")

    def test_one_line_mod10(self):
        self._check_file("test_files/one_line_mod10.py")

    def test_one_line_complicated1(self):
        self._check_file("test_files/one_line_complicated1.py")

    def test_one_line_div3(self):
        self._check_file("test_files/one_line_div3.py")

    def test_one_line_div6(self):
        self._check_file("test_files/one_line_div6.py")

    def test_if9(self):
        self._check_file("test_files/if9.py")

    def test_one_line_add5(self):
        self._check_file("test_files/one_line_add5.py")

    def test_one_line_div8(self):
        self._check_file("test_files/one_line_div8.py")

    def test_one_line_complicated10(self):
        self._check_file("test_files/one_line_complicated10.py")

    def test_if6(self):
        self._check_file("test_files/if6.py")

    def test_one_line_add3(self):
        self._check_file("test_files/one_line_add3.py")

    def test_one_line_complicated11(self):
        self._check_file("test_files/one_line_complicated11.py")

    def test_one_line_mult2(self):
        self._check_file("test_files/one_line_mult2.py")

    def test_one_line_assign10(self):
        self._check_file("test_files/one_line_assign10.py")

    def test_one_line3(self):
        self._check_file("test_files/one_line3.py")

    def test_if8(self):
        self._check_file("test_files/if8.py")

    def test_one_line_mult3(self):
        self._check_file("test_files/one_line_mult3.py")

    def test_one_line_assign2(self):
        self._check_file("test_files/one_line_assign2.py")

    def test_one_line_sub4(self):
        self._check_file("test_files/one_line_sub4.py")

    def test_one_line_div4(self):
        self._check_file("test_files/one_line_div4.py")

    def test_one_line_div2(self):
        self._check_file("test_files/one_line_div2.py")

    def test_one_line_sub7(self):
        self._check_file("test_files/one_line_sub7.py")

    def test_one_line_mult4(self):
        self._check_file("test_files/one_line_mult4.py")

    def test_one_line_complicated7(self):
        self._check_file("test_files/one_line_complicated7.py")

    def test_one_line_mult5(self):
        self._check_file("test_files/one_line_mult5.py")

    def test_one_line_complicated3(self):
        self._check_file("test_files/one_line_complicated3.py")

    def test_if5(self):
        self._check_file("test_files/if5.py")

    def test_one_line_sub1(self):
        self._check_file("test_files/one_line_sub1.py")

    def test_if3(self):
        self._check_file("test_files/if3.py")

    def test_if11(self):
        self._check_file("test_files/if11.py")

    def test_one_line_complicated8(self):
        self._check_file("test_files/one_line_complicated8.py")

    def test_one_line_sub6(self):
        self._check_file("test_files/one_line_sub6.py")

    def test_one_line_add2(self):
        self._check_file("test_files/one_line_add2.py")

    def test_one_line_mod7(self):
        self._check_file("test_files/one_line_mod7.py")

    def test_one_line_add1(self):
        self._check_file("test_files/one_line_add1.py")

    def test_if10(self):
        self._check_file("test_files/if10.py")

    def test_one_line_mod5(self):
        self._check_file("test_files/one_line_mod5.py")

    def test_if2(self):
        self._check_file("test_files/if2.py")

    def test_one_line_mod2(self):
        self._check_file("test_files/one_line_mod2.py")

    def test_one_line_assign7(self):
        self._check_file("test_files/one_line_assign7.py")

    def test_one_line_div9(self):
        self._check_file("test_files/one_line_div9.py")

    def test_one_line_mod9(self):
        self._check_file("test_files/one_line_mod9.py")

    def test_one_line_mult6(self):
        self._check_file("test_files/one_line_mult6.py")

    def test_one_line_assign1(self):
        self._check_file("test_files/one_line_assign1.py")

    def test_one_line_sub5(self):
        self._check_file("test_files/one_line_sub5.py")

    def test_one_line_complicated2(self):
        self._check_file("test_files/one_line_complicated2.py")

    def test_one_line_assign9(self):
        self._check_file("test_files/one_line_assign9.py")

    def test_if7(self):
        self._check_file("test_files/if7.py")

    def test_one_line_complicated12(self):
        self._check_file("test_files/one_line_complicated12.py")

    def test_one_line6(self):
        self._check_file("test_files/one_line6.py")

    def test_one_line_mod3(self):
        self._check_file("test_files/one_line_mod3.py")

    def test_one_line_div7(self):
        self._check_file("test_files/one_line_div7.py")

    def test_one_line_complicated13(self):
        self._check_file("test_files/one_line_complicated13.py")

    def test_one_line_complicated9(self):
        self._check_file("test_files/one_line_complicated9.py")

    def test_one_line_add6(self):
        self._check_file("test_files/one_line_add6.py")

    def test_one_line_mult1(self):
        self._check_file("test_files/one_line_mult1.py")

    def test_one_line_complicated4(self):
        self._check_file("test_files/one_line_complicated4.py")

    def test_one_line_assign11(self):
        self._check_file("test_files/one_line_assign11.py")

    def test_one_line4(self):
        self._check_file("test_files/one_line4.py")

    def test_one_line_sub2(self):
        self._check_file("test_files/one_line_sub2.py")

    def test_if1(self):
        self._check_file("test_files/if1.py")

    def test_one_line_add4(self):
        self._check_file("test_files/one_line_add4.py")

    def test_one_line5(self):
        self._check_file("test_files/one_line5.py")

    def test_one_line_mod1(self):
        self._check_file("test_files/one_line_mod1.py")

    def test_if4(self):
        self._check_file("test_files/if4.py")

    def test_one_line_sub3(self):
        self._check_file("test_files/one_line_sub3.py")

    def test_one_line_mod8(self):
        self._check_file("test_files/one_line_mod8.py")

    def test_one_line_assign8(self):
        self._check_file("test_files/one_line_assign8.py")

    def test_one_line_complicated5(self):
        self._check_file("test_files/one_line_complicated5.py")

    def test_one_line2(self):
        self._check_file("test_files/one_line2.py")

    def test_one_line_mult7(self):
        self._check_file("test_files/one_line_mult7.py")

    def test_one_line_complicated6(self):
        self._check_file("test_files/one_line_complicated6.py")

    def test_one_line_assign13(self):
        self._check_file("test_files/one_line_assign13.py")
    ##### Generated unit tests will go above here

if __name__ == '__main__':
    unittest.main()

