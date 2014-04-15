""" Facilitate dumping chars in hex.

$ cat /dev/urandom |xxd |head -3
0000000: e8a6 8c2b 8511 da71 7b56 250c 5441 8c38  ...+...q{V%.TA.8
0000010: e999 0895 d539 0a49 698c 82e8 bd62 ea6f  .....9.Ii....b.o
0000020: 0d43 20ad 370b 96d7 d1c7 146b 2743 d691  .C .7......k'C..
"""

from __future__ import print_function


class HexDumper(object):
    """ Facilitates dumping data in hex, like xxd. """
    def __init__(self, cols=16):
        self.cols = cols

    def format_line(self, position, data):
        """ Format a line for printing. """
        assert len(data)
        assert len(data) <= self.cols

        hex_text = ""
        text = ""

        for i in range(len(data)):
            char = data[i]
            byte = ord(char)

            # If the char is non-printable, replace it with a .
            if byte <= 31 or byte >= 127:
                char = "."
            text += char

            hex_text += "%02x" % byte
            if i % 2 == 1:
                hex_text += " "

        # Pad it out.
        for i in range(len(data), self.cols):
            text += " "
            hex_text += "  "
            if i % 2 == 1:
                hex_text += " "

        return "%07x: %s %s" % (position, hex_text, text)

    def dump_string(self, data):
        """ Dump the data into a string. """
        out = ""
        for start in range(0, len(data), 16):
            line = data[start:start+16]
            out += self.format_line(start, line) + "\n"
        return out

    def dump(self, data):
        """ Do the dumping! """
        print(self.dump_string(data))
