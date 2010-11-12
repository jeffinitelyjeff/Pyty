import os

"""
Generates unit tests based on the current contents of the test_files
directory. When executed, will remove all unit tests from pyty_tests.py and
fill in unit tests for the current contents of test_files.  
"""

_UNIT_TEST_FILE = "pyty_tests.py"

with open(_UNIT_TEST_FILE, 'r') as f:
    file_lines = f.readlines()

# find the index of the first "#####"
# delete all lines between first "#####" and second "#####"
# get list of all source files
# for each source file, create the unit testing for it  


