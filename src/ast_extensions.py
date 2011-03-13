import ast

from util import are_disjoint, disjoint_sums_of

### These are classifications of statement types essentially based on whether
### the statement is multi-line or not. All statement types in
### _SIMPLE_STATEMENTS do not have lists of statements as children, but every
### statement type in _COMPOUND_STATEMENT does have at least one list of
### statements as a child.

_SIMPLE_STATEMENTS = set([ "Assign", "Return", "Delet", "AugAssign", "Raise",
                           "Assert", "Import", "ImportFrom", "Print", "Pass",
                           "Break", "Continue" ])
_COMPOUND_STATEMENTS = set([ "If", "While", "FunctionDef", "ClassDef", "For",
                             "With", "TryExcept", "TryFinally" ])
_ALL_STATEMENTS = _SIMPLE_STATEMENTS.union(_COMPOUND_STATEMENTS)

# simple and compound statement should not overlap.
assert(_are_disjoint(_SIMPLE_STATEMENTS, _COMPOUND_STATEMENTS)

### These are classifications of compound statements based on the structure of
### their corresponding AST node. Body statements contain only one list of
### statements labeled "body", body-orelse statements contain lists of
### statements labeled "body" and "orelse", and body-finally statements contain
### lists of statements labeled "body" and "finally".

_BODY_STATEMENTS = set([ "FunctionDef", "ClassDef", "With" ])
_BODY_ORELSE_STATEMENTS = set([ "If", "While", "For", "TryExcept" ])
_BODY_FINALLY_STATEMENTS = set([ "TryFinally" ])

# make sure the complex statements are a disjoint sum of these statements.
assert(_disjoint_sums_of([_BODY_STATEMENTS, _BODY_ORELSE_STATEMENTS,
                          _BODY_FINALLY_STATEMENTS], _COMPOUND_STATEMENTS)

### ----------------------------------------------------------------------------
### TypeDec class and methods to add typedec to an AST -------------------------
### ----------------------------------------------------------------------------

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
        """Creates a L{TypeDec} node with the supplied parameters.

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

    def place_in_module(self, mod):
        """Places this L{TypeDec} instance in its proper place (according to its
        C{lineno}) in the module represented by the AST node C{mod}.
        """

        self._place_in_stmt_list(mod.body)

    def _place_in_stmt_list(self, stmt_list):
        """Places this L{TypeDec} instance in its proper place (according to its
        C{lineno}) in the list of statement AST nodes provided by C{stmt_list}.
        """

        idx = 0

        # iterate through stmt_list until we hit a lineno that's too far.
        for stmt in stmt_list:
            if stmt.lineno > self.lineno:
                break

            # the line of this typedec should definitely not already be in the
            # AST, at least for now. XXX ONELINETYPEDEC
            assert(stmt.lineno != self.lineno)

            idx += 1

        self._place_near_stmt(stmt_list, idx)

    def _place_near_stmt(self, stmt_list, pos):
        """Places this L{TypeDec} instance in the correct position 'near' the
        statement at position C{pos} in the list of statements C{stmt_list}. If
        the specified statement is a simple (one-line) statement, then this just
        means placing this L{TypeDec} directly after the statement; if the
        specified statement is a compound (multi-line) statement, then this
        means placing this L{TypeDec} in the proper place within the compound
        statement.

        @precondition: stmt_list[pos].lineno < self.lineno and
            stmt_list[pos+1].lineno > self.lineno
        """

        stmt = stmt_list[pos]

        if stmt in _SIMPLE_STATEMENTS:
            # if the preceeding statement is simple, then just place the typedec
            # after the statement.
            stmt_list.insert(pos + 1, typedec)
        elif stmt in _COMPOUND_STATEMENTS:
            # if the preceeding statement is complex, then figure out what kind of
            # statement AST structure it has, and place the typedec into the right
            # list of child statements.

            branch1 = stmt.body
            # branch2 = None ### XXX this might be necessary? dunno.

            if stmt in _BODY_ORELSE_STATEMENTS:
                branch2 = stmt.orelse
            elif stmt in _BODY_FINALLY_STATEMENTS:
                branch2 = stmt.finally

            if stmt in _BODY_STATEMENTS or branch2[0].lineno > self.lineno:
                # place the typedec in the first list of statements if the statement
                # type only has one branch or the lineno of the first line of the
                # second branch is past the desired lineno.
                self._place_in_stmt_list(branch1)
            else:
                # place the typedec in the second list of statements otherwise (ie,
                # if the statement type has more than one branch and the first line
                # of the second branch is not past the desired lineno).
                self._place_in_stmt_list(branch2)
        else:
            # statements are a disjoint sum of simple and compound statements, so
            # this default case should never be reached.
            assert(False)

### ----------------------------------------------------------------------------
### Functions to add environment info to an AST populated with TypeDec nodes ---
### ----------------------------------------------------------------------------
            
def embed_environments(mod):
    """Reads in a module AST and, for each statement, adds an instance variable
    called C{env} which is the environment of type declarations at that current
    state of the program. C{env} is stored as a dictionary mapping variable
    identifiers to PytyType objects.
    """

    is_mod = mod.__class__.__name__ == "Module"

    assert(is_mod)

    if is_mod:
        return _embed_environment_stmt_list(mod.body, {})
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
        # This should only be called on compound statements, which the three
        # previous cases form a disjoint sum of..
        assert(False)


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
                _embed_environment_stmt_list(stmt_list, old_env)

            # statements don't show up as children of other nodes (except as
            # statement lists of course), and expressions don't get any
            # environments added, so statement lists is all we really have to
            # worry about
            
        return tree.env

    # according to the Python API, AST nodes are disjoint sums of expressions,
    # statements, and modules, so we should never reach here.
    else:
        assert(False)

def _embed_environment_stmt_list(stmts, old_env):
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


    
        
