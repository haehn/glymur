# -*- coding:  utf-8 -*-
"""Test suite for jp2dump console script.
"""
import os
import re
import struct
import sys
import tempfile
import warnings
import unittest

if sys.hexversion < 0x03000000:
    from StringIO import StringIO
else:
    from io import StringIO

if sys.hexversion <= 0x03030000:
    from mock import patch
else:
    from unittest.mock import patch

import lxml.etree as ET

import glymur
from glymur import command_line


class TestJp2dump(unittest.TestCase):
    """Tests for verifying how jp2dump console script works."""
    def setUp(self):
        self.jpxfile = glymur.data.jpxfile()
        self.jp2file = glymur.data.nemo()
        self.j2kfile = glymur.data.goodstuff()

        # Reset printoptions for every test.
        glymur.set_printoptions(short=False, xml=True, codestream=True)

    def tearDown(self):
        pass

    def test_default_nemo(self):
        """Should be able to dump a JP2 file's metadata."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            sys.argv = ['', self.jp2file]
            command_line.main()
            actual = fake_out.getvalue().strip()
            # Remove the file line, as that is filesystem-dependent.
            lines = actual.split('\n')
            actual = '\n'.join(lines[1:])

        self.fail('Finish the test.')

    def test_codestream_0(self):
        """Verify dumping with -c 0, supressing all codestream details."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            sys.argv = ['', '-c', '0', self.jp2file]
            command_line.main()
            actual = fake_out.getvalue().strip()
            # Remove the file line, as that is filesystem-dependent.
            lines = actual.split('\n')
            actual = '\n'.join(lines[1:])

        self.fail('Finish the test.')

    def test_codestream_1(self):
        """Verify dumping with -c 1, printing headers."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            sys.argv = ['', '-c', '1', self.jp2file]
            command_line.main()
            actual = fake_out.getvalue().strip()
            # Remove the file line, as that is filesystem-dependent.
            lines = actual.split('\n')
            actual = '\n'.join(lines[1:])

        self.fail('Finish the test.')

    def test_codestream_2(self):
        """Verify dumping with -c 2, full details."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            sys.argv = ['', '-c', '2', self.jp2file]
            command_line.main()
            actual = fake_out.getvalue().strip()
            # Remove the file line, as that is filesystem-dependent.
            lines = actual.split('\n')
            actual = '\n'.join(lines[1:])

        self.fail('Finish the test.')

    def test_codestream_invalid(self):
        """Verify dumping with -c 3, not allowd."""
        self.fail('Finish the test.')
        with self.assertRaises(ValueError):
            sys.argv = ['', '-c', '3', self.jp2file]
            command_line.main()

    def test_short(self):
        """Verify dumping with -s, short option."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            sys.argv = ['', '-s', self.jp2file]
            command_line.main()
            actual = fake_out.getvalue().strip()
            # Remove the file line, as that is filesystem-dependent.
            lines = actual.split('\n')
            actual = '\n'.join(lines[1:])

        self.fail('Finish the test.')

    def test_suppress_xml(self):
        """Verify dumping with -x, suppress XML."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            sys.argv = ['', '-x', self.jp2file]
            command_line.main()
            actual = fake_out.getvalue().strip()
            # Remove the file line, as that is filesystem-dependent.
            lines = actual.split('\n')
            actual = '\n'.join(lines[1:])

        self.fail('Finish the test.')
