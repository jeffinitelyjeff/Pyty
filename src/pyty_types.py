import re

class PytyType:
    type_regex = r"^(int|float|bool)$"
    
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

    
int_type = PytyType('int')
float_type = PytyType('float')
bool_type = PytyType('bool')

