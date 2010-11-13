import unittest
from ast import parse
from typer import typecheck

"""
This is just the core of the unit testing file. generate_tests.py must be run
to fill this file with the several unit tests (each of which tests one source
code file in the test_files directory).

Test file format:

### True|False

<Python code>
"""

class TestFileFormatError(Exception):
    """Exception subclass for error encountered when a test file is not
    specified correctly.

    @type msg: C{str}.
    @ivar msg: message specifying what in test file isn't specified correctly.
    """

    def __init__(msg):
       self.msg = msg

    def __str__(msg):
        return "TestFileFormatError: " + self.msg

class PytyTests(unittest.TestCase):

    def _check_file(self, filename):

        with open(filename, 'r') as f:

            expected_str = f.readline().split('### ')[1].split('\n')[0]

            if expected_str == 'True':
                expected = True
            elif expected_str == 'False':
                expected = False
            else:
                raise TestFileFormatError("Expected test value not specified \
                properly")

            tree = ast.parse(f.read())

        self.assertEqual(expected, typecheck({}, tree, "Module"))
       

    ##### Generated unit tests will go below here
    ##### Generated unit tests will go above here

if __name__ == '__main__':
    unittest.main()

