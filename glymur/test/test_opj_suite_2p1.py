"""
The tests defined here roughly correspond to what is in the OpenJPEG test
suite.
"""

# Some test names correspond with openjpeg tests.  Long names are ok in this
# case.
# pylint: disable=C0103

# All of these tests correspond to tests in openjpeg, so no docstring is really
# needed.
# pylint: disable=C0111

# This module is very long, cannot be helped.
# pylint: disable=C0302

# unittest fools pylint with "too many public methods"
# pylint: disable=R0904

# Some tests use numpy test infrastructure, which means the tests never
# reference "self", so pylint claims it should be a function.  No, no, no.
# pylint: disable=R0201

# Many tests are pretty long and that can't be helped.
# pylint:  disable=R0915

# asserWarns introduced in python 3.2 (python2.7/pylint issue)
# pylint: disable=E1101

import re
import sys
import unittest

import numpy as np

from glymur import Jp2k
import glymur

from .fixtures import OPJ_DATA_ROOT
from .fixtures import WARNING_INFRASTRUCTURE_ISSUE, WARNING_INFRASTRUCTURE_MSG
from .fixtures import mse, peak_tolerance, read_pgx, opj_data_file


@unittest.skipIf(OPJ_DATA_ROOT is None,
                 "OPJ_DATA_ROOT environment variable not set")
@unittest.skipIf(re.match(r'''(1|2.0.0)''',
                          glymur.version.openjpeg_version) is not None,
                 "Only supported in 2.0.1 or higher")
class TestSuite2point1(unittest.TestCase):
    """Runs tests introduced in version 2.0+ or that pass only in 2.0+"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skipIf(WARNING_INFRASTRUCTURE_ISSUE, WARNING_INFRASTRUCTURE_MSG)
    def test_NR_DEC_text_GBR_jp2_29_decode(self):
        jfile = opj_data_file('input/nonregression/text_GBR.jp2')
        with self.assertWarns(UserWarning):
            # brand is 'jp2 ', but has any icc profile.
            jp2 = Jp2k(jfile)
        jp2[:]
        self.assertTrue(True)

    def test_NR_DEC_kodak_2layers_lrcp_j2c_31_decode(self):
        jfile = opj_data_file('input/nonregression/kodak_2layers_lrcp.j2c')
        Jp2k(jfile)[:]
        self.assertTrue(True)

    def test_NR_DEC_kodak_2layers_lrcp_j2c_32_decode(self):
        jfile = opj_data_file('input/nonregression/kodak_2layers_lrcp.j2c')
        Jp2k(jfile)[::4, ::4]
        self.assertTrue(True)

    def test_NR_DEC_issue104_jpxstream_jp2_33_decode(self):
        jfile = opj_data_file('input/nonregression/issue104_jpxstream.jp2')
        Jp2k(jfile)[:]
        self.assertTrue(True)

    def test_NR_DEC_mem_b2b86b74_2753_jp2_35_decode(self):
        jfile = opj_data_file('input/nonregression/mem-b2b86b74-2753.jp2')
        Jp2k(jfile)[:]
        self.assertTrue(True)

    @unittest.skipIf(WARNING_INFRASTRUCTURE_ISSUE, WARNING_INFRASTRUCTURE_MSG)
    def test_NR_DEC_gdal_fuzzer_unchecked_num_resolutions_jp2_36_decode(self):
        f = 'input/nonregression/gdal_fuzzer_unchecked_numresolutions.jp2'
        jfile = opj_data_file(f)
        with self.assertWarns(UserWarning):
            # Invalid number of resolutions.
            j = Jp2k(jfile)
            with self.assertRaises(IOError):
                j[:]

    @unittest.skipIf(WARNING_INFRASTRUCTURE_ISSUE, WARNING_INFRASTRUCTURE_MSG)
    def test_NR_DEC_gdal_fuzzer_check_number_of_tiles_jp2_38_decode(self):
        relpath = 'input/nonregression/gdal_fuzzer_check_number_of_tiles.jp2'
        jfile = opj_data_file(relpath)
        with self.assertWarns(UserWarning):
            # Invalid number of tiles.
            j = Jp2k(jfile)
            with self.assertRaises(IOError):
                j[:]

    @unittest.skipIf(WARNING_INFRASTRUCTURE_ISSUE, WARNING_INFRASTRUCTURE_MSG)
    def test_NR_DEC_gdal_fuzzer_check_comp_dx_dy_jp2_39_decode(self):
        relpath = 'input/nonregression/gdal_fuzzer_check_comp_dx_dy.jp2'
        jfile = opj_data_file(relpath)
        with self.assertWarns(UserWarning):
            # Invalid subsampling value
            with self.assertRaises(IOError):
                Jp2k(jfile)[:]

    def test_NR_DEC_file_409752_jp2_40_decode(self):
        jfile = opj_data_file('input/nonregression/file409752.jp2')
        with self.assertRaises(RuntimeError):
            Jp2k(jfile)[:]

    def test_NR_DEC_issue206_image_000_jp2_42_decode(self):
        jfile = opj_data_file('input/nonregression/issue206_image-000.jp2')
        Jp2k(jfile)[:]
        self.assertTrue(True)

    def test_NR_DEC_p1_04_j2k_57_decode(self):
        jfile = opj_data_file('input/conformance/p1_04.j2k')
        jp2k = Jp2k(jfile)
        tdata = jp2k.read(tile=63)  # last tile
        odata = jp2k[:]
        np.testing.assert_array_equal(tdata, odata[896:1024, 896:1024])

    def test_NR_DEC_p1_04_j2k_58_decode(self):
        jfile = opj_data_file('input/conformance/p1_04.j2k')
        jp2k = Jp2k(jfile)
        tdata = jp2k.read(tile=63, rlevel=2)  # last tile
        odata = jp2k[::4, ::4]
        np.testing.assert_array_equal(tdata, odata[224:256, 224:256])

    def test_NR_DEC_p1_04_j2k_59_decode(self):
        jfile = opj_data_file('input/conformance/p1_04.j2k')
        jp2k = Jp2k(jfile)
        tdata = jp2k.read(tile=12)  # 2nd row, 5th column
        odata = jp2k[:]
        np.testing.assert_array_equal(tdata, odata[128:256, 512:640])

    def test_NR_DEC_p1_04_j2k_60_decode(self):
        jfile = opj_data_file('input/conformance/p1_04.j2k')
        jp2k = Jp2k(jfile)
        tdata = jp2k.read(tile=12, rlevel=1)  # 2nd row, 5th column
        odata = jp2k[::2, ::2]
        np.testing.assert_array_equal(tdata, odata[64:128, 256:320])

    @unittest.skipIf(WARNING_INFRASTRUCTURE_ISSUE, WARNING_INFRASTRUCTURE_MSG)
    def test_NR_DEC_jp2_36_decode(self):
        lst = ('input',
               'nonregression',
               'gdal_fuzzer_assert_in_opj_j2k_read_SQcd_SQcc.patch.jp2')
        jfile = opj_data_file('/'.join(lst))
        with self.assertWarns(UserWarning):
            # Invalid component number.
            j = Jp2k(jfile)
            with self.assertRaises(IOError):
                j[:]

@unittest.skipIf(OPJ_DATA_ROOT is None,
                 "OPJ_DATA_ROOT environment variable not set")
@unittest.skipIf(re.match(r'''(1|2.0.0)''',
                          glymur.version.openjpeg_version) is not None,
                 "Only supported in 2.0.1 or higher")
class TestReadArea(unittest.TestCase):
    """
    Runs tests introduced in version 2.0+ or that pass only in 2.0+
    
    Specifically for read method with area parameter.
    """
    @classmethod
    def setUpClass(self):

        jfile = opj_data_file('input/conformance/p1_04.j2k')
        self.j2k = Jp2k(jfile)
        self.j2k_data = self.j2k[:]
        self.j2k_half_data = self.j2k[::2, ::2]
        self.j2k_quarter_data = self.j2k[::4, ::4]

        jfile = opj_data_file('input/conformance/p1_06.j2k')
        self.j2k_p1_06 = Jp2k(jfile)

    def test_NR_DEC_p1_04_j2k_43_decode(self):
        actual = self.j2k[:1024, :1024]
        expected = self.j2k_data
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_04_j2k_44_decode(self):
        actual = self.j2k[640:768, 512:640]
        expected = self.j2k_data[640:768, 512:640]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_04_j2k_45_decode(self):
        actual = self.j2k[896:1024, 896:1024]
        expected = self.j2k_data[896:1024, 896:1024]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_04_j2k_46_decode(self):
        actual = self.j2k[500:800, 100:300]
        expected = self.j2k_data[500:800, 100:300]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_04_j2k_47_decode(self):
        actual = self.j2k[520:600, 260:360]
        expected = self.j2k_data[520:600, 260:360]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_04_j2k_48_decode(self):
        actual = self.j2k[520:660, 260:360]
        expected = self.j2k_data[520:660, 260:360]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_04_j2k_49_decode(self):
        actual = self.j2k[520:600, 360:400]
        expected = self.j2k_data[520:600, 360:400]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_04_j2k_50_decode(self):
        actual = self.j2k[:1024:4, :1024:4]
        expected = self.j2k_quarter_data
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_04_j2k_51_decode(self):
        actual = self.j2k[640:768:4, 512:640:4]
        expected = self.j2k_quarter_data[160:192, 128:160]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_04_j2k_52_decode(self):
        actual = self.j2k[896:1024:4, 896:1024:4]
        expected = self.j2k_quarter_data[224:352, 224:352]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_04_j2k_53_decode(self):
        actual = self.j2k[500:800:4, 100:300:4]
        expected = self.j2k_quarter_data[125:200, 25:75]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_04_j2k_54_decode(self):
        actual = self.j2k[520:600:4, 260:360:4]
        expected = self.j2k_quarter_data[130:150, 65:90]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_04_j2k_55_decode(self):
        actual = self.j2k[520:660:4, 260:360:4]
        expected = self.j2k_quarter_data[130:165, 65:90]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_04_j2k_56_decode(self):
        actual = self.j2k[520:600:4, 360:400:4]
        expected = self.j2k_quarter_data[130:150, 90:100]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p1_06_j2k_70_decode(self):
        actual = self.j2k_p1_06[9:12:2, 9:12:2]
        self.assertEqual(actual.shape, (1, 1, 3))

    def test_NR_DEC_p1_06_j2k_71_decode(self):
        actual = self.j2k_p1_06[10:12:2, 4:10:2]
        self.assertEqual(actual.shape, (1, 3, 3))

    def test_NR_DEC_p1_06_j2k_72_decode(self):
        ssdata = self.j2k_p1_06[3:9:2, 3:9:2]
        self.assertEqual(ssdata.shape, (3, 3, 3))

    def test_NR_DEC_p1_06_j2k_73_decode(self):
        ssdata = self.j2k_p1_06[4:7:2, 4:7:2]
        self.assertEqual(ssdata.shape, (2, 2, 3))

    def test_NR_DEC_p1_06_j2k_74_decode(self):
        ssdata = self.j2k_p1_06[4:5:2, 4:5:2]
        self.assertEqual(ssdata.shape, (1, 1, 3))

    def test_NR_DEC_p1_06_j2k_75_decode(self):
        # Image size would be 0 x 0.
        with self.assertRaises((IOError, OSError)):
            self.j2k_p1_06[9:12:4, 9:12:4]

    def test_NR_DEC_p0_04_j2k_85_decode(self):
        actual = self.j2k[:256, :256]
        expected = self.j2k_data[:256, :256]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p0_04_j2k_86_decode(self):
        actual = self.j2k[:128, 128:256]
        expected = self.j2k_data[:128, 128:256]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p0_04_j2k_87_decode(self):
        actual = self.j2k[10:200, 50:120]
        expected = self.j2k_data[10:200, 50:120]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p0_04_j2k_88_decode(self):
        actual = self.j2k[150:210, 10:190]
        expected = self.j2k_data[150:210, 10:190]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p0_04_j2k_89_decode(self):
        actual = self.j2k[80:150, 100:200]
        expected = self.j2k_data[80:150, 100:200]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p0_04_j2k_90_decode(self):
        actual = self.j2k[20:50, 150:200]
        expected = self.j2k_data[20:50, 150:200]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p0_04_j2k_91_decode(self):
        actual = self.j2k[:256:4, :256:4]
        expected = self.j2k_quarter_data[0:64, 0:64]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p0_04_j2k_92_decode(self):
        actual = self.j2k[:128:4, 128:256:4]
        expected = self.j2k_quarter_data[:32, 32:64]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p0_04_j2k_93_decode(self):
        actual = self.j2k[10:200:4, 50:120:4]
        expected = self.j2k_quarter_data[3:50, 13:30]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p0_04_j2k_94_decode(self):
        actual = self.j2k[150:210:4, 10:190:4]
        expected = self.j2k_quarter_data[38:53, 3:48]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p0_04_j2k_95_decode(self):
        actual = self.j2k[80:150:4, 100:200:4]
        expected = self.j2k_quarter_data[20:38, 25:50]
        np.testing.assert_array_equal(actual, expected)

    def test_NR_DEC_p0_04_j2k_96_decode(self):
        actual = self.j2k[20:50:4, 150:200:4]
        expected = self.j2k_quarter_data[5:13, 38:50]
        np.testing.assert_array_equal(actual, expected)
