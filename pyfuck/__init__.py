""" PyFuck: A Python Brainfuck interpreter.

I'm writing this with the expectation that I will add two features
not commonly found in a Brainfuck interpreter.

(0) Debugging. Some other interpreters implement this, but I'd like to
implement a xxd-style output, which may be a bit more useful. To conform
with other existing Brainfuck interpreters, we'll use the number sign.

(1) Comments. In order to better document Brainfuck code, it'd be nice
if it actually supported comments. Since the number sign is already used
in other interpreters, I'll implement C-sytle comments.
"""

# To silence the linter.
from __future__ import print_function

import re
import sys

# Py3 compat: raw_input was renamed to just input, but input is NOT
# safe in Py2 -- input was effectively eval(raw_input()).
try:
    # pylint: disable=locally-disabled, undefined-variable
    PY_INPUT = raw_input
except NameError:
    PY_INPUT = input


class InterpreterError(Exception):
    """ An generic error in the PyFuck Interpreter. """
    pass


class PyFucker(object):
    """ A Brainfuck interpreter instance. """
    COMMENT_RE = re.compile("/\\* .*? \\*/", re.X | re.M | re.S)

    def __init__(self, code, reader=sys.stdin.readline,
                 writer=sys.stdout.write):
        # Code starts as a string, but compile() turns it into a list.
        self.code = code
        self.code_pos = 0

        self.stack = [0]
        self.stack_pos = 0
        self.fn_read = reader
        self.fn_write = writer
        self.input_buffer = []

        self.compile()

    def compile(self):
        """ Doesn't actually compile anything yet, but it will!

        For now, we'll use the compile stage to do our compile-like
        cleanups.
        """
        # Strip out comments from our code.
        self.code = re.sub(self.COMMENT_RE, "", self.code)

        # For now, just do a quick sanity check.
        if self.code.count('[') != self.code.count(']'):
            raise InterpreterError("Number of loop start/end doesn't match")

        self.code = list(self.code)

    def do_incr(self):
        """ Implements the + operator. """
        if self.stack[self.stack_pos] >= 255:
            raise InterpreterError("Char overflow at %d" % self.stack_pos)
        self.stack[self.stack_pos] += 1

    def do_decr(self):
        """ Implements the - operator. """
        if self.stack[self.stack_pos] <= 0:
            raise InterpreterError("Char underflow at %d" % self.stack_pos)
        self.stack[self.stack_pos] -= 1

    def do_write(self):
        """ Implements the . operator. """
        self.fn_write(chr(self.stack[self.stack_pos]))

    def do_read(self):
        """ Implements the , operator, using it's own buffer.

        This doesn't yet handle errors.
        """
        # Do we have data in our buffer? If not, read in a line of text.
        if len(self.input_buffer) == 0:
            self.input_buffer = list(self.fn_read())

        self.stack[self.stack_pos] = ord(self.input_buffer.pop(0))

    def do_stack_left(self):
        """ Move the stack pointer to the left.

        If this puts us at -1, grow the stack to the left and set our
        pointer back to 0.
        """
        if self.stack_pos == 0:
            self.stack.insert(0, 0)
        else:
            self.stack_pos -= 1

    def do_stack_right(self):
        """ Move the stack pointer to the right.

        If this puts us past our boundry, grow the stack to the right.
        """
        self.stack_pos += 1
        if self.stack_pos == len(self.stack):
            self.stack.append(0)

    def do_show_debug(self):
        """ Show debugging information.

        This will do something awesome, but for now, let's get something.
        """
        sys.stderr.write("Stack Position: %d\n" % self.stack_pos)
        sys.stderr.write("Stack: %s\n" % repr(self.stack))

    def run(self):
        """ Run the program?

        This doesn't yet handle loops.
        """
        dispatch = {
            '+': self.do_incr,
            '-': self.do_decr,
            '.': self.do_write,
            ',': self.do_read,
            '<': self.do_stack_left,
            '>': self.do_stack_right,
            '#': self.do_show_debug,
        }

        self.code_pos = 0
        while self.code_pos < len(self.code):
            opcode = self.code[self.code_pos]
            if opcode in dispatch:
                dispatch[opcode]()
                self.code_pos += 1

            elif opcode == '[':
                raise NotImplementedError("LOOP BEGIN")

            elif opcode == ']':
                raise NotImplementedError("LOOP END")
