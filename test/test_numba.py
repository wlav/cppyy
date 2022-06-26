import py, os, sys
import math, time
from pytest import mark, raises
from .support import setup_make

try:
    import numba
    has_numba = True
except ImportError:
    has_numba = False


class TestREFLEX:
    def setup_class(cls):
        import cppyy
        import cppyy.reflex

    def test01_method_reflection(self):
        """Test method reflection tooling"""

        import cppyy
        import cppyy.reflex as r

        cppyy.cppdef("""\
        namespace ReflexTest {
        int free1() { return 42; }
        double free2() { return 42.; }

        class MyData_m1 {};
        }""")

        ns = cppyy.gbl.ReflexTest

        assert ns.free1.__cpp_reflex__(r.RETURN_TYPE) == 'int'
        assert ns.free2.__cpp_reflex__(r.RETURN_TYPE) == 'double'

        assert ns.MyData_m1.__init__.__cpp_reflex__(r.RETURN_TYPE)              == ns.MyData_m1
        assert ns.MyData_m1.__init__.__cpp_reflex__(r.RETURN_TYPE, r.OPTIMAL)   == ns.MyData_m1
        assert ns.MyData_m1.__init__.__cpp_reflex__(r.RETURN_TYPE, r.AS_TYPE)   == ns.MyData_m1
        assert ns.MyData_m1.__init__.__cpp_reflex__(r.RETURN_TYPE, r.AS_STRING) == 'ReflexTest::MyData_m1'

    def test02_datamember_reflection(self):
        """Test data member reflection tooling"""

        import cppyy
        import cppyy.reflex as r

        cppyy.cppdef("""\
        namespace ReflexTest {
        class MyData_d1 {
        public:
           int    m_int;
           double m_double;
        }; }""")

        ns = cppyy.gbl.ReflexTest

        assert ns.MyData_d1.__dict__['m_int'].__cpp_reflex__(r.TYPE)    == 'int'
        assert ns.MyData_d1.__dict__['m_double'].__cpp_reflex__(r.TYPE) == 'double'

        d = ns.MyData_d1(); daddr = cppyy.addressof(d)
        assert ns.MyData_d1.__dict__['m_int'].__cpp_reflex__(r.OFFSET)    == 0
        assert ns.MyData_d1.__dict__['m_double'].__cpp_reflex__(r.OFFSET) == cppyy.addressof(d, 'm_double') - daddr


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
        """Numba-JITing of a compiled free function"""

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
        """Numba-JITing of Cling-JITed templated free function"""

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

    def test03_proxy_argument_for_field(self):
        """Numba-JITing of a free function taking a proxy argument for field access"""

        import cppyy
        import numpy as np

        cppyy.cppdef(r"""\
        struct MyNumbaData1 {
            MyNumbaData1(int64_t i1, int64_t i2) : fField1(i1), fField2(i2) {}
            int64_t fField1;
            int64_t fField2;
        };""")

        def go_slow(a, d):
            trace = 0.0
            for i in range(a.shape[0]):
                trace += d.fField1 + d.fField2
            return a + trace

        @numba.jit(nopython=True)
        def go_fast(a, d):
            trace = 0.0
            for i in range(a.shape[0]):
                trace += d.fField1 + d.fField2
            return a + trace

      # note: need a sizable array to outperform given the unboxing overhead
        x = np.arange(10000, dtype=np.float64).reshape(100, 100)
        d = cppyy.gbl.MyNumbaData1(42, 27)

        assert((go_fast(x, d) == go_slow(x, d)).all())
        assert self.compare(go_slow, go_fast, 10000, x, d)

    def test04_proxy_argument_for_method(self):
        """Numba-JITing of a free function taking a proxy argument for method access"""

        import cppyy
        import numpy as np

        cppyy.cppdef(r"""\
        struct MyNumbaData2 {
            MyNumbaData2(int64_t i) : fField(i) {}
            int64_t get_field() { return fField; }
            int64_t fField;
        };""")

        def go_slow(a, d):
            trace = 0.0
            for i in range(a.shape[0]):
                trace += d.get_field()
            return a + trace

        @numba.jit(nopython=True)
        def go_fast(a, d):
            trace = 0.0
            for i in range(a.shape[0]):
                trace += d.get_field()
            return a + trace

      # note: need a sizable array to outperform given the unboxing overhead
        x = np.arange(10000, dtype=np.float64).reshape(100, 100)
        d = cppyy.gbl.MyNumbaData2(42)

        assert((go_fast(x, d) == go_slow(x, d)).all())
        assert self.compare(go_slow, go_fast, 10000, x, d)

