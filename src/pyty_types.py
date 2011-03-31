import re

class PytyType:
    paren_regex = r"^\((.*)\)$"
    list_regex = r"^list of (.*)$"
    pair_regex = r"^(.*)\*(.*)$"

    @staticmethod
    def valid(s):
        if s == "int" or \
           s == "float" or \
           s == "bool":
            return True

        m0 = re.match(PytyType.paren_regex, s)
        if m0:
            return PytyType.valid(m0.groups()[0])

        m1 = re.match(PytyType.list_regex, s)
        if m1:
            return PytyType.valid(m1.groups()[0])

        m2 = re.match(PytyType.pair_regex, s)
        if m2:
            return PytyType.valid(m2.groups()[0].strip()) and \
                   PytyType.valid(m2.groups()[1].strip())

        # reaching here means nothing matched, so it's a fail.
        return False

    @staticmethod
    def get_t(s):
        if s == "int" or \
           s == "float" or \
           s == "bool":
            return s

        m0 = re.match(PytyType.paren_regex, s)
        if m0:
            return PytyType(m0.groups()[0]).t

        m1 = re.match(PytyType.list_regex, s)
        if m1:
            return "list"

        m2 = re.match(PytyType.pair_regex, s)
        if m2:
            return "pair"

        # should only call get_t on valid strings; should never reach here.
        assert(False)

    @staticmethod
    def get_members(s):
        if s == "int" or \
           s == "float" or \
           s == "bool":
            return None

        m0 = re.match(PytyType.paren_regex, s)
        if m0:
            return PytyType(m0.groups()[0]).members

        m1 = re.match(PytyType.list_regex, s)
        if m1:
            return (PytyType(m1.groups()[0]),)

        m2 = re.match(PytyType.pair_regex, s)
        if m2:
            return (PytyType(m2.groups()[0].strip()),
                    PytyType(m2.groups()[1].strip()))

        # Should only call get_members on valid strings; should never reach here.
        assert(False)
                    
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


