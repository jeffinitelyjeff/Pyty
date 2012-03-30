spec mode: mod

----pass----

---
# Danner COMP211 - Lab 2 sample code
# This sample code shows basic procedural concepts in Python.
# It asks the user for his/her age, then compares it to Mozart's
# at his death.

import sys

#: sys.argv : [str]
#: len: [str] -> int
#: raw_input: str -> str
#: int: str -> int
#: str: int -> str

if len(sys.argv) == 1:
		age = int(raw_input("Enter your age: "))
else:
		age = int(sys.argv[1])

if age > 35:
		print "When Mozart was your age, he'd been dead for " + str(age-35) + " years!"
else:
		print "If you were Mozart, you would have " + str(35-age) + " years to live."
---

---
# Danner COMP211 - Lab 3 sample code
# This program asks the user to enter a year, then determines whether that year
# is a leap year. The user may enter anotnher year or quit.

import sys

#: raw_input: str -> str
#: int: str -> int
#: str: int -> str

#: main: [str] -> unit
def main(argv):
		# Should we ask for another year?
    #: keep_going : bool
		keep_going = True

		while keep_going:
        #: year : int
				year = int(raw_input("Please enter a year: "))

				# is_leap will be true if and only if year is a leap year.
        #: is_leap : bool
				if year%4 != 0: is_leap = False
				else:
						if year%400 == 0: is_leap = True
						elif year%100 == 0: is_leap = False
						else: is_leap = True

				if is_leap: print str(year) + " is a leap year."
				else: print str(year) + " is not a leap year."

				# Ask whether to keep going and require either "Y" or "N".
        #: ask_again : bool
        #: response : str
				ask_again = True
				while ask_again:
						response = raw_input("Keep going (Y/N)? ")
						ask_again = (response != 'Y' and response != 'N')

				keep_going = (response == 'Y')

#: __name__ : str
#: sys.argv : [str]

if __name__ == '__main__':
		main(sys.argv)
---

---
# Danner COMP211 - Lab 4 sample code
# Practice with Python functions.

#: sqrt: (float, float) -> float
def sqrt(x, err):
    """
    Compute the square-root up to a given error tolerance.  The
    square-root is calculated using Netwon's method with a starting
    approximation of 1.0.  Here are some sample computations:

        >>> sqrt(2, .01)
        1.4142156862745099
        >>> sqrt(2, .001)
        1.4142135623746899

    @type x: float
    @param x: the value for which to compute the square root.  Must have
        x >= 0.
    @type err: float
    @param err: the error tolerance for the result.

    @rtype:  float
    @return:  A value y such that |y^2 - x| < err
    """

    #: y : float
    y = 1.0

    #: diff : float
    diff = err

    #: new_y : float
    while diff >= err:
        new_y = y - (y*y - x)/(2*y)
        diff = abs(new_y - y)
        y = new_y

    return y

#: __name__ : str
#: doctest.testmod: unit -> unit
if __name__ == '__main__':
    import doctest
    doctest.testmod()
