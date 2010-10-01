"""
This program is to test the epydoc epytext parser.
"""

def test_function_1(a, b):
    """Prints a * b.

    @type a: int
    @arg a: An integer.

    @type b: int
    @arg b: An integer.
    """

    print(a * b)


def test_function_2(c, d):
    """Doesn't do anything.

    @type c: bool
    @arg c: A boolean value.
    
    @type d: bool
    @arg d: A boolean value.
    """

    return
