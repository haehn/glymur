import contextlib
import ctypes
import doctest
import imp
import os
import re
import struct
import sys
import tempfile
import uuid
import unittest
if sys.hexversion <= 0x03030000:
    from mock import patch
else:
    from unittest.mock import patch
import warnings
from xml.etree import cElementTree as ET

import numpy as np
import pkg_resources

from glymur import Jp2k
from glymur.lib import openjp2 as opj2
import glymur

try:
    data_root = os.environ['OPJ_DATA_ROOT']
except KeyError:
    data_root = None
except:
    raise


# Doc tests should be run as well.
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite('glymur.jp2k'))
    return tests


@contextlib.contextmanager
def chdir(dirname=None):
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)


class TestJp2k(unittest.TestCase):

    def setUp(self):
        self.jp2file = pkg_resources.resource_filename(glymur.__name__,
                                                       "data/nemo.jp2")

    def tearDown(self):
        pass

    @unittest.skipIf(sys.hexversion < 0x03020000,
                     "Uses features introduced in 3.2.")
    def test_invalid_xml_box(self):
        # Should be able to recover from xml box with bad xml.
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            with open(self.jp2file, 'rb') as ifile:
                # Everything up until the jp2c box.
                buffer = ifile.read(77)
                tfile.write(buffer)

                # Write the xml box with bad xml
                # Length = 28, id is 'xml '.
                buffer = struct.pack('>I4s', int(28), b'xml ')
                tfile.write(buffer)

                buffer = '<test>this is a test'
                buffer = buffer.encode()
                tfile.write(buffer)

                # Get the rest of the input file.
                buffer = ifile.read()
                tfile.write(buffer)
                tfile.flush()

            with self.assertWarns(UserWarning) as cw:
                jp2k = Jp2k(tfile.name)

            self.assertEqual(jp2k.box[3].id, 'xml ')
            self.assertEqual(jp2k.box[3].offset, 77)
            self.assertEqual(jp2k.box[3].length, 28)
            self.assertIsNone(jp2k.box[3].xml)

    def test_bad_area_parameter(self):
        # Verify that we error out appropriately if given a bad area parameter.
        j = Jp2k(self.jp2file)
        with self.assertRaises(IOError):
            # Start corner must be >= 0
            d = j.read(area=(-1, -1, 1, 1))
        with self.assertRaises(IOError):
            # End corner must be > 0
            d = j.read(area=(10, 10, 0, 0))
        with self.assertRaises(IOError):
            # End corner must be >= start corner
            d = j.read(area=(10, 10, 8, 8))

    def test_reduce_too_high(self):
        # Verify that we error out appropriately if not given a JPEG 2000 file.
        j = Jp2k(self.jp2file)
        with self.assertRaises(IOError):
            d = j.read(reduce=6)

    def test_not_JPEG2000(self):
        # Verify that we error out appropriately if not given a JPEG 2000 file.
        filename = pkg_resources.resource_filename(glymur.__name__, "jp2k.py")
        with self.assertRaises(IOError):
            jp2k = Jp2k(filename)

    def test_file_not_present(self):
        # Verify that we error out appropriately if not given an existing file
        # at all.
        if sys.hexversion < 0x03030000:
            error = OSError
        else:
            error = IOError
        with self.assertRaises(error):
            filename = 'this file does not actually exist on the file system.'
            jp2k = Jp2k(filename)

    def test_nemo_tile(self):
        # Issue 134, trouble reading first nemo tile.
        j = Jp2k(self.jp2file)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tiledata = j.read(tile=0)
        subsetdata = j.read(area=(0, 0, 512, 512))
        np.testing.assert_array_equal(tiledata, subsetdata)

    def test_jp2_boxes(self):
        # Verify the boxes of a JP2 file.
        jp2k = Jp2k(self.jp2file)

        # top-level boxes
        self.assertEqual(len(jp2k.box), 4)

        self.assertEqual(jp2k.box[0].id, 'jP  ')
        self.assertEqual(jp2k.box[0].offset, 0)
        self.assertEqual(jp2k.box[0].length, 12)
        self.assertEqual(jp2k.box[0].longname, 'JPEG 2000 Signature')

        self.assertEqual(jp2k.box[1].id, 'ftyp')
        self.assertEqual(jp2k.box[1].offset, 12)
        self.assertEqual(jp2k.box[1].length, 20)
        self.assertEqual(jp2k.box[1].longname, 'File Type')

        self.assertEqual(jp2k.box[2].id, 'jp2h')
        self.assertEqual(jp2k.box[2].offset, 32)
        self.assertEqual(jp2k.box[2].length, 45)
        self.assertEqual(jp2k.box[2].longname, 'JP2 Header')

        self.assertEqual(jp2k.box[3].id, 'jp2c')
        self.assertEqual(jp2k.box[3].offset, 77)
        self.assertEqual(jp2k.box[3].length, 1133427)

        # jp2h super box
        self.assertEqual(len(jp2k.box[2].box), 2)

        self.assertEqual(jp2k.box[2].box[0].id, 'ihdr')
        self.assertEqual(jp2k.box[2].box[0].offset, 40)
        self.assertEqual(jp2k.box[2].box[0].length, 22)
        self.assertEqual(jp2k.box[2].box[0].longname, 'Image Header')
        self.assertEqual(jp2k.box[2].box[0].height, 1456)
        self.assertEqual(jp2k.box[2].box[0].width, 2592)
        self.assertEqual(jp2k.box[2].box[0].num_components, 3)
        self.assertEqual(jp2k.box[2].box[0].bits_per_component, 8)
        self.assertEqual(jp2k.box[2].box[0].signed, False)
        self.assertEqual(jp2k.box[2].box[0].compression, 7)
        self.assertEqual(jp2k.box[2].box[0].cspace_unknown, False)
        self.assertEqual(jp2k.box[2].box[0].ip_provided, False)

        self.assertEqual(jp2k.box[2].box[1].id, 'colr')
        self.assertEqual(jp2k.box[2].box[1].offset, 62)
        self.assertEqual(jp2k.box[2].box[1].length, 15)
        self.assertEqual(jp2k.box[2].box[1].longname, 'Colour Specification')
        self.assertEqual(jp2k.box[2].box[1].precedence, 0)
        self.assertEqual(jp2k.box[2].box[1].approximation, 0)
        self.assertEqual(jp2k.box[2].box[1].color_space, glymur.core.SRGB)
        self.assertIsNone(jp2k.box[2].box[1].icc_profile)

    @unittest.skipIf(data_root is None,
                     "OPJ_DATA_ROOT environment variable not set")
    def test_j2k_box(self):
        # Verify that a J2K file has no boxes.
        filename = os.path.join(data_root, 'input/conformance/p0_01.j2k')
        jp2k = Jp2k(filename)
        self.assertEqual(len(jp2k.box), 0)

    def test_64bit_XL_field(self):
        # Verify that boxes with the XL field are properly read.
        # Don't have such a file on hand, so we create one.  Copy our example
        # file, but making the codestream have a 64-bit XL field.
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            with open(self.jp2file, 'rb') as ifile:
                # Everything up until the jp2c box.
                buffer = ifile.read(77)
                tfile.write(buffer)

                # The L field must be 1 in order to signal the presence of the
                # XL field.  The actual length of the jp2c box increased by 8
                # (8 bytes for the XL field).
                L = 1
                T = b'jp2c'
                XL = 1133427 + 8
                buffer = struct.pack('>I4sQ', int(L), T, XL)
                tfile.write(buffer)

                # Get the rest of the input file (minus the 8 bytes for L and
                # T.
                ifile.seek(8, 1)
                buffer = ifile.read()
                tfile.write(buffer)
                tfile.flush()

            jp2k = Jp2k(tfile.name)

            self.assertEqual(jp2k.box[3].id, 'jp2c')
            self.assertEqual(jp2k.box[3].offset, 77)
            self.assertEqual(jp2k.box[3].length, 1133427 + 8)

    def test_L_is_zero(self):
        # Verify that boxes with the L field as zero are correctly read.
        # This should only happen in the last box of a JPEG 2000 file.
        # Our example image has its last box at byte 588458.
        baseline_jp2 = Jp2k(self.jp2file)
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            with open(self.jp2file, 'rb') as ifile:
                # Everything up until the jp2c box.
                buffer = ifile.read(588458)
                tfile.write(buffer)

                L = 0
                T = b'uuid'
                buffer = struct.pack('>I4s', int(L), T)
                tfile.write(buffer)

                # Get the rest of the input file (minus the 8 bytes for L and
                # T.
                ifile.seek(8, 1)
                buffer = ifile.read()
                tfile.write(buffer)
                tfile.flush()

            new_jp2 = Jp2k(tfile.name)

            # The top level boxes in each file should match.
            for j in range(len(baseline_jp2.box)):
                self.assertEqual(new_jp2.box[j].id,
                                 baseline_jp2.box[j].id)
                self.assertEqual(new_jp2.box[j].offset,
                                 baseline_jp2.box[j].offset)
                self.assertEqual(new_jp2.box[j].length,
                                 baseline_jp2.box[j].length)

    @unittest.skipIf(data_root is None,
                     "OPJ_DATA_ROOT environment variable not set")
    def test_read_differing_subsamples(self):
        # Verify that we error out appropriately if we use the read method
        # on an image with differing subsamples
        #
        # Issue 86.
        filename = os.path.join(data_root, 'input/conformance/p0_05.j2k')
        j = Jp2k(filename)
        with self.assertRaises(IOError):
            j.read()

    @unittest.skipIf(data_root is None,
                     "OPJ_DATA_ROOT environment variable not set")
    def test_empty_box_with_j2k(self):
        # Verify that the list of boxes in a J2C/J2K file is present, but
        # empty.
        filename = os.path.join(data_root, 'input/conformance/p0_05.j2k')
        j = Jp2k(filename)
        self.assertEqual(j.box, [])

    def test_code_block_height_different_than_width(self):
        # Verify that we can set a code block size where height does not equal
        # width.
        data = np.zeros((128, 128), dtype=np.uint8)
        with tempfile.NamedTemporaryFile(suffix='.j2k') as tfile:
            j = Jp2k(tfile.name, 'wb')

            # The code block dimensions are given as rows x columns.
            j.write(data, cbsize=(16, 32))

            c = j.get_codestream()

            # Code block size is reported as XY in the codestream.
            self.assertEqual(tuple(c.segment[2].SPcod[5:7]), (3, 2))

    def test_negative_too_many_dimensions(self):
        # OpenJP2 only allows 2D or 3D images.
        with tempfile.NamedTemporaryFile(suffix='.j2k') as tfile:
            j = Jp2k(tfile.name, 'wb')
            with self.assertRaises(IOError) as ce:
                data = np.zeros((128, 128, 2, 2), dtype=np.uint8)
                j.write(data)

    def test_unrecognized_jp2_colorspace(self):
        # We only allow RGB and GRAYSCALE.
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            with self.assertRaises(IOError) as ce:
                data = np.zeros((128, 128, 3), dtype=np.uint8)
                j.write(data, colorspace='cmyk')

    def test_2D_rgb(self):
        # RGB must have at least 3 components.
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            with self.assertRaises(IOError) as ce:
                data = np.zeros((128, 128, 2), dtype=np.uint8)
                j.write(data, colorspace='rgb')

    def test_colorspace_with_j2k(self):
        # Specifying a colorspace with J2K does not make sense.
        with tempfile.NamedTemporaryFile(suffix='.j2k') as tfile:
            j = Jp2k(tfile.name, 'wb')
            with self.assertRaises(IOError) as ce:
                data = np.zeros((128, 128, 3), dtype=np.uint8)
                j.write(data, colorspace='rgb')

    def test_specify_rgb(self):
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            data = np.zeros((128, 128, 3), dtype=np.uint8)
            j.write(data, colorspace='rgb')
            self.assertEqual(j.box[2].box[1].color_space, glymur.core.SRGB)

    def test_specify_gray(self):
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            data = np.zeros((128, 128), dtype=np.uint8)
            j.write(data, colorspace='gray')
            self.assertEqual(j.box[2].box[1].color_space,
                             glymur.core.GREYSCALE)

    def test_specify_grey(self):
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            data = np.zeros((128, 128), dtype=np.uint8)
            j.write(data, colorspace='grey')
            self.assertEqual(j.box[2].box[1].color_space,
                             glymur.core.GREYSCALE)

    def test_grey_with_extra_component(self):
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            data = np.zeros((128, 128, 2), dtype=np.uint8)
            j.write(data)
            self.assertEqual(j.box[2].box[0].height, 128)
            self.assertEqual(j.box[2].box[0].width, 128)
            self.assertEqual(j.box[2].box[0].num_components, 2)
            self.assertEqual(j.box[2].box[1].color_space,
                             glymur.core.GREYSCALE)

    def test_grey_with_two_extra_components(self):
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            data = np.zeros((128, 128, 3), dtype=np.uint8)
            j.write(data, colorspace='gray')
            self.assertEqual(j.box[2].box[0].height, 128)
            self.assertEqual(j.box[2].box[0].width, 128)
            self.assertEqual(j.box[2].box[0].num_components, 3)
            self.assertEqual(j.box[2].box[1].color_space,
                             glymur.core.GREYSCALE)

    def test_rgb_with_extra_component(self):
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            data = np.zeros((128, 128, 4), dtype=np.uint8)
            j.write(data)
            self.assertEqual(j.box[2].box[0].height, 128)
            self.assertEqual(j.box[2].box[0].width, 128)
            self.assertEqual(j.box[2].box[0].num_components, 4)
            self.assertEqual(j.box[2].box[1].color_space, glymur.core.SRGB)

    def test_specify_ycc(self):
        # We don't support writing YCC at the moment.
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            with self.assertRaises(IOError) as ce:
                data = np.zeros((128, 128, 3), dtype=np.uint8)
                j.write(data, colorspace='ycc')

    def test_uinf_ulst_url_boxes(self):
        # Verify that we can read UINF, ULST, and URL boxes.  I don't have
        # easy access to such a file, and there's no such file in the
        # openjpeg repository, so I'll fake one.
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            with open(self.jp2file, 'rb') as ifile:
                # Everything up until the jp2c box.
                buffer = ifile.read(77)
                tfile.write(buffer)

                # Write the UINF superbox
                # Length = 50, id is uinf.
                buffer = struct.pack('>I4s', int(50), b'uinf')
                tfile.write(buffer)

                # Write the ULST box.
                # Length is 26, 1 UUID, hard code that UUID as zeros.
                buffer = struct.pack('>I4sHIIII', int(26), b'ulst', int(1),
                                     int(0), int(0), int(0), int(0))
                tfile.write(buffer)

                # Write the URL box.
                # Length is 16, version is one byte, flag is 3 bytes, url
                # is the rest.
                buffer = struct.pack('>I4sBBBB',
                                     int(16), b'url ',
                                     int(0), int(0), int(0), int(0))
                tfile.write(buffer)
                buffer = struct.pack('>ssss', b'a', b'b', b'c', b'd')
                tfile.write(buffer)

                # Get the rest of the input file.
                buffer = ifile.read()
                tfile.write(buffer)
                tfile.flush()

            jp2k = Jp2k(tfile.name)

            self.assertEqual(jp2k.box[3].id, 'uinf')
            self.assertEqual(jp2k.box[3].offset, 77)
            self.assertEqual(jp2k.box[3].length, 50)

            self.assertEqual(jp2k.box[3].box[0].id, 'ulst')
            self.assertEqual(jp2k.box[3].box[0].offset, 85)
            self.assertEqual(jp2k.box[3].box[0].length, 26)
            ulst = []
            ulst.append(uuid.UUID('00000000-0000-0000-0000-000000000000'))
            self.assertEqual(jp2k.box[3].box[0].ulst, ulst)

            self.assertEqual(jp2k.box[3].box[1].id, 'url ')
            self.assertEqual(jp2k.box[3].box[1].offset, 111)
            self.assertEqual(jp2k.box[3].box[1].length, 16)
            self.assertEqual(jp2k.box[3].box[1].version, 0)
            self.assertEqual(jp2k.box[3].box[1].flag, (0, 0, 0))
            self.assertEqual(jp2k.box[3].box[1].URL, 'abcd')

    def test_xml_box_with_trailing_nulls(self):
        # ElementTree does not like trailing null chars after valid XML
        # text.
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            with open(self.jp2file, 'rb') as ifile:
                # Everything up until the jp2c box.
                buffer = ifile.read(77)
                tfile.write(buffer)

                # Write the xml box
                # Length = 36, id is 'xml '.
                buffer = struct.pack('>I4s', int(36), b'xml ')
                tfile.write(buffer)

                buffer = '<test>this is a test</test>' + chr(0)
                buffer = buffer.encode()
                tfile.write(buffer)

                # Get the rest of the input file.
                buffer = ifile.read()
                tfile.write(buffer)
                tfile.flush()

            jp2k = Jp2k(tfile.name)

            self.assertEqual(jp2k.box[3].id, 'xml ')
            self.assertEqual(jp2k.box[3].offset, 77)
            self.assertEqual(jp2k.box[3].length, 36)

    def test_asoc_label_box(self):
        # Construct a fake file with an asoc and a label box, as
        # OpenJPEG doesn't have such a file.
        data = Jp2k(self.jp2file).read(reduce=3)
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            j.write(data)

            with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile2:

                # Offset of the codestream is where we start.
                buffer = tfile.read(77)
                tfile2.write(buffer)

                # read the rest of the file, it's the codestream.
                codestream = tfile.read()

                # Write the asoc superbox.
                # Length = 36, id is 'asoc'.
                buffer = struct.pack('>I4s', int(56), b'asoc')
                tfile2.write(buffer)

                # Write the contained label box
                buffer = struct.pack('>I4s', int(13), b'lbl ')
                tfile2.write(buffer)
                tfile2.write('label'.encode())

                # Write the xml box
                # Length = 36, id is 'xml '.
                buffer = struct.pack('>I4s', int(35), b'xml ')
                tfile2.write(buffer)

                buffer = '<test>this is a test</test>'
                buffer = buffer.encode()
                tfile2.write(buffer)

                # Now append the codestream.
                tfile2.write(codestream)

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    jasoc = Jp2k(tfile2.name)
                self.assertEqual(jasoc.box[3].id, 'asoc')
                self.assertEqual(jasoc.box[3].box[0].id, 'lbl ')
                self.assertEqual(jasoc.box[3].box[0].label, 'label')
                self.assertEqual(jasoc.box[3].box[1].id, 'xml ')

    def test_openjpeg_library_message(self):
        # Verify the error message produced by the openjpeg library.
        # This will confirm that the error callback mechanism is working.
        with open(self.jp2file, 'rb') as fp:
            data = fp.read()
            with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
                tfile.write(data[0:129])

                # Make the DY bytes of the SIZ segment zero.  That means that
                # a subsampling factor is zero, which is illegal.
                tfile.write(b'\x00')
                tfile.write(data[130:132])
                tfile.write(b'\x00')
                tfile.write(data[134:136])
                tfile.write(b'\x00')

                tfile.write(data[136:])
                tfile.flush()
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    j = Jp2k(tfile.name)
                regexp = re.compile(r'''OpenJPEG\slibrary\serror:\s+
                                        Invalid\svalues\sfor\scomp\s=\s0\s+
                                        :\sdx=1\sdy=0''', re.VERBOSE)
                if sys.hexversion < 0x03020000:
                    with self.assertRaisesRegexp(IOError, regexp) as ce:
                        d = j.read(reduce=3)
                else:
                    with self.assertRaisesRegex(IOError, regexp) as ce:
                        d = j.read(reduce=3)

    @unittest.skipIf(sys.hexversion < 0x03020000,
                     "Uses features introduced in 3.2.")
    def test_config_file_via_environ(self):
        """Verify that we can read a configuration file set via environ var."""
        with tempfile.TemporaryDirectory() as tdir:
            filename = os.path.join(tdir, 'glymurrc')
            with open(filename, 'wb') as tfile:
                tfile.write('[library]\n'.encode())
                line = 'openjp2: {0}\n'.format(glymur._OPENJP2._name)
                tfile.write(line.encode())
                tfile.flush()
                with patch.dict('os.environ', {'GLYMURCONFIGDIR': tdir}):
                    imp.reload(glymur)
                    j = Jp2k(self.jp2file)

    @unittest.skipIf(sys.hexversion < 0x03020000,
                     "Uses features introduced in 3.2.")
    def test_config_file_via_environ_is_wrong(self):
        # A non-existant library location should be rejected.
        with tempfile.TemporaryDirectory() as tdir:
            fname = os.path.join(tdir, 'glymurrc')
            with open(fname, 'w') as fp:
                with tempfile.NamedTemporaryFile(suffix='.dylib') as tfile:
                    fp.write('[library]\n')
                    fp.write('openjp2: {0}.not.there\n'.format(tfile.name))
                    fp.flush()
                    with patch.dict('os.environ', {'GLYMURCONFIGDIR': tdir}):
                        # Misconfigured new configuration file should
                        # be rejected.
                        with self.assertRaises(ImportError) as ce:
                            imp.reload(glymur)

    @unittest.skipIf(sys.hexversion < 0x03020000,
                     "Uses features introduced in 3.2.")
    def test_missing_config_file_via_environ(self):
        # Verify that we error out properly if the configuration file
        # specified via environment variable is not found.
        with tempfile.TemporaryDirectory() as tdir:
            with patch.dict('os.environ', {'GLYMURCONFIGDIR': tdir}):
                # Misconfigured new configuration file should
                # be rejected.
                with self.assertRaises(ImportError) as ce:
                    imp.reload(glymur)


if __name__ == "__main__":
    unittest.main()