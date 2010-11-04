# This class is mostly being written now as a skeleton of what it should do 

class UnsatisfactoryEnvironment(Exception):
    """Exception subclass which contains data specific to an environment which
    was found to be unsatisfactory in determining whether an AST typechecks
    properly.
    
    @type env: an environment, specifically C{dict} {C{str} : C{str}}.
    @ivar env: the environment found to be unsatisfactory in typechecking.
    @type req_types: C{str}.
    @ivar req_type: the variable with missing type information that was
        necessary in order to typecheck.
    """

    def __init__(self, env, req_type): 
        self.env = env
        self.req_type = req_type

    def __str__(self):
        return "%s:\n%r\n\n%s\n%r" % ("Unsatisfactory Environment", self.env,
            "Required Type", self.req_type)

class DoesNotTypecheck(Exception):
    """Exception subclass which contains data specific to an AST which does
    not typecheck properly.

    @type tree: an AST node.
    @ivar tree: the AST which does not typecheck.
    @type node: an AST node.
    @ivar node: the AST node in C{tree} which does not typecheck.
    @type node_env: an environment, specifically C{dict} {C{str] : C{str}}
    @ivar node_env: the environment at c{node}.
    """

    def __init__(self, tree, node, node_env):
        self.tree = tree
        self.node = node
        self.node_env = node_env

    def __str__(self):
        return "%s:\n%r\n\n%s\n%r\n\n%s\n%r" % ("Full Tree", self.tree, "Error
            Tree", self.node, "Environment of Error Tree", self.node_env)


def typecheck(tree, env):
    """Returns the type of an AST C{tree} with environment C{env}, assuming it
    typechecks properly.

    @type tree: an AST node.
    @param tree: an AST to typecheck.
    @type env: c{dict} {C{str} : C{str]].
    @param env: an environment mapping variable names to types.
    @rtype: {str}.
    @return: the type of C{tree}.
    @raise UnsatisfactoryEnvironment: if the C{env} doesn't contain enough
        type information to determine the type of C{tree}.
    @raise DoesNotTypehcheck: if something doesn't typecheck within C{tree}.
    """

    # TODO: Implement function
    return true

