class TypeIncorrectlySpecifiedError(Exception):
    pass

class TypeUnspecifiedError(Exception):
    def __init__(self, msg=None, var=None):
        super(TypeUnspecifiedError, self).__init__(msg)
        self.var = var

""" oops I don't think this helps at all
class ASTTraversalError(Exception):
    def __init__(self, msg=None, missing_field=None, treated_as=None,
                 node=None):
        self.msg = msg
        self.missing_field = field
        self.treated_as = treated
        self.node = node
"""

