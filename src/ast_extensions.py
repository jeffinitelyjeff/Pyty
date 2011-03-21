import ast

from util import are_disjoint, disjoint_sums_of
from pyty_types import PytyTypes

class ASTInfo:
    """
    Class to encapsulate and provide info about the AST.

    @type simple_stmts: C{set} of C{str}
    @cvar simple_stmts: Statement types that do not contain other statements as
        children.
    @type compound_stmts: C{set} of C{str}
    @cvar compound_stmts: Statement types that do contain other statements as
        children.
    @type all_stmts: C{set} of C{str}
    @cvar all_stmts All statement types.
    @type body_stmts: C{set} of C{str}
    @cvar body_stmts: Compound statement types that contain statement children
        in one list labeled 'body'.
    @type body_orelse_stmts: C{set} of C{str}
    @cvar body_orelse_stmts: Compound statement types that contain statement
        children in one list labeled 'body' and another list labeled 'orelse'.
    @type body_finally_stmts: C{set} of C{str}
    @cvar body_finally_stmts: Compound statement types that contain statement
        children in one list labeled 'body' and another list labeled 'finally'.
    """

    simple_stmts = set(("Assign Return Delete AugAssign Raise Assert " + \
                        "Import ImportFrom Print Pass Break Continue").split())
    compound_stmts = set(("If While FunctionDef ClassDef For With " + \
                          "TryExcept TryFinally").split())
    all_stmts = simple_stmts.union(compound_stmts)

    # simple and compound statements should not overlap.
    assert(are_disjoint(simple_statements, compound_statements))


    body_stmts = set("FunctionDef ClassDef With".split())
    body_orelse_stmts = set("If While For TryExcept".split())
    body_finally_stmts = set("TryFinally".split())
    
    # make sure the compound statements are a disjoint sum of these statements.
    assert(disjoint_sums_of([body_stmts, body_orelse_stmts, body_finally_stmts],
                            compound_stmts))

    @staticmethod
    def is_node_of_type(obj, node_type):
        """Returns whether the object has the proper type as determined by the
        name of its class.

        @param obj: an object.
        @type node_type: str
        @param node_type: the name of the class which this is checking the
            object against.
        """
        
        return obj.__class__.__name__ == node_type

    @staticmethod
    def get_stmt_lists(node):
        """Returns a tuple of the stmt lists that are children of this AST
        C{node}. Provided so clients don't need to ask what kind of compound
        statement C{node} is.
        """
    
        node_type = node.__class__.__name__

        if node_type in _BODY_ORELSE_STATEMENTS:
            return (node.body, node.orelse)
        elif node_type in _BODY_STATEMENTS:
            return (node.body)
        elif node_type in _BODY_FINALLY_STATEMENTS:
            return (node.body, node.finalbody)
        else:
            # This should only be called on compound statements, which the three
            # previous cases form a disjoint sum of.
            assert(False)


### ----------------------------------------------------------------------------
### TypeDec class and methods to add typedec to an AST -------------------------
### ----------------------------------------------------------------------------

class TypeStore():
    """Context to use for an ast.Name node when declaraing the identifier's
    type. I don't think there's anything special about the contexts except
    whether they're an instance of ast.Store or ast.Load, so I don't think this
    needs to do anything special.
    """
    
    pass
           
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
    @type t: PytyType
    @ivar t: A PytyType object representing the type which the C{targets} are
        being declared as.
    @type lineno: int
    @ivar lineno: The line number of the declaration in the source code.
    @type col_offset: int
    @ivar col_offset: The column offset of the beginning of the declaration (ie,
        the '#:' in the source code).
    """

    def __init__(targets, t, line, col):
        """Creates a L{TypeDec} node with the supplied parameters.

        @type targets: list of ast.Name
        @param targets: The list of variables which are having their types
            declared. 
        @type t: PytyType
        @param t: The type which the C{targets} are declared as. If a string is
            provided, then a PytyType object will be created based on this
            string.
        @type line: int
        @param line: The line number of the source code for the declaration.
        @type col: int
        @param col: The column number of the source code for the declaration.
        """
    
        self.targets = targets
        self.lineno = line
        self.col_offset = col

        if isinstance(t, str):
            self.t = PytyType(t)
        else:
            self.t = t

        # XXX Provide some way to specify target name nodes by their id's.

    @staticmethod
    def is_typedec(node):
        return ASTInfo.is_node_of_type(node, "TypeDec")

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

        for typedec in typedecs:
            self.place_typedec(typedec)

    def __str__(self):
        return str(self.tree) + " with " + str(self.typedecs)

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
        
### ----------------------------------------------------------------------------
### Functions to add environment info to an AST populated with TypeDec nodes ---
### ----------------------------------------------------------------------------

class EnvASTModule(TypeDecASTModule):
    """A L{TypeDecASTModule} which has the property that each statement node
    contained in the wrapped AST has an additional field to represent the type
    environment for the execution of that statement. The environments are stored
    as dictionaries called C{env}, and are mappings from variable identifiers to
    L{PytyType} objects.

    @type tree: C{ast.Module}
    @ivar tree: The AST backing this L{EnvASTModule}, which has been modified to
        include the type environments.
    """

    def __init__(self, typed_tree, clone=False):
        # make sure that it is initialized with a module AST node.
        assert(typed_tree.__class__.__name__ == "Module")
        
        if clone:
            self.tree = copy.deepcopy(typed_tree)
        else:
            self.tree = typed_tree

        self._embed_environment()

    def _embed_environment(self):
        """For each statement node of this L{EnvASTModule}'s underlying AST,
        adds an instance variable called C{env} which is the type environment at
        that stage of execution. 
        """

        return _embed_environment_stmt_list(self.tree.body, {})

    @staticmethod
    def _embed_environment_node(node, old_env):
        """Recursive helper for embed_environment to add environments to AST
        nodes.  There are three distinct types of nodes that this can be called
        on: expressions, statements, and modules. We are only attaching
        environments to statements, so expressions and modules are ignored; it
        makes no sense for a module to have an environment (also, a module
        should not have module children, and this is only called on the children
        of modules), but the decision about expressions is a matter of
        preference, and is chosen in the spirit of lazy evaluation (ie, not
        assigning environment references all over the place when
        possibly/probably unnecessary). For convenience, this function returns
        the environment which is added to the node, or None if an environment
        isn't set.
        """

        if isinstance(node, ast.mod):

            # this method should never be called when self.tree is a module.
            assert(False)
            
        elif isinstance(node, ast.expr):

            # no environment will be added, so return None to signal this.
            return None
        
        elif isinstance(node, ast.stmt):

            if is_typedec(node):
                # if it's a typedec, then add typedefs to the dictionary.
                
                node.env = old_env.copy()

                for target in node.targets:
                    node.env[target.id] = node.t

                return node.env

            elif is_simple_stmt(node):
                # if it's a simple statement, but not a typedec, then the
                # enviroment is the same as the previous statement's
                # environment.

                # NOTE for now, if the environment doesn't change between
                # statements, the same env dictionary is being stored with a
                # different reference; I don't think this should cause any
                # issues for now, but we'll see.
                node.env = old_env

                return node.env

            elif is_compound_stmt(node):
                # if it's a compound statement, then add environments to the
                # children statements, but we need to process each block
                # differently so that variables declared in an if block aren't
                # usable in the else block.

                # TODO currently, the environment we store for a compound
                # statement is just the environment of the typedec above it, and
                # it has nothing to do with the typedecs in its statement lists,
                # since a compound statement could have more than one statement
                # list. in the future, it is planned for compound statements to
                # store an environment for each statement list representing the
                # type environment at the end of each statement list, and then
                # instead of embedding several copies of environments at each
                # statement making some kind of chain of references to
                # environments so that data isn't copied and reused all over the
                # place.
                
                stmt_lists = ASTInfo.get_stmt_lists(node)

                for stmt_list in stmt_lists:
                    _embed_environment_stmt_list(stmt_list, old_env)

                return old_env

            else:
                # simple and compound statements should form a disjoint sum of
                # all statements, so this should never be reached.
                assert(False)

        else:
            # according to the Python API, AST nodes are disjoint sums of
            # expressions, statements, and modules, so we should never reach
            # here.
            assert(False)

    @staticmethod
    def _embed_environment_stmt_list(stmts, old_env):
        """Recursive helper for _embed_environment to add environments to lists
        of statements. The list of statements to be processed is assumed to be
        consecutively ordered within one block (and consisting of the entire
        block), so we assume that the working environment of line n is the
        working environment of line n-1, plus any type declarations that may
        have been added in line n. We do not need to return or keep track of the
        environment at the end of the list of statements because we are assuming
        that C{stmts} is the entire contents of one block, so, once we're done
        with the block, we should no longer know or care about the type
        declarations from within the block.

        @returns: The environment at the end of the list of statements. This will
        only be used when processing the list of statements in a module to get a
        "master" environment for a file to use in debugging.
        """

        current_env = old_env

        for s in stmts:
            current_env = _embed_environment_node(s, current_env)

        return current_env


    ## This probably won't be necessary.
    ## def find_env(expr):
    ##     """This should only be called on an expression within an AST that has
    ##     already been propogated with environments. All statements will have
    ##     environments set as instance variables, but expressions will have to refer
    ##     to the environments of their parent statements. XXX This probably will be
    ##     redundant, because the environments of the parent statements will be
    ##     accessed and then typecheck will be called with those environments when the
    ##     children expressions are typechecked.
    ##     """

    ##     # this function is pointless to call on anything other than expressions.
    ##     assert(isinstance(expr, ast.expr))

    ##     # TODO implement if necessary




