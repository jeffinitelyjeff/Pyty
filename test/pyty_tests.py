import unittest
import ast
import sys

# Include src in the Python search path.
sys.path.insert(0, '../src')

from typecheck import typecheck
from pyty_types import PytyMod

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

    def setUp(self):
        self.pyty_mod_obj = PytyMod()

    def _check_file(self, filename):

        with open(filename, 'r') as f:

            expected_str = f.readline().strip('###').strip()

            # expected_str needs to be either 'True' or 'False'
            try:
                expected_bool = ast.literal_eval(expected_str)
            except ValueError:
                raise TestFileFormatError("Expected test value not specified \
                properly")
            
            tree = ast.parse(f.read())

        self.assertEqual(expected_bool, typecheck({}, tree, self.pyty_mod_obj))
       

    ##### Generated unit tests will go below here
    def test_one_line7(self):
        self._check_file("test_files/one_line7.py")

    def test_one_line5(self):
        self._check_file("test_files/one_line5.py")

    def test_one_line4(self):
        self._check_file("test_files/one_line4.py")

    def test_one_line2(self):
        self._check_file("test_files/one_line2.py")

    def test_one_line1(self):
        self._check_file("test_files/one_line1.py")

    def test_one_line3(self):
        self._check_file("test_files/one_line3.py")

    def test_one_line6(self):
        self._check_file("test_files/one_line6.py")
    ##### Generated unit tests will go above here

if __name__ == '__main__':
    unittest.main()

