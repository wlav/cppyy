import py, os, sys
from pytest import raises

try:
    import __pypy__
    is_pypy = True
except ImportError:
    is_pypy = False


class TestAPI:
    def setup_class(cls):
        if is_pypy:
            py.test.skip('C++ API only available on CPython')

        import cppyy
        cppyy.include('CPyCppyy/API.h')

    def test01_type_checking(self):
        """Python class type checks"""

        import cppyy
        cpp = cppyy.gbl
        API = cpp.CPyCppyy

        cppyy.cppdef("""
        class APICheck {
        public:
          void some_method() {}
        };""")

        assert API.Scope_Check(cpp.APICheck)
        assert not API.Scope_CheckExact(cpp.APICheck)

        a = cpp.APICheck()
        assert API.Instance_Check(a)
        assert not API.Instance_CheckExact(a)

        m = a.some_method
        assert API.Overload_Check(m)
        assert API.Overload_CheckExact(m)

    def test02_interpreter_access(self):
        """Access to the python interpreter"""

        import cppyy
        API = cppyy.gbl.CPyCppyy

        assert API.Exec('import sys')

    def test03_instance_conversion(self):
        """Proxy object conversions"""

        import cppyy
        cpp = cppyy.gbl
        API = cpp.CPyCppyy

        cppyy.cppdef("""
        class APICheck2 {
        public:
          virtual ~APICheck2() {}
        };""")

        m = cpp.APICheck2()

        voidp = API.Instance_AsVoidPtr(m)
        m2 = API.Instance_FromVoidPtr(voidp, 'APICheck2')
        assert m is m2
