import ast
import logging

from util import disjoint_sum, cname
from parse_type import PType, TypeSpecParser

def dump_self(self):
    return ast.dump(self)
ast.mod.__repr__ = dump_self
ast.stmt.__repr__ = dump_self
ast.expr.__repr__ = dump_self

### ---------------------------------------------------------------------------
### Information about AST statements ------------------------------------------
### ---------------------------------------------------------------------------

# Set of strings representing all simple Python statements.
_simple_stmts = set(("Assign Return Delete AugAssign Raise Assert Import "
                     "ImportFrom Print Pass Break Continue TypeDec").split())

# Set of strings representing all Python compound statements that have all
# their children statements in one node, `body`.
_body_stmts = set("FunctionDef ClassDef With".split())

# Set of strings representing all Python compound statements that have all
# their children statements in a `body` node and an `orelse` node.
_body_orelse_stmts = set("If While For TryExcept".split())

# Set of strings representing all Python compound statements that have all
# their children statements in a `body` node and a `finally` node.
_body_finally_stmts = set("TryFinally".split())

# Every compound statement is a body, body_orelse, or body_finally statement,
# and they should all be disjoint.
_compound_stmts = _body_stmts | _body_orelse_stmts | _body_finally_stmts
assert disjoint_sum(_compound_stmts,
                    [_body_stmts, _body_orelse_stmts, _body_finally_stmts])

# Every statement is a simple or compound statement.
_all_stmts = _simple_stmts | _compound_stmts
assert disjoint_sum(_all_stmts, [_simple_stmts, _compound_stmts])

def _is_simple_stmt(self):
    """This method should only be called by an `ast.stmt` node."""
    return self.__class__.__name__ in _simple_stmts
ast.stmt.is_simple = _is_simple_stmt

def _is_compound_stmt(self):
    """This method should only be called by an `ast.stmt` node."""
    return self.__class__.__name__ in _compound_stmts
ast.stmt.is_compound = _is_compound_stmt

def _is_body_stmt(self):
    """This method should only be called by an `ast.stmt` node."""
    return self.__class__.__name__ in _body_stmts
ast.stmt.is_body = _is_body_stmt

def _is_body_orelse_stmt(self):
    """This method should only be called by an `ast.stmt` node."""
    return self.__class__.__name__ in _body_orelse_stmts
ast.stmt.is_body_orelse = _is_body_orelse_stmt

def _is_body_finally_stmt(self):
    """This method should only be called by an `ast.stmt` node."""
    return self.__class__.__name__ in _body_finally_stmts
ast.stmt.is_body_finally = _is_body_finally_stmt

def _get_stmt_lists(self):
    """
    Returns a tuple of the statement lists contained in this `ast.stmt`
    node. This method should only be called by an `ast.stmt` node.
    """

    if self.is_simple():
        return ()
    elif self.is_body():
        return (self.body,)
    elif self.is_body_orelse():
        return (self.body, self.orelse)
    elif self.is_body_finally():
        return (self.body, self.finalbody)
    else:
        # Every statement has to be simple or complex.
        assert(False)
ast.stmt.stmt_lists = _get_stmt_lists

def _get_last_lineno(self):
    """
    Returns the last line number of statements contained in this `ast.stmt`
    node. If `self` is a simple statement, then this is just the statement's
    line number.

    This method should only be called by an `ast.stmt` node.
    """

    branches = self.stmt_lists()

    if len(branches) == 0:

        # Simple statement.
        return self.lineno

    elif len(branches) == 1:

        # Compound statement with only one branch.
        body = branches[0]

        if len(body) == 0:
            # Empty body shouldn't happen, or it at least shouldn't parse.
            assert False, "Stmt with one branch and empty shouldn't parse"
        else:
            return body[-1].lineno

    else: # len(branches) == 2

        # Compound statement with two branches.
        body1 = branches[0]
        body2 = branches[1]

        if len(body2) > 0:
            return body2[-1].lineno
        elif len(body1) > 0:
            return body1[-1].lineno
        else:
            # Both empty bodies shouldn't happen, or at least it shouldn't
            # parse.
            assert False, "Stmt with two empty branches shouldn't parse"
ast.stmt.last_lineno = _get_last_lineno

### ----------------------------------------------------------------------------
### TypeDec class and methods to add typedec to an AST -------------------------
### ----------------------------------------------------------------------------

class TypeStore():
    """Context to use for an ast.Name node when declaraing the identifier's
    type. I don't think there's anything special about the contexts except
    whether they're an instance of ast.Store or ast.Load, so I don't think this
    needs to do anything special.
    """

    def __init__(self):
        pass

    def __repr__(self):
        return "TypeStore()"

class TypeDec(ast.stmt):
    """
    A TypeDec is an AST statement node which represents the assertion that a
    variable or function is of a certain type. This is effectively a
    side-effecting expression, where the side-effect is the alteration of the
    type environment of the program. Storing these type declarations as AST
    nodes should allow us to treat their processing more uniformly.
    TypeDec AST nodes will be added to the generic AST in a second-run of
    parsing. A normal ast.AST will be generated with ast.parse, then a
    line-by-line parsing of the source code will put these TypeDec nodes in
    their proper places.

    @type targets: list of ast.Name
    @ivar targets: The list of variables which are having their types declared.
    @type t: PType
    @ivar t: A PType object representing the type which the C{targets} are
        being declared as.
    @type lineno: int
    @ivar lineno: The line number of the declaration in the source code.
    @type col_offset: int
    @ivar col_offset: The column offset of the beginning of the declaration (ie,
        the '#:' in the source code).
    """

    def __init__(self, targets, t, line, col = None):
        """Creates a L{TypeDec} node with the supplied parameters.

        @type targets: list of ast.Name
        @param targets: The list of variables which are having their types
            declared.
        @type t: PType
        @param t: The type which the C{targets} are declared as. If a string is
            provided, then a PType object will be created based on this
            string.
        @type line: int
        @param line: The line number of the source code for the declaration.
        @type col: int
        @param col: The column number of the source code for the declaration.
        """

        self.targets = targets
        self.lineno = line
        if col is not None:
            self.col_offset = col

        if type(t) == str:
            self.t = PType(t)
            assert self.t.__class__ == PType, \
                   ("Got a %s back from TypeSpecParser.parse, not a PType" %
                    cname(self.t.__class__))
        elif t.__class__ == PType:
            self.t = t
        else:
            assert False, ("t needs to be specified as str or PType, not " +
                           cname(t))


        # these are instance variables provided by AST nodes to allow traversal
        # / parsing of the nodes.
        self._fields = ("targets", "t")
        self._attributes = ("lineno", "col_offset")

        # XXX Provide some way to specify target name nodes by their id's?

    @staticmethod
    def is_typedec(node):
        return node.__class__.__name__ == "TypeDec"

    def place_in_module(self, mod):
        """Places this L{TypeDec} instance in its proper place (according to its
        C{lineno}) in the module represented by the AST node C{mod}.
        """

        self._place_in_stmt_list(mod.body)

    def _place_in_stmt_list(self, stmt_list):
        """
        Place this `TypeDec` instance in its proper place in AST statement node
        list `stmt_list`.
        """

        # For each index and corresponding statement in `stmt_list`.
        for (i, stmt) in zip(range(len(stmt_list)), stmt_list):

            assert self.lineno != stmt.lineno, \
                "This typedec shouldn't already exist in the AST"

            # Place `self` if we've gone past the desired lineno or hit the end
            # of the list. Note: this will always be reached eventually.
            if self.lineno < stmt.lineno or i == len(stmt_list) - 1:

                # If the desired lineno is past the previous statement's last
                # lineno, then just put `self` before the next statement;
                # otherwise, put `self` inside the previous statement.

                if self.lineno > stmt_list[i-1].last_lineno():
                    stmt_list.insert(i, self)
                    return
                else: # self.lineno < stmt_list[i-1].last_lineno()
                    assert stmt_list[i-1].is_compound()
                    self._place_in_compound_stmt(stmt_list[i-1])
                    return

    def _place_in_compound_stmt(self, stmt):
        """
        Place this `TypeDec` instance in its proper place within the AST
        compound statement node `stmt`.

        Pre-condition: `stmt.is_compound()`
        Pre-condition: `stmt.lineno < self.lineno < stmt.last_lineno()`
        """

        # Assert pre-conditions.
        assert stmt.is_compound()
        assert stmt.lineno < self.lineno < stmt.last_lineno(), \
            str(stmt.lineno) + " < " + str(self.lineno) + " < " + \
            str(stmt.last_lineno())


        branches = stmt.stmt_lists()

        if len(branches) == 1:

            # Compound statemnet with only one branch.
            body = branches[0]

            self._place_in_stmt_list(body)

        else: # len(branches) == 2

            # Compound statement with two branches.
            body1 = branches[0]
            body2 = branches[1]

            if self.lineno < body1.last_lineno():
                self._place_in_stmt_list(body1)
            else:
                self._place_in_stmt_list(body2)

class TypeDecASTModule:
    """A wrapper for an C{ast.Module} which has the property that all of its
    children nodes have been populated with additional nodes (not specified in
    the standard AST library) to represent Pyty type declarations.

    @type tree: C{ast.Module}
    @ivar tree: The AST backing this L{TypeDecASTModule}, which has been modified to
        include the L{TypeDec} nodes.
    @type typedecs: C{list} of L{TypeDec}
    @ivar typedecs: The L{TypeDec} type declarations that have been added to
        this AST.
    """

    def __init__(self, untyped_tree, typedecs, clone=False):
        if clone:
            self.original_tree = untyped_tree
            self.tree = copy.deepcopy(untyped_tree)
        else:
            self.tree = untyped_tree

        self.clone = clone
        self.typedecs = typedecs

        # place each type declaration
        for typedec in typedecs:
            self.place_typedec(typedec)

    def __str__(self):
        return "Tree:\n" + str(self.tree) + "\nTypedecs:\n" + str(self.typedecs)

    def get_original_tree(self):
        """Returns the original tree if this L{TypeDecAST} was initialized as a
        copy (with the clone flag), and returns C{None} otherwise.
        """

        if clone:
            return self.original_tree
        else:
            return None

    def place_typedec(self, typedec):
        """Places the specified L{TypeDec} in this L{TypeDecAST}. This is
        essentially a wrapper for the L{TypeDec} method which places the typedec
        in a specified AST.
        """

        typedec.place_in_module(self.tree)
