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

from pyfuck.hexdump import HexDumper

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
    #pylint: disable=locally-disabled, too-many-instance-attributes

    COMMENT_RE = re.compile("/\\* .*? \\*/", re.X | re.M | re.S)

    def __init__(self, code, reader=sys.stdin.readline,
                 writer=sys.stdout.write, strict=False):
        # Code starts as a string, but compile() turns it into a list.
        self.code = code
        self.code_pos = 0

        self.stack = [0]
        self.stack_pos = 0

        self.loop_returns = []

        self.fn_read = reader
        self.fn_write = writer
        self.input_buffer = []

        # Should we be strict about over/under flows?
        self.strict = strict

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
            if not self.strict:
                return
            raise InterpreterError("Char overflow at %d" % self.stack_pos)
        self.stack[self.stack_pos] += 1

    def do_decr(self):
        """ Implements the - operator. """
        if self.stack[self.stack_pos] <= 0:
            if not self.strict:
                return
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
        dumper = HexDumper()
        ewrite = sys.stderr.write
        ewrite("Code Position: %04x\n" % self.code_pos)
        ewrite("Stack Position: %04x\n" % self.stack_pos)
        ewrite("Stack:\n")
        stack_bin = "".join([chr(x) for x in self.stack])
        ewrite(dumper.dump_string(stack_bin))

    def find_loop_ending(self, start):
        """ Find the end of this begin loop marker.

        Used by do_loop_begin.

        A possible future improvement is to cache where the loops start
        and end, respectively. Although, this may prove useless if we
        go with a tokenizing approach.
        """
        if self.code[start] != '[':
            raise InterpreterError("find_loop_ending(%d) is %s not [" % (
                start, self.code[start]))

        # Here comes the grody part. We need to correctly match our
        # start and end positions -- if someone asks about the ending
        # of start0, we must return end0, not end1.
        #   [  xxx  [  xxx  ]  xxx  ]
        #   ^       ^       ^       ^
        # start0  start1  end1    end0
        pos = start
        depth = 1

        while True:
            pos += 1
            if self.code[pos] == '[':
                depth += 1
                continue
            if self.code[pos] != ']':
                continue

            depth -= 1
            if depth == 0:
                return pos

    def do_loop_begin(self):
        """ Begin loop marker.

        If the value on the stack is 0, then we skip to the end of the
        loop we were about to begin.

        Otherwise, we push our position on to the loop positions so we
        remember where to return to later.
        """
        # Check if we need to enter this loop at all.
        if self.stack[self.stack_pos] == 0:
            self.code_pos = self.find_loop_ending(self.code_pos) + 1
            return

        # Okay, we need to enter it. Save where this loop began.
        self.loop_returns.append(self.code_pos)
        self.code_pos += 1

    def do_loop_end(self):
        """ End loop marker.

        Remove the last-loop-start pointer from the loop stack.

        If the value on the stack is 0, then we discard the return
        position and skip to the next instruction. (No need to return
        if it's just going to jump forwards anyways!)

        Otherwise, we change our EIP to the last-loop-start + 1. (We
        already tested the value, so no need to do the begin again.)
        """
        return_pos = self.loop_returns[-1]

        if self.stack[self.stack_pos] == 0:
            self.loop_returns.pop()
            self.code_pos += 1
            return

        self.code_pos = return_pos + 1

    def run(self):
        """ Run the program. """
        dispatch = {
            '+': self.do_incr,
            '-': self.do_decr,
            '.': self.do_write,
            ',': self.do_read,
            '<': self.do_stack_left,
            '>': self.do_stack_right,
            '#': self.do_show_debug,
            '[': self.do_loop_begin,
            ']': self.do_loop_end,
        }

        self.code_pos = 0
        while self.code_pos < len(self.code):
            opcode = self.code[self.code_pos]
            if opcode not in dispatch:
                self.code_pos += 1
                continue

            dispatch[opcode]()

            # We don't manipulate the code_pos for the two loop markers,
            # as they alter this themselves.
            if opcode not in "[]":
                self.code_pos += 1
