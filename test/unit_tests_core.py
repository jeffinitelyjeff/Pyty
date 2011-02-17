import unittest
import ast
import sys

# Include src in the Python search path.
sys.path.insert(0, '../src')

from typecheck import *
from parse import  parse_type_declarations
from errors import TypeUnspecifiedError, TypeIncorrectlySpecifiedError

"""
This is just the core of the unit testing file. generate_tests.py must be run
to fill this file with the several unit tests (each of which tests one source
code file in the test_files directory).

Test file format:

### True|False|[ErrorName]

<Python code>
"""

_DEBUG = False

def debug(string):
    """Prints string if global variable _DEBUG is true, otherwise
    does nothing
    
    @type string: C{str}.
    @param string: a string.
    """

    if _DEBUG: print string

def debug_c(test, string):
    """Prints string if debugging is on and test is C{True}.

    @type test: C{bool}.
    @param test: a boolean test.
    @type string: C{str}.
    @param string: a string.
    """

    if test and _DEBUG: debug(string)

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

    def _check_expr(self, s, expr_type, expected):
    """Typechecks the string C{s} as an C{expr_type} expression."""

        a = ast.parse(s)

        f = get_expr_func_name(expr_type)

        if expected == "pass":
            self.assertEqual(True, call_function(f, a, {}))
        elif expected == "fail":
            self.assertEqual(False, call_function(f, a, {}))
        else:
            raise TestFileFormatError("Expression tests can only be" +
                "specified as passing or failing, but this test was" +
                "specified as: " + expected)
    
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
                    expection = ast.literal_eval(expected_str)
                    
                    if expection:
                        fail_msg = "Should typecheck, but does not."
                    else:
                        fail_msg = "Shouldn't typecheck, but does."

                    self.assertEqual(expection, 
                        check_mod(a, env), fail_msg)
                except TypeUnspecifiedError as e:
                    self.fail("A variable type (" + e.var + ") was not " + 
                        "specified somewhere, but the program is either " + 
                        "supposed to typecheck or be checked with no errors.")

            elif expected_str == "TypeUnspecifiedError": 
                # test if it's looking for a TypeUnspecifiedError. if
                # there end up being a lot of possible errors, might want to
                # generalize this, but if there are only going to be a couple,
                # might as well just include each case explicitly.
                self.assertRaises(TypeUnspecifiedError, check_mod,
                        a, env)

            else:
                raise TestFileFormatError("Expected test value or expected " +
                    "error specified improperly")


    ##### Generated unit tests will go below here
    ##### Generated unit tests will go above here

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "d":
        _DEBUG = True
        del sys.argv[1]     # this is becasue unittest gets mad if there are 
                            # command line arguments it doesn't understand

    unittest.main()

 
