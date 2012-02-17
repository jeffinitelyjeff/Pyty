import ast
import logging

from util import disjoint_sum, cname
from ptype import PType

def dump_self(self):
    return ast.dump(self)
ast.mod.__repr__ = dump_self
ast.stmt.__repr__ = dump_self
ast.expr.__repr__ = dump_self

## Information about AST statements

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
            return _get_last_lineno(body[-1])

    else: # len(branches) == 2

        # Compound statement with two branches.
        body1 = branches[0]
        body2 = branches[1]

        if len(body2) > 0:
            return _get_last_lineno(body2[-1])
        elif len(body1) > 0:
            return _get_last_lineno(body1[-1])
        else:
            # Both empty bodies shouldn't happen, or at least it shouldn't
            # parse.
            assert False, "Stmt with two empty branches shouldn't parse"
ast.stmt.last_lineno = _get_last_lineno


## TypeDec class and methods to insert TypeDecs into an AST

class TypeStore():
    """
    Context for an `ast.Name` node when in a `TypeDec` node.
    """

    def __init__(self):
        pass

    def __repr__(self):
        return "TypeStore()"

class TypeDec(ast.stmt):
    """
    An AST statement node which binds an identifier to a specified type.

    Before typechecking a module, a "typed" AST will be created by parsing the
    file to create proper `TypeDec` nodes and placing them appropriately in the
    AST.

    #### Instance variables
    - `targets`: the list of identifiers (as `ast.Name` objects) having their
        types declared.
    - `t`: the type (as a PType abject) being assigned.
    - `lineno`: the (int) line number of the declaration in the source code.
    - `col_offset`: the (int) column offset of the beginning of the declaration
        (i.e., the `#:` in the source code).
    """

    def __init__(self, targets, t, line, col = None):
        """
        Create a `TypeDec` node with the supplied parameters.

        #### Parameters
        - `targets`: list of identifiers (as `ast.Name` objects) having their
            types declared.
        - `t`: the type being assigned, as a PType or string. If a string is
            provided, it is parsed into the appropriate PType.
        - `line`: the (int) line number of the declaration in the source code.
        - `col`: [optional] the (int) column number of the declaration in the
            source code. If not provided, then the column number will just be
            set as `None`.
        """

        self.targets = targets
        self.lineno = line
        if col is not None:
            self.col_offset = col

        if type(t) == str:
            self.t = PType.from_str(t)
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

    @staticmethod
    def is_typedec(node):
        return node.__class__.__name__ == "TypeDec"

    def place_in_module(self, mod):
        """
        Place this `TypeDEc` instance in its proper place in AST module node
        `mod`.
        """

        self._place_in_stmt_list(mod.body)

    def _place_in_stmt_list(self, stmt_list):
        """
        Place this `TypeDec` instance in its proper place in AST statement node
        list `stmt_list`.

        NOTE: This all assumes that no blocks have a typedec as a last
        statement. If so, the typedec will probably be inserted after the block
        (or in the next part of the block). For determining whether a typedec is
        at the end of a block or after it, we can compare columns, but there is
        no way to tell whether a typedec is at the end of a block or at the
        beginning of an adjacent block (ie, body vs orelse blocks).
        """

        # For each index and corresponding statement in `stmt_list`
        for (i, stmt) in zip(range(len(stmt_list)), stmt_list):

            # Place `self` if we've gone past the desired lineno or hit the end
            # of the list. Note: one of these will always be reached eventually.

            if stmt.lineno > self.lineno:

                # If the desired lineno is past the previous statement's last
                # lineno, then just put `self` before the next statement;
                # otherwise, put `self` inside the previous statement.

                if i == 0 or self.lineno > stmt_list[i-1].last_lineno():
                    stmt_list.insert(i, self)
                    return
                else: # self.lineno < stmt_list[i-1].last_lineno()
                    self._place_in_compound_stmt(stmt_list[i-1])
                    return

            elif stmt.lineno == self.lineno:

                # We've hit a statement with the same line number as the type
                # declaration. This corresponds to cases like this:
                #   x = 5 #: x : int
                # We allow this even for compound statements because this could
                # be handy:
                #   for x in y: #: x : int

                stmt_list.insert(i, self)
                return

            elif i == len(stmt_list) - 1:

                # The desired lineno is past the last statement, so either it's
                # in the last statement or after it.

                if self.lineno > stmt.last_lineno():
                    stmt_list.insert(i+1, self)
                    return
                else: # self.lineno < stmt.last_lineno()
                    self._place_in_compound_stmt(stmt)
                    return


    def _place_in_compound_stmt(self, stmt):
        """
        Place this `TypeDec` instance in its proper place within the AST
        compound statement node `stmt`.

        Pre-condition: `stmt.is_compound()`
        Pre-condition: `stmt.lineno < self.lineno < stmt.last_lineno()`

        NOTE: This all assumes that no blocks have a typedec as a last
        statement. If so, the typedec will probably be inserted after the block
        (or in the next part of the block). For determining whether a typedec is
        at the end of a block or after it, we can compare columns, but there is
        no way to tell whether a typedec is at the end of a block or at the
        beginning of an adjacent block (ie, body vs orelse blocks).
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

            if len(body1) == 0:
                body1_last = stmt.lineno
            else:
                body1_last = body1[-1].lineno

            if self.lineno < body1_last:
                self._place_in_stmt_list(body1)
            else:
                self._place_in_stmt_list(body2)

class TypeDecASTModule:
    """
    A wrapper for an `ast.Module` which has the property that all of its
    children nodes have been populated with additional nodes (not specified in
    the standard AST library) to represent Pyty type declarations.

    #### Instance variables
    - `tree`: the `ast.Module` AST wrapped, which has been modified to include
        `TypeDec` nodes in proper locations.
    - `typedecs`: list of `TypeDec` nodes which have been added to this AST.
    - `clone`: whether `tree` was created by directly modifying a provided
        untyped AST or if a copy was modified.
    - `original_tree`: (only exists if `clone` is `True`) the untyped AST which
        was populated wiht `TypeDec`s.
    """

    def __init__(self, untyped_tree, typedecs, clone=False):
        """
        Create `TypeDecASTModule` from an AST that has no type declarations and
        a list of type declarations to add. Can insert the `TypeDec` nodes into
        the provided tree, or into a clone of the provided tree.

        #### Parameters:
        - `untyped_tree`: the `ast.Module` AST without any type declarations.
        - `typedecs`: list of `TypeDec` nodes to add to `untyped_tree`.
        - `clone`: whether to modify `untyped_tree` directly or instead operate
            on a copy. Defaults to modifying `untyped_tree` directly.
        """

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
        """
        Return the original tree if this `TypeDecAST` was initializeda s a copy
        (with the `clone` field), and returns `None` otherwise.
        """

        if clone:
            return self.original_tree
        else:
            return None

    def place_typedec(self, typedec):
        """
        Place the specified `TypeDec` in this `TypeDecASTModule`.
        """

        typedec.place_in_module(self.tree)
