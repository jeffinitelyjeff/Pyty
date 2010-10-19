import compiler
import ast

_MULTIPLE_VARIABLE_ASSIGNS = "Multiple variables assignments in one line"

class PyTyError(Exception):
    """Bass error class for PyTy errors.

    @type msg: C{str}.
    @ivar msg: Explanation of error message.
    """

    def __init__(self, msg):
        self.msg = msg

class AssignmentBuilder(ast.NodeVisitor):
    """Node visitor which inspects each node to gather the list of variables
    in the AST and stores a dictionary mapping line numbers to variables
    assigned on that line.

    @type dict: C{dict} {C{int} : C{tuple} (variables)}
    @ivar dict: Dictionary storing line number to variables mapping.
    """

    def __init__(self):
        dict = {}

    def visit(node):
        if ast_type(node) == "Assign":
            # If the node is an assignment node, its repr will be of the form:
            #   Assign([AssName('x', 'OP_ASSIGN')], expr), where x is the name
            #   of the variable being assigned and expr is the expression
            #   assigned to x.
            
            # Assuming the first child node of every Assign node is an AssName
            # node.
            # TODO: need to cover cases of x,y,z = 1,2,3
            varname = node.getChildNodes()[0].name

            if node.lineno in dict:
                # Note: this is meant to throw an error in the strange case of
                # there being multiple Assign nodes on the same line, not in the
                # case of x,y,z = 1,2,3, which will be addressed later (and I'm
                # guessing is handled differently than there being 3 Assign
                # nodes on the same line).
                raise PyTyError(_MULTIPLE_VARIABLE_ASSIGNS)
            else:
                dict[lineno] = varname

def get_ast(filename):
    """Returns the Abstract Syntax Tree for the Python code in file 
    C{filename}. This actually returns the topmost node in the Abstrsact Syntax
    Tree.

    @type filename: C{str}.
    @param filename: A valid path to a Python source code file.
    @rtype: an AST.
    @return: An Abstract Syntax Tree for the code in the file if it is a valid
    Python source code file, none if it isn't.
    """

    try:
        return compiler.parseFile(filename).node
    except IOError:
        return None

def ast_type(node):
    """Returns the type of the AST node C{node}.

    @type node: an AST node.
    @paraam node: an AST node.
    @rtype: C{str}
    @return: C{str} representation of the type of C{node}.ast.
    """

    # The string representation for AST nodes contains the type of node.
    return node.__repr__().split('(')[0]
