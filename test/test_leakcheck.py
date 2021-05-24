import py, os, sys
from pytest import mark
from .support import setup_make, pylong, pyunicode

currpath = py.path.local(__file__).dirpath()
test_dct = str(currpath.join("datatypesDict"))

def setup_module(mod):
    setup_make("datatypes")

nopsutil = False
try:
    import psutil
except Exception:
    nopsutil = True


@mark.skipif(nopsutil == True, reason="module psutil not installed")
class TestLEAKCHECK:
    def setup_class(cls):
        import cppyy, psutil

        cls.test_dct = test_dct
        cls.memory = cppyy.load_reflection_info(cls.test_dct)

        cls.process = psutil.Process(os.getpid())

    def check_func(self, scope, func, *args, **kwds):
        """Leak-check 'func', given args and kwds"""

        import gc

      # warmup function (TOOD: why doesn't once suffice?)
        for i in range(8):
            getattr(scope, func)(*args, **kwds)

      # define method to run for scoping (iteration can still allocate)
        def runit():
            for i in range(100000):
                getattr(scope, func)(*args, **kwds)

      # leak check
        gc.collect()
        last = self.process.memory_info().rss

        runit()

        gc.collect()
        assert last == self.process.memory_info().rss

    def test01_free_functions(self):
        """Leak test of free functions"""

        import cppyy

        cppyy.cppdef("""\
        namespace LeakCheck {
        void free_f() {}
        void free_f_ol(int) {}
        void free_f_ol(std::string s) {}
        std::string free_f_ret() { return "aap"; }
        template<class T> void free_f_ol(T) {}
        }""")

        ns = cppyy.gbl.LeakCheck

        self.check_func(ns, 'free_f')
        self.check_func(ns, 'free_f_ol', 42)
        self.check_func(ns, 'free_f_ol', '42')
        self.check_func(ns, 'free_f_ol', 42.)
        self.check_func(ns, 'free_f_ret')

    def test02_test_methods(self):
        """Leak test of methods"""

        import cppyy

        cppyy.cppdef("""\
        namespace LeakCheck {
        class MyClass {
        public:
            void method() {}
            void method_ol(int) {}
            void method_ol(std::string s) {}
            std::string method_ret() { return "aap"; }
            template<class T> void method_ol(T) {}
        }; }""")

        ns = cppyy.gbl.LeakCheck

        m = ns.MyClass()
        self.check_func(m, 'method')
        self.check_func(m, 'method_ol', 42)
        self.check_func(m, 'method_ol', '42')
        self.check_func(m, 'method_ol', 42.)
        self.check_func(m, 'method_ret')
