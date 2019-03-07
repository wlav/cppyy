import py, os, sys
from pytest import raises
from .support import setup_make, pylong, pyunicode

currpath = py.path.local(__file__).dirpath()
test_dct = str(currpath.join("conversionsDict.so"))

def setup_module(mod):
    setup_make("conversionsDict.so")


class TestCONVERSIONS:
    def setup_class(cls):
        cls.test_dct = test_dct
        import cppyy
        cls.datatypes = cppyy.load_reflection_info(cls.test_dct)

    def test01_implicit_vector_conversions(self):
        """Test implicit conversions of std::vector"""

        import cppyy
        CNS = cppyy.gbl.CNS

        N = 10
        total = sum(range(N))

        v = cppyy.gbl.std.vector['double'](range(N))
        assert CNS.sumit(v) == total
        assert sum(v) == total
        assert CNS.sumit(range(N)) == total
