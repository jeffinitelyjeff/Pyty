import os

"""
Generates unit tests based on the current contents of the test_files
directory. When executed, will remove all unit tests from pyty_tests.py and
fill in unit tests for the current contents of test_files.  
"""

_ONE_LINERS_SOURCE = "one_liners.txt"
_UNIT_TEST_CORE = "pyty_tests_core.py"
_UNIT_TEST_OUTPUT = "pyty_tests.py"
_TEST_FILE_DIR = "test_files"

with open(_ONE_LINERS_SOURCE, 'r') as f:
    file_data = f.read().split("---")[1:]
    for file_datum in file_data:
        file_datum = file_datum.strip('\n')

        if file_datum != '':
            file_name = file_datum.split('\n')[0]

            # for somer reason file_datum.strip('\n'+filen_name+'\n') went
            # crazy here and would remove 'e\n' or 'ue\n' from the end.
            file_body = file_datum.split(file_name + '\n')[1] + '\n'

            with open(_TEST_FILE_DIR + '/' + file_name, 'w') as g:
                g.write(file_body)

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
