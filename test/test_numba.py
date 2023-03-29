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

    def test01_instance_box_unbox(self):
        """Access to box/unbox methods"""

        import cppyy

        assert cppyy.addressof('Instance_AsVoidPtr')
        assert cppyy.addressof('Instance_FromVoidPtr')

        with raises(TypeError):
            cppyy.addressof('doesnotexist')

    @mark.xfail
    def test02_method_reflection(self):
        """Method reflection tooling"""

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

    def test03_datamember_reflection(self):
        """Data member reflection tooling"""

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

    @mark.xfail
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

    @mark.xfail
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

    @mark.xfail
    def test03_proxy_argument_for_field(self):
        """Numba-JITing of a free function taking a proxy argument for field access"""

        import cppyy
        import numpy as np

        cppyy.cppdef(r"""\
        struct MyNumbaData03 {
            MyNumbaData03(int64_t i1, int64_t i2) : fField1(i1), fField2(i2) {}
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
        d = cppyy.gbl.MyNumbaData03(42, 27)

        assert((go_fast(x, d) == go_slow(x, d)).all())
        assert self.compare(go_slow, go_fast, 10000, x, d)

    @mark.xfail
    def test04_proxy_argument_for_method(self):
        """Numba-JITing of a free function taking a proxy argument for method access"""

        import cppyy
        import numpy as np

        cppyy.cppdef(r"""\
        struct MyNumbaData04 {
            MyNumbaData04(int64_t i) : fField(i) {}
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
        d = cppyy.gbl.MyNumbaData04(42)

        assert((go_fast(x, d) == go_slow(x, d)).all())
        assert self.compare(go_slow, go_fast, 10000, x, d)

    @mark.xfail
    def test05_datatype_mapping(self):
        """Numba-JITing of various data types"""

        import cppyy

        @numba.jit(nopython=True)
        def access_field(d):
            return d.fField

        code = """\
        namespace NumbaDTT {
        struct M%d { M%d(%s f) : fField(f) {};
             %s buf, fField;
        }; }"""

        cppyy.cppdef("namespace NumbaDTT { }")
        ns = cppyy.gbl.NumbaDTT

        types = (
            # 'int8_t', 'uint8_t',     # TODO b/c check using return type fails
            'short', 'unsigned short', 'int', 'unsigned int',
            'int32_t', 'uint32_t', 'int64_t', 'uint64_t',
            'long', 'unsigned long', 'long long', 'unsigned long long',
            'float', 'double',
        )

        nl = cppyy.gbl.std.numeric_limits
        for i, ntype in enumerate(types):
            cppyy.cppdef(code % (i, i, ntype, ntype))
            for m in ('min', 'max'):
                val = getattr(nl[ntype], m)()
                assert access_field(getattr(ns, 'M%d'%i)(val)) == val

    @mark.xfail
    def test06_object_returns(self):
        """Numba-JITing of a function that returns an object"""

        import cppyy
        import numpy as np

        cppyy.cppdef(r"""\
        struct MyNumbaData06 {
            MyNumbaData06(int64_t i1) : fField(i1) {}
            int64_t fField;
        };

        MyNumbaData06 get_numba_data_06() { return MyNumbaData06(42); }
        """)

        def go_slow(a):
            trace = 0.0
            for i in range(a.shape[0]):
                trace += cppyy.gbl.get_numba_data_06().fField
            return a + trace

        @numba.jit(nopython=True)
        def go_fast(a):
            trace = 0.0
            for i in range(a.shape[0]):
                trace += cppyy.gbl.get_numba_data_06().fField
            return a + trace

        x = np.arange(100, dtype=np.float64).reshape(10, 10)

        assert((go_fast(x) == go_slow(x)).all())
        assert self.compare(go_slow, go_fast, 100000, x)


@mark.skipif(has_numba == False, reason="numba not found")
class TestNUMBA_DOC:
    def setup_class(cls):
        import cppyy
        import cppyy.numba_ext

    @mark.xfail
    def test01_templated_freefunction(self):
        """Numba support documentation example: free templated function"""

        import cppyy
        import numba
        import numpy as np

        cppyy.cppdef("""
        namespace NumbaSupportExample {
        template<typename T>
        T square(T t) { return t*t; }
        }""")

        @numba.jit(nopython=True)
        def tsa(a):
            total = type(a[0])(0)
            for i in range(len(a)):
                total += cppyy.gbl.NumbaSupportExample.square(a[i])
            return total

        a = np.array(range(10), dtype=np.float32)
        assert type(tsa(a)) == float
        assert tsa(a) == 285.0

        a = np.array(range(10), dtype=np.int64)
        assert type(tsa(a)) == int
        assert tsa(a) == 285

    @mark.xfail
    def test02_class_features(self):
        """Numba support documentation example: class features"""

        import cppyy
        import numba
        import numpy as np

        cppyy.cppdef("""\
        namespace NumbaSupportExample {
        class MyData {
        public:
            MyData(int i, int j) : fField1(i), fField2(j) {}
            virtual ~MyData() {}

        public:
            int get_field1() { return fField1; }
            int get_field2() { return fField2; }

            MyData copy() { return *this; }

        public:
            int fField1;
            int fField2;
        }; }""")

        @numba.jit(nopython=True)
        def tsdf(a, d):
            total = type(a[0])(0)
            for i in range(len(a)):
                total += a[i] + d.fField1 + d.fField2
            return total

        d = cppyy.gbl.NumbaSupportExample.MyData(5, 6)
        a = np.array(range(10), dtype=np.int32)

        assert tsdf(a, d) == 155

        @numba.jit(nopython=True)
        def tsdm(a, d):
            total = type(a[0])(0)
            for i in range(len(a)):
                total += a[i] +  d.get_field1() + d.get_field2()
            return total

        assert tsdm(a, d) == 155

        @numba.jit(nopython=True)
        def tsdcm(a, d):
            total = type(a[0])(0)
            for i in range(len(a)):
                total += a[i] + d.copy().fField1 + d.get_field2()
            return total

        assert tsdcm(a, d) == 155

        @numba.jit(nopython=True)
        def tsdcmm(a, d):
            total = type(a[0])(0)
            for i in range(len(a)):
                total += a[i] + d.copy().fField1 + d.copy().fField2
            return total

        assert tsdcmm(a, d) == 155
