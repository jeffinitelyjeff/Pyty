import re

class PytyType:
    type_regex = r"^(int|float|bool|list of (.*))$"

    @staticmethod
    def valid_type_string(spec):
        m = re.match(PytyType.type_regex, spec)

        if not m:
            return False
        else:
            if m.groups()[1] is None:
                return True
            else:
                return PytyType.valid_type_string(m.groups()[1])

    def __init__(self, spec):
        if re.match(PytyType.type_regex, spec):
            self.t = spec

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


