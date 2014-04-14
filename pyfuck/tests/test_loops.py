""" Tests the basic ops: + - < > . , """
import unittest
from pyfuck import PyFucker, InterpreterError

# No need for these in tests!
# pylint: disable=locally-disabled, too-many-public-methods, no-self-use


class TestLoops(unittest.TestCase):
    """ Tests the basic ops. """

    def find_loop_endings(self):
        """ Loop ending discovery is correct. """
        #                01234567890123456789
        inst = PyFucker("[x[x[x[x[x]x]x]x]x]")

        # Quickly ensure that finding the ending of a non-loop dies.
        with self.assertRaises(InterpreterError):
            inst.find_loop_ending(1)

        assert inst.find_loop_ending(0) == 18
        assert inst.find_loop_ending(4) == 14

    def test_multiplication(self):
        """ Multiplication (5 * 4 = 20 and 2 * 2 * 5 = 20) """
        inst = PyFucker("+++++[->++++<]")
        inst.run()
        assert inst.stack == [0, 20]
        assert inst.stack_pos == 0

        inst = PyFucker("++[->++[->+++++<]<]")
        inst.run()
        assert inst.stack == [0, 0, 20]
        assert inst.stack_pos == 0

    def test_zero_jump(self):
        """ while(false) """
        inst = PyFucker("[++++]++")
        inst.run()
        assert inst.stack == [2]
        assert inst.stack_pos == 0
