import re

class PytyType:
    type_regex = r"^((int)|(float)|(bool)|(list of (.*)))$"

    @staticmethod
    def valid_type_string(spec):
        m = re.match(PytyType.type_regex, spec)

        if not m:
            return False
        else:
            if m.groups()[5] is None:
                return True
            else:
                return PytyType.valid_type_string(m.groups()[5])

    @staticmethod
    def kill_none_spots(tup):
        return tuple([t for t in tup if t is not None])

    def __init__(self, spec):
        if PytyType.valid_type_string(spec):
            self.t = spec

            m = re.match(PytyType.type_regex, spec)

            self.main_t = m.groups()[1]
            
            g = PytyType.kill_none_spots(m.groups())

            if len(g) > 2:
                for i in range(1, len(g)):
                    setattr(self, 'member_' + str(i), PytyType(g[i]))

    def __repr__(self):
        return self.t

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


