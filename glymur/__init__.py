"""glymur - read, write, and interrogate JPEG 2000 files
"""
import unittest

from glymur import version
__version__ = version.version

from .jp2k import Jp2k
from .jp2box import (get_printoptions, set_printoptions,
                     get_parseoptions, set_parseoptions)

from . import data

__all__ = [Jp2k, get_printoptions, set_printoptions, get_parseoptions,
           set_parseoptions, data]


def runtests():
    """Discover and run all tests for the glymur package.
    """
    suite = unittest.defaultTestLoader.discover(__path__[0])
    unittest.TextTestRunner(verbosity=2).run(suite)
