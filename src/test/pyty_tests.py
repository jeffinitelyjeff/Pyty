import unittest

"""
Test file format:

### True|False

<Python code>
"""

class pyty_tests(unittest.TestCase):

    def _checkfile(filename):
        # * Open file
        # * Read first line to determine whether the test should return
        #   True or False.
        # * Delete first line.
        # * Check file.
        pass
    
    def test_oneline1(self):
        self._checkfile('one_line1.py')

if __name__ == '__main__':
    unittest.main()

