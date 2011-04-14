import re
import os
import sys
import logging
from datetime import datetime

# Include src in the Python search path.
sys.path.insert(0, '../src')

from errors import *
import typecheck
from settings import *
from logger import announce_file

"""
Uses the specification of the files in C{TEST_SPECS} to generate lots of
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

announce_file("generate_tests.py")

def _expr_test_function_def(test_name, expr_string, expr_kind,
                            type, expected_result):
    template = "    def test_%s(self):\n" + \
               "        self._check_expr(\"%s\",\"%s\",\"%s\",\"%s\")\n\n"
    return template % (test_name, expr_string, expr_kind, type, expected_result)

# note: the expected result is not used in creating the test call because that
#       information is stored in the file generated to hold the module.
def _mod_test_function_def(file_name, file_name_path):
    base_file_name = file_name.split('.')[0]
    template = "    def test_%s(self):\n" + \
               "        self._check_mod(\"%s\")\n\n"
    return template % (base_file_name, file_name_path)

def _create_generic_tests(spec_file, result_delim, test_delim, expr_kind):
    """Creates typechecking unit tests based on a specification file of the
    following format:

    HEADER
    \result_delim{test_result_1}\result_delim
    \test_delim\test_1\test_delim
    \test_delim\test_2\test_delim
    ...
    \result_delim{test_result_2}\result_delim
    \test_delim\test_n+1\test_delim
    ...
    """

    tests = ""
    count = 0

    with open(SPEC_SUBDIR + spec_file, 'r') as f:
        text = f.read()

    split_text = text.split(result_delim)

    if expr_kind != "mod":
        # If we're dealing with expression tests, make sure that there is a
        # function in typecheck.py to actually deal with that kind of
        # expression.
        try:
            getattr(typecheck, 'check_'+expr_kind+'_expr')
        except AttributeError:
            raise Exception("Expression test spec states that checking " +
                            "against expressions of type " + check_type +
                            ", but that functionality is not included " +
                            "in PyTy (yet).")

    # delete the stuff above the first test
    del split_text[0] 

    # go through each test specification
    while len(split_text) > 0:
        # split_text will be of form: [expected_result, tests, ...]
        expected_result = split_text[0]
        things_to_test = split_text[1]

        # make sure a valid test result was specified
        if not expected_result in ('pass', 'fail') \
            and not issubclass(eval(expected_result), Exception):
            raise Exception("Test spec (for " + check_type +
                            ") not of valid format")

        split_things = things_to_test.split(test_delim)
        
        if expr_kind == "mod":

            for mod in split_things:
                if mod != '' and mod.strip('\n') != '':
                    count += 1

                    file_name = spec_file.split('.')[0]+str(count)+'.py'

                    with open(TEST_CODE_SUBDIR + file_name, 'w') as g:
                        g.write("### " + expected_result)
                        g.write(mod)

                    test = _mod_test_function_def(file_name,
                                                  TEST_CODE_SUBDIR+file_name) 
                    tests = tests + test

        else:

            for expr in split_things:
                # make a test if the expression isn't blank and isn't a comment.
                if expr != '' and not re.match(r'^#[^\n]*$', expr):
                    count += 1

                    actual_expr = expr.split(':')[0].strip()
                    type = expr.split(':')[1].strip()

                    test_name = spec_file.split('.')[0]+str(count)
                    
                    test = _expr_test_function_def(test_name, actual_expr,
                                                   expr_kind, type, expected_result)
                    
                    tests = tests + test

        # get rid of this section of tests to proceed
        del split_text[0]
        del split_text[0]

    return tests

def create_expression_tests(spec_file):
    with open(SPEC_SUBDIR + spec_file, 'r') as f:
        text = f.read()
        expr_type = text.split('expr type: ')[1].split('\n')[0].strip()
    
    return _create_generic_tests(spec_file, '----', '\n', expr_type)

def create_module_tests(spec_file):
    return _create_generic_tests(spec_file, '----', '---', "mod")

# remove generated test source code
for file_name in os.listdir(TEST_CODE_SUBDIR):
    os.remove(TEST_CODE_SUBDIR + file_name)

tests = ""

# create new tests (this creates files to contain the module tests as an
# intermediate step). 
for file_name in os.listdir(SPEC_SUBDIR):
    if file_name.endswith('.spec'):
        if file_name.startswith(SPEC_EXPR_PREFIX):
            tests = tests + create_expression_tests(file_name)
        elif file_name.startswith(SPEC_MOD_PREFIX):
            tests = tests + create_module_tests(file_name)

# remove the tailing newline
tests = tests[0:-1]

flag1 = "    ##### Generated unit tests will go below here\n"
flag2 = "    ##### Generated unit tests will go above here\n"

with open(UNIT_TEST_CORE, 'r') as f:
    core_text = f.read();

replaced = core_text.replace(flag1+flag2, flag1+tests+flag2)

with open(UNIT_TEST_OUTPUT, 'w') as f:
    f.write(replaced)
