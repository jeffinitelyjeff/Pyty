class PytyError(Exception):
    pass

class TypeIncorrectlySpecifiedError(PytyError):
    pass

class TypeUnspecifiedError(PytyError):
    def __init__(self, msg=None, var=None):
        super(TypeUnspecifiedError, self).__init__(msg)
        self.var = var

class ASTTraversalError(PytyError):
    def __init__(self, msg=None, missing_field=None, treated_as=None,
                 node=None):
        self.msg = msg
        self.missing_field = field
        self.treated_as = treated
        self.node = node

