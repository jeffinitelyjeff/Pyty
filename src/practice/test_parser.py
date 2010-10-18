from epydoc.docparser import parse_docs

doc = parse_docs(filename="test.py")

types = set(["int", "bool"])


docstrings = {}
for variable in doc.variables:
    docstrings[variable] = doc.variables[variable].value.docstring

typedefs = {}
for function in docstrings:
    docstring_lines = docstrings[function].split("\n")
    for docstring_line in docstring_lines:
        if docstring_line.find("@type") != -1:
            # add error checking in case types aren't specified correctly
            spec_type = docstring_line.split(": ")[1]
            var_name = docstring_line.split(":")[0].split("type ")[1]

            if spec_type in types:
                typedefs[var_name] = spec_type

print typedefs
