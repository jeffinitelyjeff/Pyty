class TypeIncorrectlySpecifiedError(Exception):
    pass

class TypeUnspecifiedError(Exception):
    def __init__(self, msg = None, var = None):
        super(TypeUnspecifiedError, self).__init__(msg)
        self.var = var
