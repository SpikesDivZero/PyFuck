""" CLI code for pyfuck """

# To silence the linter.
from __future__ import print_function

import sys
from pyfuck import PyFucker


def main():
    """ For now, we're just adding a really trivial runner. """
    if len(sys.argv) != 2:
        print("Usage: %s <script>\n" % sys.argv[0])
        sys.exit(1)

    script = sys.argv[1]
    with open(script, 'r') as fh_script:
        code = fh_script.read()

    inst = PyFucker(code)
    inst.run()

if __name__ == '__main__':
    main()
