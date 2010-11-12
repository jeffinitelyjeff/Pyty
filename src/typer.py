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
    @type env: C{dict} {C{str} : C{str}}.
    @param env: an environment mapping variable names to types.
    @rtype: C{str}.
    @return: the type of C{tree}.
    @raise UnsatisfactoryEnvironment: if the C{env} doesn't contain enough
        type information to determine the type of C{tree}.
    @raise DoesNotTypehcheck: if something doesn't typecheck within C{tree}.
    """

    # TODO: Implement function
    return true

def does_typecheck(tree, env):
    """Returns a boolean value for whether an AST C{tree} with environment
    C{env} typechecks properly. Abstracts away the errors thrown by typecheck().

    @type tree: an AST node.
    @param tree: an AST to typecheck.
    @type env: C{dict} {C{str} : C{str}}.
    @param env: an environment mapping variable names to types.
    @rtype: C{bool}.
    @return: whether C{tree} typechecks properly.
    """

    try:
        typecheck(tree, env)
    except UnsatisfactoryEnvironment, DoesNotTypecheck:
        return false
    else:
        return true

# MIGHT NOT WANT THIS; ABSTRACTING AWAY IN THIS SENSE COULD JUST MAKE MORE WORK,
# MIGHT AS WELL JUST USE THE ERROR INFORMATION.
def satisfactory_environment(tree, env):
    """Returns a boolean value for whether C{env} is a satisfactory
    environment for typechecking AST C{tree}. Abstracts away the errors thrown
    by typecheck().

    @type tree: an AST node.
    @param tree: an AST to typecheck.
    @type env: C{dict} {C{str} : C{str}}.
    @param env: an environment mapping variable names to types.
    @rtype: C{bool}.
    @return: whether C{env} is a satisfactory environment to typecheck C{tree}.
    """

    try:
        typecheck(tree, env)
    except UnsatisfactoryEnvironment:
        return false
    else:
        return true

def typecheck_and_update(tree, env):
    """Updates and returns env to include the type of AST C{tree}, assuming it
    typechecks properly.

    @type tree: an AST node.
    @param tree: an AST to typecheck.
    @type env: C{dict} {C{str} : C{str}}.
    @param env: an environment mapping variable names to types.
    @rtype: {str}.
    @retrun: the type of C{tree}.
    @raise UnsatisfactoryEnvironment: if the C{env} doesn't contain enough type
        information to determine the type of C{tree}.
    @raise DoesNotTypecheck: if something doesn't typecheck within C{tree}.
    """

    # TODO: implement
    # call typecheck and create an entry in env to store the type returned by
    # typecheck.
    # NOTE: this doesn't entirely make sense unless environments contain
    # information about every AST node and not just variables.
    return env
