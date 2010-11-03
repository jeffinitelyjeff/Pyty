import unittest
from typer import typecheck
from parser_helper import get_ast, find_node_by_line

_BASIC_FILE = "basic_file.py"

class TestAssignment(unittest.TestCase):

    def setUp(self):
        self.tree = get_ast(_BASIC_FILE) 
        self.env = {}

    def test_file(self):
        does_type = typecheck(self.tree, self.env)
        self.assertFalse(does_type)

    def test_lines_1_through_4(self):
        for i in range(1, 4):
            node = find_node_by_line(self.tree, i)
            does_type

