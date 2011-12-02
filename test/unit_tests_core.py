import unittest
import ast
import sys
import logging
from datetime import datetime
import ast

# Include src in the Python search path.
sys.path.insert(0, '../src')

from ast_extensions import TypeDecASTModule
from typecheck import (check_expr, check_mod, get_check_expr_func_name,
                       call_function)
from parse_file import parse_type_decs
from ptype import PType
from errors import TypeUnspecifiedError, TypeIncorrectlySpecifiedError
from settings import (TEST_CODE_SUBDIR, DEBUG_SUBJECT_FILE, DEBUG_UNTYPED_AST,
                      DEBUG_TYPED_AST, DEBUG_TYPEDECS)
from logger import Logger, announce_file
from util import log_center

# these should be redundant, but they're necessary to refer to the specific log
# objects.
import ast_extensions
import parse_file
import typecheck
import infer

"""
This is just the core of the unit testing file. generate_tests.py must be run
to fill this file with the several unit tests (each of which tests one source
code file in the test_files directory).
"""

announce_file("unit_tests_core.py")

log = typecheck.log = parse_file.log = infer.log = Logger()

class PytyTests(unittest.TestCase):

    def _check_expr(self, s, expr_kind, typ, expected):
        """Typechecks the string C{s} as an C{expr_type} expression."""

        a = ast.parse(s).body[0].value

        f = get_check_expr_func_name(expr_kind)

        if expected == "pass" or expected == "fail":
            t = PType(typ)

        if expected == "pass":
            self.assertEqual(True, call_function(f, a, t, {}),
                             "%s should typecheck as %s but does not." % (s,t))
        elif expected == "fail":
            self.assertEqual(False, call_function(f, a, t, {}),
                             "%s shouldn't typecheck as %s but does." % (s, t))
        elif issubclass(eval(expected), Exception):
            # if the expected value is an error, then make sure it
            # raises the right error.
            try:
                t = PType(typ)
                call_function(f, a, t, {})
            except eval(expected):
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

        debug_file = TEST_CODE_SUBDIR + DEBUG_SUBJECT_FILE
        if filename == debug_file:
            log.enter_debug_file()
        else:
            log.exit_debug_file()

        log.debug("--- v File : " + filename + " v ---\n" + text + "--- ^ File text ^ ---")

        untyped_ast = ast.parse(text)

        log.debug((log_center("v Untyped AST v") + str(untyped_ast) +
                   log_center("^ Untyped AST ^")), DEBUG_UNTYPED_AST)

        typedecs = parse_type_decs(filename)

        log.debug((log_center("v TypeDecs v") + str(typedecs) +
                   log_center("^ TypeDecs ^")), DEBUG_TYPEDECS)

        typed_ast = TypeDecASTModule(untyped_ast, typedecs)

        log.debug((log_center("v TypedAST v") + str(typed_ast) +
                   log_center("^ TypedAST ^")), DEBUG_TYPED_AST)

        return check_mod(typed_ast.tree)

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
        else:
            # in generate_tests.py, we should have already ensured that the
            # expected string is "pass", "fail", or a valid error name, so we
            # should be able to parse the error name at this point, and if not
            # then we have other issues.
            try:
                err = eval(expected)
            except NameError:
                # at this point, expected better be a valid error name.
                assert(False)

            # at this point, the error better actually be a subclass of
            # Exception, since generate.py tests will already throw errors if
            # improper errors are specified.
            assert(issubclass(err, Exception))

            try:
                result = self._parse_and_check_mod(filename)
                self.fail("Should raise error %s, but instead returned %s:\n%s"
                          % (expected, result, text.strip('\n')))
            except err:
                pass
            except AssertionError as e:
                self.fail(e)
            except Exception as e:
                self.fail("Should have raised %s, but instead raised %s (%s):\n%s" %
                          (expected, e.__class__.__name__, e, text.strip('\n')))

    ##### Generated unit tests will go below here
    ##### Generated unit tests will go above here

if __name__ == '__main__':
    unittest.main()

