# Singleton pattern adapted from http://code.activestate.com/recipes/52558/

class PytyType:
    # constructor just throws an error because this is an abstract class.
    def __init__(self):
        raise Exception("Don't instantiate a PytyType object!")

class BaseFloat(PytyType):
    class __impl(PytyType):
        """Implementation of BaseFloat class."""

        def __init__(self):
            pass

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """Create reference to singleton instance."""
        # Create and remember instance only if we don't already have one.
        if BaseFloat.__instance is None:
            BaseFloat.__instance = BaseFloat.__impl()

        # Store instance reference as the only member of the handle
        self.__dict__['_BaseFloat__instance'] = BaseFloat.__instance

class BaseInt(BaseFloat):
    class __impl(BaseFloat):
        """Implementation of BaseInt class."""
        pass

    __instance = None

    def __init__(self):
        """Create reference to singleton instance."""

        if BaseInt.__instance is None:
            BaseInt.__instance = BaseInt.__impl()

        self.__dict__['_BaseInt__instance'] = BaseInt.__instance
        
class BaseBool(PytyType):
    class __impl(PytyType):
        """Implementation of BaseBool class."""

        def __init__(self):
            pass

    __instance = None

    def __init__(self):
        """Create reference to singleton instance."""

        if BaseBool.__instance is None:
            BaseBool.__instance = BaseBool.__impl()

        self.__dict__['_BaseBool__instance'] = BaseBool.__instance


# These is_type methods abstract away the implementation of how types are
# specified in the typechecker. Right now they are specified with strings,
# but this should allow an interface such that they can easily be changed to
# objects or something else to implement disjoint sum types.

type_regex = r"^(int|float|bool)$"

def is_int(t):
    return t == "int"

def is_float(t):
    return t == "float"

def is_bool(t):
    return t == "bool"

def is_subt(t0, t1):
    return t0 == t1 or (t0 == "int" and t1 == "float")

int_type = "int"
float_type = "float"
bool_type = "bool"

