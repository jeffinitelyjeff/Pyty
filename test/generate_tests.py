import os

"""
Generates unit tests based on the current contents of the test_files
directory. When executed, will remove all unit tests from pyty_tests.py and
fill in unit tests for the current contents of test_files.  
"""

_UNIT_TEST_CORE = "pyty_tests_core.py"
_UNIT_TEST_OUTPUT = "pyty_tests.py"
_TEST_FILE_DIR = "test_files"

tests = ""

file_names = os.listdir(_TEST_FILE_DIR)

# for each file, insert a unit test
for file_name in file_names:
    base_file_name = file_name.split(".")[0]

    tests = tests + "    def test_%s(self):\n" % base_file_name
    tests = tests + "        self._check_file(\"%s/%s\")\n" % (_TEST_FILE_DIR,
            file_name)
    tests = tests + "\n"

# remove the tailing newline
tests = tests[0:-1]

flag1 = "    ##### Generated unit tests will go below here\n"
flag2 = "    ##### Generated unit tests will go above here\n"

with open(_UNIT_TEST_CORE, 'r') as f:
    core_text = f.read();

replaced = core_text.replace(flag1+flag2, flag1+tests+flag2)

with open(_UNIT_TEST_OUTPUT, 'w') as f:
    f.write(replaced)
