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

        M = 5
        total = sum(range(N)) + sum(range(M, N))
        v1 = cppyy.gbl.std.vector['double'](range(N))
        v2 = cppyy.gbl.std.vector['double'](range(M, N))
        assert CNS.sumit(v1, v2) == total
        assert sum(v1)+sum(v2)   == total
        assert CNS.sumit(v1, range(M, N))       == total
        assert CNS.sumit(range(N), v2)          == total
        assert CNS.sumit(range(N), range(M, N)) == total

    def test02_memory_handling_of_temporaries(self):
        """Verify that memory of temporaries is properly cleaned up"""

        import cppyy, gc
        CNS, CC = cppyy.gbl.CNS, cppyy.gbl.CNS.Counter

        assert CC.s_count == 0
        c = CC()
        assert CC.s_count == 1
        del c; gc.collect()
        assert CC.s_count == 0

        assert CNS.howmany((CC(), CC(), CC())) == 3
        gc.collect()
        assert CC.s_count == 0

        assert CNS.howmany((CC(), CC(), CC()), [CC(), CC()]) == 5
        gc.collect()
        assert CC.s_count == 0
