import py, os, sys
from pytest import raises, mark
from .support import setup_make

currpath = py.path.local(__file__).dirpath()
test_dct = str(currpath.join("conversionsDict.so"))
test_h = str(currpath.join("conversions.h"))

def setup_module(mod):
    setup_make("conversions")


class TestCONVERSIONS:
    def setup_class(cls):
        cls.test_dct = test_dct
        cls.test_h = test_h
        import cppyy
        cls.conversion = cppyy.load_library(cls.test_dct)
        cppyy.include(cls.test_h)

    @mark.xfail
    def test01_implicit_vector_conversions(self):
        """Test implicit conversions of std::vector"""

        import cppyy
        CNS = cppyy.gbl.CNS

        N = 10
        total = float(sum(range(N)))

        v = cppyy.gbl.std.vector['double'](range(N))
        assert CNS.sumit(v) == total
        assert sum(v) == total
        assert CNS.sumit(range(N)) == total

        M = 5
        total = float(sum(range(N)) + sum(range(M, N)))
        v1 = cppyy.gbl.std.vector['double'](range(N))
        v2 = cppyy.gbl.std.vector['double'](range(M, N))
        assert CNS.sumit(v1, v2) == total
        assert sum(v1)+sum(v2)   == total
        assert CNS.sumit(v1, range(M, N))       == total
        assert CNS.sumit(range(N), v2)          == total
        assert CNS.sumit(range(N), range(M, N)) == total

    @mark.xfail
    def test02_memory_handling_of_temporaries(self):
        """Verify that memory of temporaries is properly cleaned up"""

        import cppyy, gc
        CNS, CC = cppyy.gbl.CNS, cppyy.gbl.CNS.Counter

        assert CC.s_count == 0
        c = CC()
        assert c.__python_owns__
        assert CC.s_count == 1
        del c; gc.collect()
        assert CC.s_count == 0

        assert CNS.myhowmany((CC(), CC(), CC())) == 3
        gc.collect()
        assert CC.s_count == 0

        assert CNS.myhowmany((CC(), CC(), CC()), [CC(), CC()]) == 5
        gc.collect()
        assert CC.s_count == 0

    @mark.xfail
    def test03_error_handling(self):
        """Verify error handling"""

        import cppyy, gc
        CNS, CC = cppyy.gbl.CNS, cppyy.gbl.CNS.Counter

        N = 13
        total = sum(range(N))
        assert CNS.sumints(range(N)) == total
        assert CNS.sumit([float(x) for x in range(N)]) == float(total)
        raises(TypeError, CNS.sumints, [float(x) for x in range(N)])
        raises(TypeError, CNS.sumints, list(range(N))+[0.])

        assert CC.s_count == 0

        raises(TypeError, CNS.sumints, list(range(N))+[CC()])
        gc.collect()
        assert CC.s_count == 0

        raises(TypeError, CNS.sumints, range(N), [CC()])
        gc.collect()

        assert CC.s_count == 0
        raises(TypeError, CNS.sumints, [CC()], range(N))
        gc.collect()
        assert CC.s_count == 0

    @mark.xfail
    def test04_implicit_conversion_from_tuple(self):
        """Allow implicit conversions from tuples as arguments {}-like"""

        # Note: fails on windows b/c the assignment operator for strings is
        # template, which ("operator=(std::string)") doesn't instantiate
        import cppyy

        m = cppyy.gbl.std.map[str, str]()
        m.insert(('a', 'b'))      # implicit conversion to std::pair

        assert m['a'] == 'b'
