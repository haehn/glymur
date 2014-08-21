"""
Test suite for warnings issued by glymur.
"""

# unittest doesn't work well with R0904.
# pylint: disable=R0904

# tempfile.TemporaryDirectory, unittest.assertWarns introduced in 3.2
# pylint: disable=E1101

import os
import re
import struct
import sys
import tempfile
import unittest
import warnings

from glymur import Jp2k
import glymur

from .fixtures import opj_data_file, OPJ_DATA_ROOT

@unittest.skipIf(sys.hexversion < 0x03030000,
                 "assertWarn methods introduced in 3.x")
@unittest.skipIf(OPJ_DATA_ROOT is None,
                 "OPJ_DATA_ROOT environment variable not set")
class TestWarnings(unittest.TestCase):
    """Test suite for warnings issued by glymur."""

    def test_NR_broken_jp2_dump(self):
        """
        The colr box has a ridiculously incorrect box length.
        """
        jfile = opj_data_file('input/nonregression/broken.jp2')
        regex = re.compile(r'''b'colr'\sbox\shas\sincorrect\sbox\slength\s
                               \(\d+\)''',
                           re.VERBOSE)
        with self.assertWarnsRegex(UserWarning, regex):
            jp2 = Jp2k(jfile)

    def test_NR_broken2_jp2_dump(self):
        """
        Invalid marker ID on codestream.
        """
        jfile = opj_data_file('input/nonregression/broken2.jp2')
        regex = re.compile(r'''Invalid\smarker\sid\sencountered\sat\sbyte\s
                               \d+\sin\scodestream:\s*"0x[a-fA-F0-9]{4}"''', 
                           re.VERBOSE)
        with self.assertWarnsRegex(UserWarning, regex):
            jp2 = Jp2k(jfile)

    def test_bad_rsiz(self):
        """Should warn if RSIZ is bad.  Issue196"""
        filename = opj_data_file('input/nonregression/edf_c2_1002767.jp2')
        with self.assertWarnsRegex(UserWarning, 'Invalid profile'):
            j = Jp2k(filename)

    def test_bad_wavelet_transform(self):
        """Should warn if wavelet transform is bad.  Issue195"""
        filename = opj_data_file('input/nonregression/edf_c2_10025.jp2')
        with self.assertWarnsRegex(UserWarning, 'Invalid wavelet transform'):
            j = Jp2k(filename)

    def test_invalid_progression_order(self):
        """Should still be able to parse even if prog order is invalid."""
        jfile = opj_data_file('input/nonregression/2977.pdf.asan.67.2198.jp2')
        with self.assertWarnsRegex(UserWarning, 'Invalid progression order'):
            Jp2k(jfile)

    def test_tile_height_is_zero(self):
        """Zero tile height should not cause an exception."""
        filename = opj_data_file('input/nonregression/2539.pdf.SIGFPE.706.1712.jp2')
        with self.assertWarnsRegex(UserWarning, 'Invalid tile dimensions'):
            Jp2k(filename)

    @unittest.skipIf(os.name == "nt", "Temporary file issue on window.")
    def test_unknown_marker_segment(self):
        """Should warn for an unknown marker."""
        # Let's inject a marker segment whose marker does not appear to
        # be valid.  We still parse the file, but warn about the offending
        # marker.
        filename = os.path.join(OPJ_DATA_ROOT, 'input/conformance/p0_01.j2k')
        with tempfile.NamedTemporaryFile(suffix='.j2k') as tfile:
            with open(filename, 'rb') as ifile:
                # Everything up until the first QCD marker.
                read_buffer = ifile.read(45)
                tfile.write(read_buffer)

                # Write the new marker segment, 0xff79 = 65401
                read_buffer = struct.pack('>HHB', int(65401), int(3), int(0))
                tfile.write(read_buffer)

                # Get the rest of the input file.
                read_buffer = ifile.read()
                tfile.write(read_buffer)
                tfile.flush()
 
                with self.assertWarnsRegex(UserWarning, 'Unrecognized marker'):
                    codestream = Jp2k(tfile.name).get_codestream()

                self.assertEqual(codestream.segment[2].marker_id, '0xff79')
                self.assertEqual(codestream.segment[2].length, 3)
                self.assertEqual(codestream.segment[2].data, b'\x00')


if __name__ == "__main__":
    unittest.main()
