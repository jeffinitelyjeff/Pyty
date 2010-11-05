import unittest
from typer import typecheck
from parser_helper import get_ast, find_node_by_line

_BASIC_FILE = "basic_file.py"

class TestAssignment(unittest.TestCase):

    def setUp(self):
        self.tree = get_ast(_BASIC_FILE) 

    def test_file(self):
        # File should not typecheck because the last line does +(str, int).
        # Environment is empty since all variables are defined within the file.
        self.assertFalse(typecheck(self.tree, {}))

    def test_line_1(self):
        # Line 1: a = "hi"
        # so it should typecheck with the empty environment.
        node = find_node_by_line(self.tree, 1)
        self.assertTrue(does_typecheck(self.tree, {}))

    def test_line_2(self):
        # Line 2: x = 5*6*10
        # so it should typecheck with the empty environment.
        node = find_node_by_line(self.tree, 2)
        self.assertTrue(does_typecheck(self.tree, {}))

    def test_line_3(self):
        # Line 3: y = 3
        # so it should typecheck with the empty environment.
        node = find_node_by_line(self.tree, 3)
        self.assertTrue(does_typecheck(self.tree, {}))

    def test_line_4(self):
        # Line 4: z0 = x + y
        # so it should typecheck with an environment specifying the types of x 
        # and y.
        node = find_node_by_line(self.tree, 4)
        
        # TODO: in order to specify what x and y are, need to decide how I'm
        # representing environments.
        # env = ...

        self.assertTrue(does_typecheck(self.tree, env))

    def test_line_5(self):
        # Line 5: z1 = a + x
        # so it should not typecheck with an environment specifying the types of
        # a and x, even though the environment is satisfactory.
        node = find_node_by_line(self.tree, 5)

        # TODO: find type definition for a
        # TODO: find type definition for x
        # TODO: create env with type definitions

        # pass if unsatisfactoryenvironment
        # fail if doesnottypecheck
        # fail if no errors thrown (assertRaises fails if no errors)
        try:
            with self.assertRaises(DoesNotTypecheck):
                typecheck(self.tree, env)
        except UnsatisfactoryEnvironment:
            self.fail("UnsatisfactoryEnvironment error was thrown when \
                DoesNotTypecheck error was expected")

    def test_line_6(self):
        # Line 6: z2 = b + x
        # so an environment specifying the types of b and x is needed.
        node = find_node_by_line(self.tree, 6)

        # TODO: ...
        
