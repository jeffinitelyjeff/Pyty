import re

class PytyType:
    type_grammar = ("BaseType", "ParenType", "ListType", "TupleType")

    @staticmethod
    def valid(s):
        for t in PytyType.type_grammar:
            c = eval("PytyType._" + t + "Parser")

            m = c.match(s)
            if m:
                return c.valid(s, m)

        # reaching here means nothing matched, so it's a fail.
        return False

    @staticmethod
    def get_t(s):
        for t in PytyType.type_grammar:
            c = eval("PytyType._" + t + "Parser")

            m = c.match(s)
            if m:
                return c.get_t(s, m)

        # should only call get_t on valid strings; should never reach here.
        assert(False)

    @staticmethod
    def get_members(s):
        for t in PytyType.type_grammar:
            c = eval("PytyType._" + t + "Parser")

            m = c.match(s)
            if m:
                return c.get_members(s, m)

        # should only call get_members on valid strings; should never reach
        # here.
        assert(False)

    class _BaseTypeParser:
        regex = r"^int|float|bool$"

        @staticmethod
        def match(s):
            return re.match(PytyType._BaseTypeParser.regex, s)

        @staticmethod
        def valid(s, m):
            return True

        @staticmethod
        def get_t(s, m):
            return s

        @staticmethod
        def get_members(s, m):
            return None

    class _ParenTypeParser:
        regex = r"^\((.*)\)$"

        @staticmethod
        def match(s):
            return re.match(PytyType._ParenTypeParser.regex, s)
        
        @staticmethod
        def valid(s, m):
            return PytyType.valid(m.groups()[0])

        @staticmethod
        def get_t(s, m):
            return PytyType(m.groups()[0]).t

        @staticmethod
        def get_members(s, m):
            return PytyType(m.groups()[0]).members

    class _ListTypeParser:
        regex = r"^list of (.*)$"

        @staticmethod
        def match(s):
            return re.match(PytyType._ListTypeParser.regex, s)

        @staticmethod
        def valid(s, m):
            return PytyType.valid(m.groups()[0])

        @staticmethod
        def get_t(s, m):
            return "list"

        @staticmethod
        def get_members(s, m):
            return PytyType(m.groups()[0])

    class _TupleTypeParser:
        regex = r"^((.*)\*)*(.*)$"

        @staticmethod
        def match(s):
            if re.match(PytyType._TupleTypeParser.regex, s):
                # XXX major caveat: this does not allow tuples of tuples, since
                # we're just counting the raw # of *'s
                num_items = s.count("*") + 1
                g_regex = r"^" + r"(.*)\*" * (self.num_items - 1) + \
                          r"(.*)$"
                return re.match(g_regex, s)
            else:
                return None

        @staticmethod
        def valid(s, m):
            for sub_t in m.groups():
                if not PytyType.valid(sub_t): return False
            return True

        @staticmethod
        def get_t(s, m):
            return "tuple"

        @staticmethod
        def get_members(s, m):
            return tuple(PytyType(sub_t) for sub_t in m.groups())
            
    @staticmethod
    def kill_none_spots(tup):
        return tuple([t for t in tup if t is not None])

    def __init__(self, spec):
        if PytyType.valid(spec):
            self.t = PytyType.get_t(spec)
            self.members = PytyType.get_members(spec)
        else:
            raise Exception("Invalid Pyty Type specification!")

        """
        if PytyType.valid_type_string(spec):
            self.main_t = spec

            m = re.match(PytyType.type_regex, spec)

            self.members = []
            
            g = PytyType.kill_none_spots(m.groups())

            for i in range(0, len(g)):
                self.members.append(PytyType(g[i].strip()))
        else:
            raise Exception("Invalid Pyty Type specification.")
            """

    def is_base_type(self):
        return self.members is None

    def __eq__(self, other):
        return self.t == other.t and self.members == other.members

    def __repr__(self):
        if self.is_base_type():
            return self.t
        else:
            return self.t + ": " + str(self.members)

    def is_int(self):
        return self.t == "int"
    
    def is_float(self):
        return self.t == "float"

    def is_bool(self):
        return self.t == "bool"

    def is_subtype(self, other):
            
        return self.t == other.t or (self.is_int() and other.is_float())

        # XXX include more complicated rules for collection and function types

class PytyTypes:
    int_t = PytyType('int')
    float_t = PytyType('float')
    bool_t = PytyType('bool')


