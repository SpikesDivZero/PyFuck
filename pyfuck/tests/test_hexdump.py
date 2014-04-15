""" Tests the hex dumper """
from __future__ import print_function

import unittest
from pyfuck.hexdump import HexDumper

# No need for these in tests!
# pylint: disable=locally-disabled, too-many-public-methods, no-self-use


class TestHexDumper(unittest.TestCase):
    """ Tests the hex dumper. """

    def test_format_line(self):
        """ Test that formatting a single line works. """
        inst = HexDumper(cols=16)

        assert inst.format_line(0x100, "12\n45") == \
            "0000100: 3132 0a34 35                            " + \
            " 12.45           "

        assert inst.format_line(0x200, "12\n456") == \
            "0000200: 3132 0a34 3536                          " + \
            " 12.456          "

        assert inst.format_line(0x300, "1245678901234567") == \
            "0000300: 3132 3435 3637 3839 3031 3233 3435 3637 " + \
            " 1245678901234567"

    def test_dump_string(self):
        """ Test the generic dump string method. """
        inval = "123456789\n123456" + "12\n45"
        out = \
            "0000000: 3132 3334 3536 3738 390a 3132 3334 3536 " + \
            " 123456789.123456\n" + \
            "0000010: 3132 0a34 35                            " + \
            " 12.45           \n"
        assert out == HexDumper(cols=16).dump_string(inval)
