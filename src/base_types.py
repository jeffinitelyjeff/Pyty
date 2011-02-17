# Singleton pattern adapted from http://code.activestate.com/recipes/52558/
class PytyType(object):
    class __impl:
        """Implementation of pyty class."""
        pass

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """Create reference to singleton instance."""
        # Create and remember instance only if we don't already have one.
        if PytyType.__instance is None:
            PytyType.__instance = PytyType.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_PytyType__instance'] = PytyType.__instance

class BaseFloat(PytyType):
    pass

class BaseInt(BaseFloat):
    pass

class BaseBool(PytyType):
    pass

# the strings in this list must be defined as the names of the defined
# classes, but without Base- and decapitalized.
base_types_list = ["float", "int", "bool"]
