import logging

LOG_LEVEL = logging.DEBUG
LOGFILE = "test_log.log"  # log file lives in the root of the app
LOG_DIR = "../"           # all logging will be called from either src/ or
                          # test/, which have the root as their parent, and we
                          # want the log to go in the root for now (maybe will
                          # have a log directory later)

TEST_DIR = "test/"               # test directory lives in the root of the app
TEST_CODE_SUBDIR = "test_files/" # test code subdir lives in the test dir

UNIT_TEST_CORE = "unit_tests_core.py"    # unit test core lives in the test dir
UNIT_TEST_OUTPUT = "_unit_tests_gen.py" # unit test output lives in the test
                                         # dir

SPEC_SUBDIR = "spec/"      # spec subdir lives in the test dir
SPEC_EXPR_PREFIX = "expr_" # prefix for files specifying expr tests
SPEC_MOD_PREFIX = "mod_"   # prefix for files specifying module tests

FILE_DEBUG = True
DEBUG_SUBJECT_FILE = "mod_assignment11.py"
DEBUG_TYPEDEC_PARSING = False
DEBUG_UNTYPED_AST     = False
DEBUG_TYPEDECS        = False
DEBUG_TYPED_AST       = False
DEBUG_ENV_AST         = False
DEBUG_TYPECHECK       = True
DEBUG_INFER           = True
