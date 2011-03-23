import unittest
import ast
import sys

# Include src in the Python search path.
sys.path.insert(0, '../src')

from ast_extensions import *
from typecheck import *
from parse import  parse_type_decs
from errors import *
import errors
from generate_tests import _TEST_CODE_DIR

"""
This is just the core of the unit testing file. generate_tests.py must be run
to fill this file with the several unit tests (each of which tests one source
code file in the test_files directory).
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

class PytyTests(unittest.TestCase):

    def _check_expr(self, s, expr_kind, type, expected):
        """Typechecks the string C{s} as an C{expr_type} expression."""

        a = ast.parse(s).body[0].value
            
        f = get_expr_func_name(expr_kind)

        if expected == "pass":
            self.assertEqual(True, call_function(f, a, type, {}),
                             "Should typecheck but does not (%s)." % s)
        elif expected == "fail":
            self.assertEqual(False, call_function(f, a, type, {}),
                             "Shouldn't typecheck but does. (%s)." % s)
        elif issubclass(getattr(errors, expected), PytyError):
            # if the expected value is an error, then make sure it
            # raises the right error.
            try:
                call_function(f, a, type, {})
            except getattr(errors, expected):
                pass
            else:
                self.fail("Should have raised error %s, but does not. (%s)."
                          % (expected, s))                
        else:
            raise TestFileFormatError("Expression tests can only be" + \
                " specified as passing, failing, or raising an error " + \
                " specified in errors.py, but this test was specified " + \
                " as expecting: " + expected)

    def _parse_and_check_mod(self, filename):
        with open(filename, 'r') as f:
            text = f.read()

        untyped_ast = ast.parse(text)
        typedecs = parse_type_decs(filename)
        typed_ast = TypeDecASTModule(untyped_ast, typedecs)
        env_ast = EnvASTModule(typed_ast)
        return check_mod(env_ast)

    def _check_mod(self, filename):
        """Typechecks the contents of file C{filename} as a
        module. The file will contain a header of the form '### Pass'
        to indicate whether the module is expected to pass or fail
        typechecking or throw a specified error.
        """

        with open(filename, 'r') as f:
            expected = f.readline().strip('###').strip()
            text = f.read()

        if expected == "pass":
            # the third parameter is a message displayed if assertion fails.
            self.assertEqual(True, self._parse_and_check_mod(filename),
                             "Should typecheck, but does not:\n%s" % text)
        elif expected == "fail":
            # the third parameter is a message displayed if assertion fails.
            self.assertEqual(False, self._parse_and_check_mod(filename),
                             "Shouldn't typecheck, but does:\n%s" % text)
        elif issubclass(eval(expected), PytyError):
            try:
                self._parse_and_check_mod(filename)
            except getattr(errors, expected):
                pass
            else:
                self.fail("Should raise error %s, but does not:\n%s"
                          % (expected, text.strip('\n')))
        else:
            # in generate_tests.py, we should have already ensured that the
            # expecetd string is pass, fail, or a valid error name, so this case
            # should never be reached, but this is here just in case.
            raise Exception("Expected test result not specified with a " +
                            "valid value")
    

    ##### Generated unit tests will go below here
    ##### Generated unit tests will go above here

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "d":
        _DEBUG = True
        del sys.argv[1]     # this is becasue unittest gets mad if there are 
                            # command line arguments it doesn't understand

    unittest.main()

