class PytyError(Exception):
    pass

class TypeIncorrectlySpecifiedError(PytyError):
    pass

class TypeMultiSpecifiedError(PytyError):
    pass

class TypeUnspecifiedError(PytyError):
    def __init__(self, msg=None, var=None, env=None):
        super(TypeUnspecifiedError, self).__init__(msg)
        self.var = var
        self.env = env

    def __str__(self):
        return "Variable %s has unspecified type in env: %s" % (self.var, self.env)

class ASTTraversalError(PytyError):
    def __init__(self, msg=None, missing_field=None, treated_as=None,
                 node=None):
        self.msg = msg
        self.missing_field = field
        self.treated_as = treated
        self.node = node

