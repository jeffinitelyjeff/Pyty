import ast

# These are statements which do not contain statement children.
_SIMPLE_STATEMENTS = ( "Assign", "Return", "Delet", "AugAssign", "Raise",
                       "Assert", "Import", "ImportFrom", "Print", "Pass",
                       "Break", "Continue" )

# These are statements which do contain statement children.
_COMPOUND_STATEMENTS = ( "If", "While", "FunctionDef", "ClassDef", "For",
                         "With", "TryExcept", "TryFinally" )

assert(set(_SIMPLE_STATEMENTS).intersection(set(_COMPOUND_STATEMENTS)) = set([]))

# These are statements which contain statements in just a list called "body".
_BODY_STATEMENTS = ( "FunctionDef", "ClassDef", "With" )

# These are statements which contain statements in lists called "body" and
# "orelse".
_BODY_ORELSE_STATEMENTS = ( "If", "While", "For", "TryExcept" )

# These are statements which contain statements in lists called "body" and
# "finally".
_BODY_FINALLY_STATEMENTS = ( "TryFinally", )

assert(set(_BODY_STATEMENTS).issubset(
    set(_SIMPLE_STATEMENTS).union(set(_COMPOUND_STATEMETNS))))
assert(set(_BODY_ORELSE_STATEMENTS).issubset(
    set(_SIMPLE_STATEMENTS).union(set(_COMPOUND_STATEMETNS))))
assert(set(_BODY_FINALLY_STATEMENTS).issubset(
    set(_SIMPLE_STATEMENTS).union(set(_COMPOUND_STATEMETNS))))

       

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

def place_typedec(tree, typedec):
    """Traverses the AST C{tree} and finds the proper place to insert the type
    declaration based on the line numbers of the nodes in the AST.
    """

    # TODO implement
    
def place_typedec_in_stmt_list(stmt_list, typedec):
    """Places the typedec in the proper position of the lit of statements."""

    lower_bound_idx = 0
    lower_bound_stmt = None

    # increment lower_bound_idx until we hit a lineno that's past the desired lineno
    for stmt in stmt_list:
        if stmt.lineno > typedec.lineno:
            break

        # the line of the typedec should definitely not already be in the AST.
        assert(stmt.lineno != typedec.lineno)

        lower_bound_idx += 1
        lower_bound_stmt = stmt
    
    # if the lower bound we found is a simple statement (one that does not have
    # statement children), then we can just insert the typedec.
    if stmt in _SIMPLE_STATEMENTS:
        


def embed_environments(mod):
    """Reads in a module AST and, for each statement, adds an instance variable
    called C{env} which is the environment of type declarations at that current
    state of the program. C{env} is stored as a dictionary mapping variable
    identifiers to PytyType objects.
    """

    is_mod = mod.__class__.__name__ == "Module"

    assert(is_mod)

    if is_mod:
        return _embed_environment_stmtlist(mod.body, {})
    else:
        return None
    

def _get_stmt_lists(node):
    """Provides a layer of abstraction for extracting all the children from a
    node that are lists of statements."""

    node_type = node.__class__.__name__

    if node_type in _BODY_ORELSE_STATEMENTS:
        return (node.body, node.orelse)
    elif node_type in _BODY_STATEMENTS:
        return (node.body)
    elif node_type in _BODY_FINALLY_STATEMENTS:
        return (node.body, node.finalbody)
    else:
        return tuple()

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
        # we only need to add typedefs to the dictionary if it's a TypeDec statement
        if tree.__class__.__name__ = "TypeDec":
            new_env = old_env.copy()
            
            for target in tree.targets:
                new_env[target.id] = tree.t
                
            tree.env = new_env
        # but if it's any kind of statement with children, we need to recurse
        # down and assign environments to those nodes.
        else:
            tree.env = old_env

            # need to get all the children which are lists of statements. AST's
            # built-in function of iter_child_nodes won't quite do the job here,
            # as it'll just return a generator with all the children nodes
            # flattened.
            stmt_lists = _get_stmt_lists(tree)

            for stmt_list in stmt_lists:
                _embed_environment_stmtlist(stmt_list, old_env)

            # statements don't show up as children of other nodes (except as
            # statement lists of course), and expressions don't get any
            # environments added, so statement lists is all we really have to
            # worry about
            
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

    @returns: The environment at the end of the list of statements. This will
    only be used when processing the list of statements in a module to get a
    "master" environment for a file to use in debugging.
    """

    working_env = old_env
    
    for s in stmts:
        working_env = _embed_environment_node(s, working_env)

    return working_env

        
def find_env(expr):
    """This should only be called on an expression within an AST that has
    already been propogated with environments. All statements will have
    environments set as instance variables, but expressions will have to refer
    to the environments of their parent statements. XXX This probably will be
    redundant, because the environments of the parent statements will be
    accessed and then typecheck will be called with those environments when the
    children expressions are typechecked.
    """

    # this function is pointless to call on anything other than expressions.
    assert(isinstance(expr, ast.expr))

    # TODO implement if necessary


    
        
