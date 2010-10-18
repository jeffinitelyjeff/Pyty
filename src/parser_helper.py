import compiler.parseFile
import ast.NodeVisitor

class PyTyNodeVisitor(ast.NodeVisitor):

    def visit(node):
        

def get_ast(filename):
    """Returns the Abstract Syntax Tree for the Python code in file 
    C{filename}.

    @type filename: C{str}.
    @param filename: A valid path to a Python source code file.
    @rtype: an AST.
    @return: An Abstract Syntax Tree for the code in the file if it is a valid
    Python source code file, none if it isn't.
    """

    return compiler.parseFile(filename)
