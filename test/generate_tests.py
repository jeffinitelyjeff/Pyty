import os

"""
Uses the specification of the files in C{_TEST_SPECS} to generate lots of
individual python source code files which are all placed in the directory
specified by C{_TEST_FILE_DIR}.
Then generates a unit test for every individual python source file created.

Note: In test specification documents, files will be specified as:
[Name of test] - [Expected typecheck behavior]
[Source code]
but in the generated python source files (with file name
[KindOfTest_NameOfTest]), this will be formatted as:
### [Expected typecheck behavior]
[Source code]
"""

# Maps descriptions of kinds of tests to the spec documents.
_TEST_SPECS = {"one_line" : "one_liners.txt"}
# File containing all the non-generated work of the unit tests.
_UNIT_TEST_CORE = "pyty_tests_core.py"
# File to store the test file with the generated unit tests.
_UNIT_TEST_OUTPUT = "pyty_tests.py"
# Directory to store individual python test source files.
_TEST_FILE_DIR = "test_files"

# --- Helper Functions -------------------------------------------------------

def create_source_files(source, prefix):
    with open(source, 'r') as f:
        file_data = f.read().split("---")[1:]
        for file_datum in file_data:
            file_datum = file_datum.strip('\n')

            if file_datum != '':
                test_name = file_datum.split(' - ')[0]

                # for some reason file_datum.strip('\n'+filen_name+'\n') went
                # crazy here and would remove 'e\n' or 'ue\n' from the end.
                file_body = '### '+file_datum.split(test_name+' - ')[1]+'\n'

                with open("%s/%s_%s.py" % 
                          (_TEST_FILE_DIR, prefix, test_name), 'w') as g:
                    g.write(file_body)

def unit_test_code(test_file_name):
    base_file_name = test_file_name.split(".")[0]

    return "    def test_%s(self):\n" % base_file_name + \
           "        self._check_file(\"%s/%s\")\n\n" % (_TEST_FILE_DIR,
                test_file_name)


# --- Create test files based on specification document ----------------------

# clear out the previous contents of the test files directory.
for file_name in os.listdir(_TEST_FILE_DIR):
    os.remove(_TEST_FILE_DIR + '/' + file_name)

# create new contents of the test file directory.
for test_kind in _TEST_SPECS:
    create_source_files(_TEST_SPECS[test_kind], test_kind)

# --- Read test files and make unit tests ------------------------------------

tests = ""
file_names = os.listdir(_TEST_FILE_DIR)

# insert a unit test for each file
for file_name in file_names:
    tests = tests + unit_test_code(file_name)

# remove the tailing newline
tests = tests[0:-1]

flag1 = "    ##### Generated unit tests will go below here\n"
flag2 = "    ##### Generated unit tests will go above here\n"

with open(_UNIT_TEST_CORE, 'r') as f:
    core_text = f.read();

replaced = core_text.replace(flag1+flag2, flag1+tests+flag2)

with open(_UNIT_TEST_OUTPUT, 'w') as f:
    f.write(replaced)


