import ast

class TypeDec(ast.stmt):
    """A TypeDec is an AST statement node which represents the assertion that a
    variable or function is of a certain type. This is effectively a
    side-effecting expression, where the side-effect is the alteration of the
    type environment of the program. Storing these type declarations as AST
    nodes should allow us to treat their processing more uniformly.

    TypeDec AST nodes will be added to the generic AST in a second-run of
    parsing. A normal ast.AST will be generated with ast.parse, then a
    line-by-line parsing of the source code will put these TypeDec nodes in
    their proper places.
    """

    def __init__(targets, t, line, col):
        """Creates a C{TypeDec} node with the supplied parameters.

        @type targets: list of ast.Name
        @param targets: The list of variables which are having their types
        declared. A list is permitted to allow for cases of declaring several
        variables at once.
        @type t: PytyType
        @param t: A PytyType object representing the type which the C{targets}
        are declared as.
        @type line: int
        @param line: The line number of the source code for the declaration.
        @type col: int
        @param col: The column number of the source code for the declaration.
        """

        self.targets = targets
        self.t = t
        self.lineno = line
        self.col = col


def embed_environments(tree):
    """Reads in an AST and, for each statement, adds an instance variable called
    C{env} which is the environment of type declarations at that current state
    of the program. C{env} is stored as a dictionary mapping variable
    identifiers to PytyType objects.
    """

    for child in ast.iter_child_nodes(tree):

def _embed_environment_node(tree, old_env):
    """Recursive helper for embed_environment to add environments to AST nodes.
    There are three distinct types of nodes that this can be called on:
    expressions, statements, and modules. We are only attaching environments to
    statements, so expressions and modules are ignored; it makes no sense for a
    module to have an environment, but the decision about expressions is a
    matter of preference, and is chosen in the spirit of lazy evaluation (ie,
    not assigning environment references all over the place when
    possibly/probably unnecessary). For convenience, this function returns the
    environment which is added to the node, or None if an environment isn't set.
    """

    # if tree is an expression.
    if isinstance(tree, ast.expr) or isinstance(tree, ast.module):
        # no environment will be added, so return None to signal this.
        return None

    # if tree is a statement
    elif isinstance(tree, ast.stmt):
        # we only need to do real work if it's a TypeDec statement
        if tree.__class__.__name__ = "TypeDec":
            new_env = old_env.copy()
            
            for target in tree.targets:
                new_env[target.id] = tree.t
                
            tree.env = new_env
        else:
            tree.env = old_env

        return tree.env

    # according to the Python API, AST nodes are disjoint sums of expressions,
    # statements, and modules, so we should never reach here.
    else:
        assert(False)

def _embed_environment_stmtlist(stmts, old_env):
    """Recursive helper for embed_environment to add environments to lists of
    statements. The list of statements to be processed is assumed to be
    consecutively ordered within one block (and consisting of the entire block),
    so we assume that the working environment of line n is the working
    environment of line n-1, plus any type declarations that may have been added
    in line n. We do not need to return or keep track of the environment at the
    end of the list of statements because we are assuming that C{stmts} is the
    entire contents of one block, so, once we're done with the block, we should
    no longer know or care about the type declarations from within the block.
    """

    working_env = old_env
    
    for s in stmts:
        working_env = _embed_environment_node(s, working_env)

        
            
        
