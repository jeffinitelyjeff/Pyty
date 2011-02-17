# Singleton pattern adapted from http://code.activestate.com/recipes/52558/

class PytyType:
    # constructor just throws an error because this is an abstract class.
    def __init__(self):
        raise Exception("Don't instantiate a PytyType object!")

class BaseFloat(PytyType):
    class __impl(PytyType):
        """Implementation of BaseFloat class."""
        pass

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """Create reference to singleton instance."""
        # Create and remember instance only if we don't already have one.
        if BaseFloat.__instance is None:
            BaseFloat.__instance = BaseFloat.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_BaseFloat__instance'] = BaseFloat.__instance

class BaseInt(BaseFloat):
     class __impl(BaseFloat):
        """Implementation of BaseInt class."""
        pass

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """Create reference to singleton instance."""
        # Create and remember instance only if we don't already have one.
        if BaseInt.__instance is None:
            BaseInt.__instance = BaseInt.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_BaseInt__instance'] = BaseInt.__instance

class BaseBool(PytyType):
     class __impl:
        """Implementation of BaseBool class."""
        pass

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """Create reference to singleton instance."""
        # Create and remember instance only if we don't already have one.
        if BaseBool.__instance is None:
            BaseBool.__instance = BaseBool.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_BaseBool__instance'] = BaseBool.__instance
