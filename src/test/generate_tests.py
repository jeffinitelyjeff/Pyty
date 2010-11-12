import os

"""
Generates unit tests based on the current contents of the test_files
directory. When executed, will remove all unit tests from pyty_tests.py and
fill in unit tests for the current contents of test_files.  
"""

_UNIT_TEST_CORE = "pyty_tests_core.py"
_UNIT_TEST_OUTPUT = "pyty_tests.py"
_TEST_FILE_DIR = "test_files"

# open the unit test file and make an in-memory copy -------------------------
with open(_UNIT_TEST_CORE, 'r') as f:
    file_lines = f.readlines()

# find the index of the "#####"s ---------------------------------------------
seen_start = False
for line in file_lines:
    if "#####" in line and not seen_start:
        start_line = line
        seen_start = True
    elif "#####" in line and seen_start:
        end_line = line
        break

start_idx = file_lines.index(start_line)
end_idx = file_lines.index(end_line)

# delete all lines between start_idx and end_idx -----------------------------
while (end_idx - start_idx != 1):
    del file_lines[start_idx + 1]
    end_idx -= 1

# get list of all source files -----------------------------------------------
source_files = os.listdir(_TEST_FILE_DIR)

# for each source file, create the unit testing for it -----------------------
for source_file in source_files:
    file_lines.insert(end_idx, "    def test_%s(self):\n" % source_file)
    end_idx += 1

    file_lines.insert(end_idx, "        _check_file(\"%s/%s\")\n" % \
            (_TEST_FILE_DIR, source_file))
    end_idx += 1
    
    file_lines.insert(end_idx, "\n")
    end_idx += 1

# delete extra \n at end to make it look nicer
del file_lines[end_idx - 1]
end_idx -= 1

# rewrite the unit test file -------------------------------------------------
with open(_UNIT_TEST_OUTPUT, 'w') as f:
    f.writelines(file_lines)
