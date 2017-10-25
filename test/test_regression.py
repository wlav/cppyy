import py, os, sys
from pytest import raises
from .support import setup_make

currpath = py.path.local(__file__).dirpath()


class TestREGRESSION:
    def setup_class(cls):
        import cppyy

    def test01_kdcraw(self):
        """Template member functions lookup and calls"""

        import cppyy

        # TODO: run a find for these paths
        qtpath = "/usr/include/qt5"
        kdcraw_h = "/usr/include/KF5/KDCRAW/kdcraw/kdcraw.h"
        if not os.path.isdir(qtpath) or not os.path.exists(kdcraw_h):
            import warnings
            warnings.warn("no KDE/Qt found, skipping test01_kdcraw")
            return

        cppyy.add_include_path(qtpath)
        cppyy.include(kdcraw_h)

        from cppyy.gbl import KDcrawIface
        help(KDcrawIface)

    def test02_dir(self):
        """For the same reasons as test01_kdcraw, this used to crash."""

        import cppyy

        help(cppyy.gbl.gInterpreter)
