import py, os, sys
import math, time
from pytest import mark, raises
from .support import setup_make

try:
    import numba
    has_numba = True
except ImportError:
    has_numba = False


@mark.skipif(has_numba == False, reason="numba not found")
class TestNUMBA:
    def setup_class(cls):
        import cppyy
        import cppyy.numba_ext

    def compare(self, go_slow, go_fast, N, *args):
        t0 = time.time()
        for i in range(N):
            go_slow(*args)
        slow_time = time.time() - t0

        t0 = time.time()
        for i in range(N):
            go_fast(*args)
        fast_time = time.time() - t0

        return fast_time < slow_time

    def test01_compiled_free_func(self):
        """Test Numba-JITing of a compiled free function"""

        import cppyy
        import numpy as np

        def go_slow(a):
            trace = 0.0
            for i in range(a.shape[0]):
                trace += math.tanh(a[i, i])
            return a + trace

        @numba.jit(nopython=True)
        def go_fast(a):
            trace = 0.0
            for i in range(a.shape[0]):
                trace += cppyy.gbl.tanh(a[i, i])
            return a + trace

        x = np.arange(100, dtype=np.float64).reshape(10, 10)

        assert (go_fast(x) == go_slow(x)).all()
        assert self.compare(go_slow, go_fast, 300000, x)

    def test02_JITed_template_free_func(self):
        """Test Numba-JITing of Cling-JITed templated free function"""

        import cppyy
        import numpy as np

        cppyy.cppdef(r"""\
        template<class T>
        T add42(T t) {
            return T(t+42);
        }""")


        def add42(t):
            return type(t)(t+42)

        def go_slow(a):
            trace = 0.0
            for i in range(a.shape[0]):
                trace += add42(a[i, i]) + add42(int(a[i, i]))
            return a + trace

        @numba.jit(nopython=True)
        def go_fast(a):
            trace = 0.0
            for i in range(a.shape[0]):
                trace += cppyy.gbl.add42(a[i, i]) + cppyy.gbl.add42(int(a[i, i]))
            return a + trace

        x = np.arange(100, dtype=np.float64).reshape(10, 10)

        assert (go_fast(x) == go_slow(x)).all()
        assert self.compare(go_slow, go_fast, 100000, x)
