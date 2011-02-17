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

_SPEC_DIR = "spec"
_SPEC_EXPR_PREFIX = "expr_"
_SPEC_MOD_PREFIX = "mod_"

_TEST_CODE_DIR = "test_files"
_UNIT_TEST_CORE = "unit_test_core.py"
_UNIT_TEST_OUTPUT = "_unit_test_gen.py"

def create_expression_tests(file_name):
    """Creates expression typechecking unit tests based on a specification
    file of the following format.

    spec mode: expr
    expr type: expr_type
    
    ---pass---
    expr1
    expr2
    ...
    exprn
    ---fail---
    exprn+1
    exprn+2
    ...
    exprn+m

    where expr_type specifies what type of AST node the expression corresponds
    to (capitalized or not), expr1-n should all typecheck correctly, and
    exprn+1-m should not typecheck."""

    tests = ""
    test_count = 0

    with open(file_name, 'r') as f:
        text = f.read()
        head = text.split('---pass---')[0]
        pass_tests = text.split('---pass---')[1].split('---fail---')[0]
        fail_tests = text.split('---fail---')[1]

        expr_type = head.split('expr type: ')[1].strip()

        test_template = "    def test_%s(self):\n" + \
            "self._check_expr(\"%s\",\"%s\",\"%s\")\n\n"

        for l in pass_tests:
            count += 1
            t = test_template % (file_name+str(count), l, expr_type, "pass")
            tests = tests + t
        for l in fail_tests:
            count += 1
            t = test_template % (file_name+str(count), l, expr_type, "fail")
            tests = tests + t

    return tests

def create_module_tests(file_name):
    """Creates module typechecking unit tests based on a specification
    file of the following format.

    spec mode: module
    
    ---pass---
    m
    o
    d
    1
    ---
    ...
    ---
    m
    o
    d
    n
    ---fail---
    m
    o
    d
    n+1
    ---
    ...
    m
    o
    d
    n+m
    ---

    modules 1 through n should all typecheck correctly, and module n+1 through 
    m should not."""

    tests = ""

    # TODO Implement!

    return tests

# remove generated test source code
for file_name in os.listdir(_TEST_CODE_DIR):
    os.remove(_TEST_FILE_DIR + '/' + file_name)

tests = ""

# create new tests (this generates the test source code for module tests as an
# intermediate step)
for file_name in os.listdir(_SPEC_DIR):
    if file_name.startswith(_SPEC_EXPR_RPEFIX):
        tests = tests + create_expression_tests(file_name)
    elif file_name.starstwith(_SPEC_MOD_PREFIX):
        tests = tests + create_module_tests(file_name)

# remove the tailing newline
tests = tests[0:-1]

flag1 = "    ##### Generated unit tests will go below here\n"
flag2 = "    ##### Generated unit tests will go above here\n"

with open(_UNIT_TEST_CORE, 'r') as f:
    core_text = f.read();

replaced = core_text.replace(flag1+flag2, flag1+tests+flag2)

with open(_UNIT_TEST_OUTPUT, 'w') as f:
    f.write(replaced)
