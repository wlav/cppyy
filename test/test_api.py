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

    def test04_custom_converter(self):
        """Custom type converter"""

        import cppyy

        cppyy.cppdef("""
        #include "CPyCppyy/API.h"

        class APICheck3 {
            int fFlags;
        public:
            APICheck3() : fFlags(0) {}
            virtual ~APICheck3() {}

            void setSetArgCalled()     { fFlags |= 0x01; }
            bool wasSetArgCalled()     { return fFlags & 0x01; }
            void setFromMemoryCalled() { fFlags |= 0x02; }
            bool wasFromMemoryCalled() { return fFlags & 0x02; }
            void setToMemoryCalled()   { fFlags |= 0x04; }
            bool wasToMemoryCalled()   { return fFlags & 0x04; }
        };

        class APICheck3Converter : CPyCppyy::Converter {
        public:
            virtual bool SetArg(PyObject* pyobject, CPyCppyy::Parameter&, CPyCppyy::CallContext* = nullptr) {
                APICheck3* a3 = (APICheck3*)CPyCppyy::Instance_AsVoidPtr(pyobject);
                a3->setSetArgCalled();
                return true;
            }

            virtual PyObject* FromMemory(void* address) {
                APICheck3* a3 = (APICheck3*)address;
                a3->setFromMemoryCalled();
                return CPyCppyy::Instance_FromVoidPtr(a3, "APICheck3");
            }

            virtual bool ToMemory(PyObject* value, void* address) {
                APICheck3* a3 = (APICheck3*)address;
                a3->setToMemoryCalled();
                *a3 = *(APICheck3*)CPyCppyy::Instance_AsVoidPtr(value);
                return true;
            }
        };

        typedef CPyCppyy::ConverterFactory_t cf_t;
        void register_a3() {
            CPyCppyy::RegisterConverter("APICheck3",  (cf_t)+[](Py_ssize_t*) { static APICheck3Converter c{}; return &c; });
            CPyCppyy::RegisterConverter("APICheck3&", (cf_t)+[](Py_ssize_t*) { static APICheck3Converter c{}; return &c; });
        }
        void unregister_a3() {
            CPyCppyy::UnregisterConverter("APICheck3");
        }

        APICheck3 gA3a, gA3b;
        void CallWithAPICheck3(APICheck3&) {}
        """)

        cppyy.gbl.register_a3()

        gA3a = cppyy.gbl.gA3a
        assert gA3a
        assert type(gA3a) == cppyy.gbl.APICheck3
        assert gA3a.wasFromMemoryCalled()

        assert not gA3a.wasSetArgCalled()
        cppyy.gbl.CallWithAPICheck3(gA3a)
        assert gA3a.wasSetArgCalled()

        cppyy.gbl.unregister_a3()

        gA3b = cppyy.gbl.gA3b
        assert gA3b
        assert type(gA3b) == cppyy.gbl.APICheck3
        assert not gA3b.wasFromMemoryCalled()
