class UnsatisfactoryEnvironment(Exception):
    """Exception subclass which contains data specific to an environment which
    was found to be unsatisfactory in determining whether an AST typechecks
    properly.
    
    @type env: an environment, specifically C{dict} {C{str} : C{str}}.
    @ivar env: the environment found to be unsatisfactory in typechecking.
    @type req_types: C{list} [C{str}].
    @ivar req_types: a list of variable names which must have types in order for
        the AST to be properly typechecked.
    """

    def __init__(self, env, req_types): 
        self.env = env
        self.req_types = req_types

    def __str__(self):
        return "Unsatisfactory Environment:\n" + repr(self.env) + "\n\n \
                Required Types:\n" + repr(self.req_types)

def typecheck(tree, env):
    """Determines if an AST C{tree} typechecks with environment C{env}. Throws
    an UnsatisfactoryEnvironment exception if the C{env} doesn't contain enough
    type information to typecheck C{tree}.

    @type tree: an AST node.
    @param tree: an AST to typecheck.
    @type env: C{dict} {C{str} : C{str}}.
    @param env: an environment mapping variable names to types.
    """

    # TODO: Implement function
    return true

