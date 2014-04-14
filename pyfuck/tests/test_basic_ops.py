""" Tests the basic ops: + - < > . , """
import unittest
from pyfuck import PyFucker, InterpreterError

# No need for these in tests!
# pylint: disable=locally-disabled, too-many-public-methods, no-self-use


class TestBasicOps(unittest.TestCase):
    """ Tests the basic ops. """

    def test_initial_state(self):
        """ Verify our expected initial state.

        If this breaks, all of our tests will break.
        """
        inst = PyFucker("")
        assert inst.stack == [0]
        assert inst.stack_pos == 0
        assert inst.input_buffer == []

    def test_incr(self):
        """ Basic incrememtation. """
        inst = PyFucker("")
        inst.stack[inst.stack_pos] = 254
        inst.do_incr()
        assert inst.stack == [255]
        assert inst.stack_pos == 0
        with self.assertRaises(InterpreterError):
            inst.do_incr()
        assert inst.stack == [255]
        assert inst.stack_pos == 0

    def test_decr(self):
        """ Basic decrementation. """
        inst = PyFucker("")
        inst.stack[inst.stack_pos] = 1
        inst.do_decr()
        assert inst.stack == [0]
        assert inst.stack_pos == 0
        with self.assertRaises(InterpreterError):
            inst.do_decr()
        assert inst.stack == [0]
        assert inst.stack_pos == 0

    def test_write(self):
        """ Writing. """
        def writer(val):
            """ Test writer. """
            assert val == "A"
        inst = PyFucker("", writer=writer)
        inst.stack[inst.stack_pos] = ord("A")
        inst.do_write()

    def test_read(self):
        """ Reading. """

        class FakeReader(object):
            """ Our fake reader! """
            def __init__(self):
                self.ctr = 0

            def counter(self):
                """ How many times was readline called? """
                return self.ctr

            def readline(self):
                """ Test reader. """
                self.ctr += 1
                return "Hello!\n"

        reader = FakeReader()
        inst = PyFucker("", reader=reader.readline)

        inst.do_read()
        assert reader.counter() == 1
        assert inst.stack == [ord("H")]
        assert inst.stack_pos == 0
        assert inst.input_buffer == list("ello!\n")

        inst.do_read()
        assert reader.counter() == 1
        assert inst.stack == [ord("e")]
        assert inst.stack_pos == 0
        assert inst.input_buffer == list("llo!\n")

    def test_stack_left(self):
        """ Shfiting stack to the left. """
        inst = PyFucker("")

        # First, check for underflow (auto-prepending)
        inst.stack = [1]
        inst.stack_pos = 0
        inst.do_stack_left()
        assert inst.stack == [0, 1]
        assert inst.stack_pos == 0

        inst.stack = [1, 2]
        inst.stack_pos = 1
        inst.do_stack_left()
        assert inst.stack == [1, 2]
        assert inst.stack_pos == 0

    def test_stack_right(self):
        """ Shfiting stack to the right. """
        inst = PyFucker("")

        # First, check for overflow (auto-appending)
        inst.stack = [1]
        inst.stack_pos = 0
        inst.do_stack_right()
        assert inst.stack == [1, 0]
        assert inst.stack_pos == 1

        inst.stack = [1, 2]
        inst.stack_pos = 0
        inst.do_stack_right()
        assert inst.stack == [1, 2]
        assert inst.stack_pos == 1


class TestCompile(unittest.TestCase):
    """ Tests the compiler steps. """

    def test_strip_comments(self):
        """ Comments should be stripped sanely. """
        # Single line comment
        inst = PyFucker("foo /* wat * wat */ bar")
        assert inst.code == list("foo  bar")

        # Multi-line comment
        inst = PyFucker("foo \n /* wat \n wat \n wat */ \n bar")
        assert inst.code == list("foo \n  \n bar")

        # Multiple comments (not-greedy!)
        inst = PyFucker("foo /* stuff */ bar /* boom */ baz")
        assert inst.code == list("foo  bar  baz")

    def test_loop_brace_match(self):
        """ Verify that bracing counts match. """
        # Simple match.
        PyFucker("foo [ bar ] baz")

        # Comments are removed first
        PyFucker("foo [ /* ] */ ] bar")


class TestSimpleRun(unittest.TestCase):
    """ Simple run test.

    Not exhaustive by any means, just gives us an idea that
    things are on track.
    """

    def test_hello(self):
        """ A simple hello printer! """

        class FakeWriter(object):
            """ A fake writer. """
            def __init__(self):
                self.buffer = ""

            def output(self):
                """ Get the output buffer. """
                return self.buffer

            def write(self, val):
                """ Append to the buffer. """
                self.buffer += val

        # Generate our code and expected stack.
        code = ""
        expected_stack = []
        for letter in list("Hello!\n"):
            expected_stack.append(ord(letter))
            code += "+" * ord(letter)
            code += ".>"
        expected_stack.append(0)

        writer = FakeWriter()

        inst = PyFucker(code, writer=writer.write)
        inst.run()

        assert writer.output() == "Hello!\n"
        assert inst.code_pos == len(code)
        assert inst.stack == expected_stack
        assert inst.stack_pos == 7
