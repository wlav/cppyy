import py, os, sys
from pytest import raises
from .support import setup_make, IS_WINDOWS


class TestREGRESSION:
    helpout = []

    def setup_class(cls):
        import cppyy

        def stringpager(text, cls=cls):
            cls.helpout.append(text)

        import pydoc
        pydoc.pager = stringpager

    def test01_kdcraw(self):
        """Doc strings for KDcrawIface (used to crash)."""

        import cppyy, pydoc

        # TODO: run a find for these paths
        qtpath = "/usr/include/qt5"
        kdcraw_h = "/usr/include/KF5/KDCRAW/kdcraw/kdcraw.h"
        if not os.path.isdir(qtpath) or not os.path.exists(kdcraw_h):
            py.test.skip("no KDE/Qt found, skipping test01_kdcraw")

        # need to resolve qt_version_tag for the incremental compiler; since
        # it's not otherwise used, just make something up
        cppyy.cppdef("int qt_version_tag = 42;")
        cppyy.add_include_path(qtpath)
        cppyy.include(kdcraw_h)

        # bring in some symbols to resolve the class
        cppyy.load_library("libQt5Core.so")
        cppyy.load_library("libKF5KDcraw.so")

        from cppyy.gbl import KDcrawIface

        self.__class__.helpout = []
        pydoc.doc(KDcrawIface.KDcraw)
        helptext  = ''.join(self.__class__.helpout)
        assert 'KDcraw' in helptext
        assert 'CPPInstance' in helptext

    def test02_dir(self):
        """For the same reasons as test01_kdcraw, this used to crash."""

        import cppyy, pydoc

        assert not '__abstractmethods__' in dir(cppyy.gbl.gInterpreter)
        assert '__class__' in dir(cppyy.gbl.gInterpreter)

        self.__class__.helpout = []
        pydoc.doc(cppyy.gbl.gInterpreter)
        helptext = ''.join(self.__class__.helpout)
        assert 'TInterpreter' in helptext
        assert 'CPPInstance' in helptext
        assert 'AddIncludePath' in helptext

        cppyy.cppdef("namespace cppyy_regression_test { void iii() {}; }")

        assert not 'iii' in cppyy.gbl.cppyy_regression_test.__dict__
        assert not '__abstractmethods__' in dir(cppyy.gbl.cppyy_regression_test)
        assert '__class__' in dir(cppyy.gbl.cppyy_regression_test)
        assert 'iii' in dir(cppyy.gbl.cppyy_regression_test)

        assert not 'iii' in cppyy.gbl.cppyy_regression_test.__dict__
        assert cppyy.gbl.cppyy_regression_test.iii
        assert 'iii' in cppyy.gbl.cppyy_regression_test.__dict__

        self.__class__.helpout = []
        pydoc.doc(cppyy.gbl.cppyy_regression_test)
        helptext = ''.join(self.__class__.helpout)
        # TODO: it's deeply silly that namespaces inherit from CPPInstance (in CPyCppyy)
        assert ('CPPInstance' in helptext or 'CPPNamespace' in helptext)

    def test03_pyfunc_doc(self):
        """Help on a generated pyfunc used to crash."""

        import cppyy, distutils, pydoc, sys
        import distutils.sysconfig as sc

        cppyy.add_include_path(sc.get_python_inc())
        if sys.hexversion < 0x3000000:
            cppyy.cppdef("#undef _POSIX_C_SOURCE")
            cppyy.cppdef("#undef _XOPEN_SOURCE")
        else:
            cppyy.cppdef("#undef slots")     # potentially pulled in by Qt/xapian.h

        cppyy.cppdef("""#include "Python.h"
           long py2long(PyObject* obj) { return PyLong_AsLong(obj); }""")

        pydoc.doc(cppyy.gbl.py2long)

        assert 1 == cppyy.gbl.py2long(1)

    def test04_avx(self):
        """Test usability of AVX by default."""

        import cppyy, subprocess

        has_avx = False
        try:
            f = open('/proc/cpuinfo', 'r')
            for line in f.readlines():
                if 'avx' in line:
                    has_avx = True
                    break
            f.close()
        except Exception:
            try:
                cli_arg = subprocess.check_output(['sysctl', 'machdep.cpu.features'])
                has_avx = 'avx' in cli_arg.decode("utf-8").strip().lower()
            except Exception:
                pass

        if has_avx:
            assert cppyy.cppdef('int check_avx() { return (int) __AVX__; }')
            assert cppyy.gbl.check_avx()   # attribute error if compilation failed

    def test05_default_template_arguments(self):
        """Calling a templated method on a templated class with all defaults used to crash."""

        import cppyy

        cppyy.cppdef("""
        template<typename T>
        class AllDefault {
        public:
           AllDefault(int val) : m_t(val) {}
           template<int aap=1, int noot=2>
              int do_stuff() { return m_t+aap+noot; }

        public:
           T m_t;
        };""")

        a = cppyy.gbl.AllDefault[int](24)
        a.m_t = 21;
        assert a.do_stuff() == 24

    def test06_class_refcounting(self):
        """The memory regulator would leave an additional refcount on classes"""

        import cppyy, gc, sys

        x = cppyy.gbl.std.vector['float']
        old_refcnt = sys.getrefcount(x)

        y = x()
        del y
        gc.collect()

        assert sys.getrefcount(x) == old_refcnt

    def test07_typedef_identity(self):
        """Nested typedefs should retain identity"""

        import cppyy

        cppyy.cppdef("""namespace PyABC {
            struct S1 {};
            struct S2 {
                typedef std::vector<const PyABC::S1*> S1_coll;
            };
        }""")

        from cppyy.gbl import PyABC

        assert PyABC.S2.S1_coll
        assert 'S1_coll' in dir(PyABC.S2)
        assert not 'vector<const PyABC::S1*>' in dir(PyABC.S2)
        assert PyABC.S2.S1_coll is cppyy.gbl.std.vector('const PyABC::S1*')

    def test08_gil_not_released(self):
        """GIL was released by accident for by-value returns"""

        import cppyy

        something = 5.0

        code = """
            #include "Python.h"

            std::vector<float> some_foo_calling_python() {
              auto pyobj = reinterpret_cast<PyObject*>(ADDRESS);
              float f = (float)PyFloat_AsDouble(pyobj);
              std::vector<float> v;
              v.push_back(f);
              return v;
            }
            """.replace("ADDRESS", str(id(something)))

        cppyy.cppdef(code)
        cppyy.gbl.some_foo_calling_python()

    def test09_enum_in_global_space(self):
        """Enum declared in search.h did not appear in global space"""

        if IS_WINDOWS:
            return           # no such enum in MSVC's search.h

        import cppyy

        cppyy.include('search.h')

        assert cppyy.gbl.ACTION
        assert hasattr(cppyy.gbl, 'ENTER')
        assert hasattr(cppyy.gbl, 'FIND')

    def test10_cobject_addressing(self):
        """AsCObject (now as_cobject) had a deref too many"""

        import cppyy
        import cppyy.ll

        cppyy.cppdef('struct CObjA { CObjA() : m_int(42) {} int m_int; };')
        a = cppyy.gbl.CObjA()
        co = cppyy.ll.as_cobject(a)

        assert a == cppyy.bind_object(co, 'CObjA')
        assert a.m_int == 42
        assert cppyy.bind_object(co, 'CObjA').m_int == 42

    def test11_exception_while_exception(self):
        """Exception from SetDetailedException during exception handling used to crash"""

        import cppyy

        cppyy.cppdef("namespace AnExceptionNamespace { }")

        try:
            cppyy.gbl.blabla
        except AttributeError:
            try:
                cppyy.gbl.AnExceptionNamespace.blabla
            except AttributeError:
                pass

    def test12_char_star_over_char(self):
        """Map str to const char* over char"""

      # This is debatable, but although a single character string passes through char,
      # it is more consistent to prefer const char* or std::string in all cases. The
      # original bug report is here:
      #    https://bitbucket.org/wlav/cppyy/issues/127/string-argument-resolves-incorrectly

        import cppyy

        cppyy.cppdef("""
        namespace csoc1 {
            std::string call(char) { return "char"; }
        }

        namespace csoc2 {
            std::string call(char) { return "char"; }
            std::string call(const char*) { return "const char*"; }
        }

        namespace csoc3 {
            std::string call(char) { return "char"; }
            std::string call(const std::string&) { return "string"; }
        }
        """)

        assert cppyy.gbl.csoc1.call('0') == 'char'
        raises(ValueError, cppyy.gbl.csoc1.call, '00')

        assert cppyy.gbl.csoc2.call('0')  == 'const char*'
        assert cppyy.gbl.csoc2.call('00') == 'const char*'

        assert cppyy.gbl.csoc3.call('0')  == 'string'
        assert cppyy.gbl.csoc3.call('00') == 'string'

    def test13_struct_direct_definition(self):
        """Struct defined directly in a scope miseed scope in renormalized name"""

        import cppyy

        cppyy.cppdef("""
        namespace struct_direct_definition {
        struct Bar {
            struct Baz {
                std::vector<double> data;
            } baz[2];

            Bar() {
                baz[0].data.push_back(3.14);
                baz[1].data.push_back(2.73);
            }
        };

        class Foo {
        public:
            class Bar {
            public:
                Bar(): x(5) {}
                int x;
            } bar;

        }; }""")

        from cppyy.gbl import struct_direct_definition as sds

        b = sds.Bar()

        assert len(b.baz) == 2
        assert len(b.baz[0].data) == 1
        assert b.baz[0].data[0]   == 3.14
        assert len(b.baz[1].data) == 1
        assert b.baz[1].data[0]   == 2.73

        f = sds.Foo()
        assert f.bar.x == 5

    def test14_vector_vs_initializer_list(self):
        """Prefer vector in template and initializer_list in formal arguments"""

        import cppyy

        cppyy.cppdef("""
        namespace vec_vs_init {
           template<class T>
           std::string nameit1(const T& t) {
               return typeid(T).name();
           }
           template<class T>
           std::string nameit2(T&& t) {
               return typeid(T).name();
           }
           template<class T>
           size_t sizeit(T&& t) {
               return t.size();
           }
        }""")

        nameit1 = cppyy.gbl.vec_vs_init.nameit1
        assert 'vector' in nameit1(list(range(10)))
        assert 'vector' in nameit1(cppyy.gbl.std.vector[int]())

        nameit2 = cppyy.gbl.vec_vs_init.nameit2
        assert 'vector' in nameit2(list(range(10)))
        assert 'vector' in nameit2(cppyy.gbl.std.vector[int]())

        sizeit = cppyy.gbl.vec_vs_init.sizeit
        assert sizeit(list(range(10))) == 10

    def test15_iterable_enum(self):
        """Use template to iterate over an enum"""
      # from: https://stackoverflow.com/questions/52459530/pybind11-emulate-python-enum-behaviour

        import cppyy

        cppyy.cppdef("""
        template <typename Enum>
        struct my_iter_enum {
            struct iterator {
                using value_type = Enum;
                using difference_type = ptrdiff_t;
                using reference = const Enum&;
                using pointer = const Enum*;
                using iterator_category = std::input_iterator_tag;

                iterator(Enum value) : cur(value) {}

                reference operator*() { return cur; }
                pointer operator->() { return &cur; }
                bool operator==(const iterator& other) { return cur == other.cur; }
                bool operator!=(const iterator& other) { return !(*this == other); }
                iterator& operator++() { if (cur != Enum::Unknown) cur = static_cast<Enum>(static_cast<std::underlying_type_t<Enum>>(cur) + 1); return *this; }
                iterator operator++(int) { iterator other = *this; ++(*this); return other; }

            private:
                Enum cur;
                int TODO_why_is_this_placeholder_needed; // JIT error? Too aggressive optimization?
            };

            iterator begin() {
                return iterator(Enum::Black);
            }

            iterator end() {
                return iterator(Enum::Unknown);
            }
        };

        enum class MyColorEnum : char {
            Black = 1,
            Blue,
            Red,
            Yellow,
            Unknown
        };""")

        Color = cppyy.gbl.my_iter_enum['MyColorEnum']
        assert Color.iterator

        c_iterable = Color()
        assert c_iterable.begin().__deref__() == chr(1)

        all_enums = []
        for c in c_iterable:
            all_enums.append(ord(c))
        assert all_enums == list(range(1, 5))

    def test16_operator_eq_pickup(self):
        """Base class python-side operator== interered with derived one"""

        import cppyy

        cppyy.cppdef("""
        namespace SelectOpEq {
        class Base {};

        class Derived1 : public Base {
        public:
            bool operator==(Derived1&) { return true; }
        };

        class Derived2 : public Base {
        public:
            bool operator!=(Derived2&) { return true; }
        }; }""")

        soe = cppyy.gbl.SelectOpEq

        soe.Base.__eq__ = lambda first, second: False
        soe.Base.__ne__ = lambda first, second: False

        a = soe.Derived1()
        b = soe.Derived1()

        assert a == b             # derived class' C++ operator== called

        a = soe.Derived2()
        b = soe.Derived2()

        assert a != b             # derived class' C++ operator!= called

    def test17_operator_plus_overloads(self):
        """operator+(string, string) should return a string"""

        import cppyy

        a = cppyy.gbl.std.string("a")
        b = cppyy.gbl.std.string("b")

        assert a == 'a'
        assert b == 'b'

        assert type(a+b) == str
        assert a+b == 'ab'

    def test18_std_string_hash(self):
        """Hashing of std::string"""

        import cppyy

        import cppyy

        s = cppyy.gbl.std.string("text")
        d = {}

      # hashes of std::string larger than 2**31 would fail; run a couple of
      # strings to check although it may still succeed by accident (and never
      # was an issue on p3 anyway)
        for s in ['abc', 'text', '321', 'stuff', 'very long string']:
            d[s] = 1

    def test19_signed_char_ref(self):
        """Signed char executor was self-referencing"""

        import cppyy

        cppyy.cppdef("""
        class SignedCharRefGetter {
        public:
            void setter(signed char sc) { m_c = sc; }
            signed char& getter() { return m_c; }
            signed char m_c;
        };""")

        obj = cppyy.gbl.SignedCharRefGetter()
        obj.setter('c')

        assert obj.getter() == 'c'

    def test20_temporaries_and_vector(self):
        """Extend a life line to references into a vector if needed"""

        import cppyy

        cppyy.cppdef("""
            std::vector<std::string> get_some_temporary_vector() { return { "x", "y", "z" }; }
        """)

        l = [e for e in cppyy.gbl.get_some_temporary_vector()]
        assert l == ['x', 'y', 'z']

    def test21_initializer_list_and_temporary(self):
        """Conversion rules when selecting intializer_list v.s. temporary"""

        import cppyy

        cppyy.cppdef("""\
        namespace regression_test21 {
        std::string what_called = "";
        class Foo {
        public:
            Foo() = default;
            Foo(int i) {
                what_called += "Foo(int)";
            }
            Foo(std::initializer_list<uint8_t> il) {
                std::ostringstream os;
                os << "Foo(il<size=" << il.size() << ">)";
                what_called += os.str();
            }
        };

        class Bar {
        public:
            Bar() = default;
            Bar(int i) {
                what_called = "Bar(int)";
            }
            Bar(std::initializer_list<uint8_t> il) {
                std::ostringstream os;
                os << "Bar(il<size=" << il.size() << ">)";
                what_called += os.str();
            }
            Bar(Foo x) {
                what_called += "Bar(Foo)";
            }
        }; }""")

        r21 = cppyy.gbl.regression_test21

        assert len(r21.what_called) == 0

        r21.Bar(1)
        assert r21.what_called == 'Bar(int)'

        r21.what_called = ''
        r21.Bar([1,2])  # used to call Bar(Foo x) through implicit conversion
        assert r21.what_called == 'Bar(il<size=2>)'

    def test22_copy_constructor(self):
        """Copy construct an object into an empty (NULL) proxy"""

        import cppyy, gc

        cppyy.cppdef("""\
        namespace regression_test22 {
        struct Countable {
            static int s_count;
            Countable() { ++s_count; }
            Countable(const Countable&) { ++s_count; }
            Countable& operator=(const Countable&) { return *this; }
            ~Countable() { --s_count; }
        };
        int Countable::s_count = 0;

        Countable copy_creation() { return Countable{}; }
        Countable* c;
        void destroyit() { delete c; }
        }""")

        r22 = cppyy.gbl.regression_test22

        assert r22.Countable.s_count == 0
        c = r22.Countable()
        assert r22.Countable.s_count == 1

        raises(ReferenceError, c.__init__, r22.Countable())
        gc.collect()
        assert r22.Countable.s_count == 1

        c.__assign__(r22.Countable())
        gc.collect()
        assert r22.Countable.s_count == 1

        c.__destruct__()
        assert r22.Countable.s_count == 0
        c.__init__(r22.Countable())
        gc.collect()
        assert r22.Countable.s_count == 1

        del c
        gc.collect()
        assert r22.Countable.s_count == 0

        c = cppyy.bind_object(cppyy.nullptr, r22.Countable)
        assert r22.Countable.s_count == 0
        c.__init__(r22.Countable())
        gc.collect()
        assert r22.Countable.s_count == 1

        del c
        gc.collect()
        assert r22.Countable.s_count == 0

        c = r22.copy_creation()
        assert r22.Countable.s_count == 1
        del c
        gc.collect()
        assert r22.Countable.s_count == 0

        c = r22.copy_creation()
        r22.c = c
        c.__python_owns__ = False
        del c
        gc.collect()
        assert r22.Countable.s_count == 1

        r22.destroyit()
        r22.c = cppyy.nullptr
        assert r22.Countable.s_count == 0

    def test23_C_style_enum(self):
        """Support C-style enum variable declarations"""

        import cppyy

        cppyy.cppdef("""\
        namespace CStyleEnum {
           enum MyEnum { kOne, kTwo };
           MyEnum my_enum = kOne;

           enum YourEnum { kThree, kFour };
           enum YourEnum your_enum = kThree;
        }""")

        CSE = cppyy.gbl.CStyleEnum

        assert CSE.my_enum == CSE.MyEnum.kOne
        CSE.my_enum = CSE.MyEnum.kTwo
        assert CSE.my_enum == CSE.MyEnum.kTwo

      # the following would fail b/c the type was not properly resolved
        assert CSE.your_enum == CSE.YourEnum.kThree
        CSE.your_enum = CSE.YourEnum.kFour
        assert CSE.your_enum == CSE.YourEnum.kFour

    def test24_const_iterator(self):
        """const_iterator failed to resolve the proper return type"""

        import cppyy

        cppyy.cppdef("""\
        namespace RooStuff {
        struct RooArg {};

        struct RooCollection {
            using const_iterator = std::vector<RooArg*>::const_iterator;
            std::vector<RooArg*> _list;

            RooCollection() { _list.emplace_back(); }
            const_iterator begin() const { return _list.begin(); }
            const_iterator end() const { return _list.end(); }
        }; }""")

        l = cppyy.gbl.RooStuff.RooCollection()

        i = 0
        for e in l:
            assert type(e) == cppyy.gbl.RooStuff.RooArg
            i += 1
        assert i

    def test25_const_charptr_data(self):
        """const char* is not const; const char* const is"""

        import cppyy

        cppyy.cppdef("""
        namespace ConstCharStar {
        struct ImGuiIO1 {
            ImGuiIO1() : BackendPlatformName(nullptr) {}
            const char* BackendPlatformName;
        };
        struct ImGuiIO2 {
            ImGuiIO2() : BackendPlatformName(nullptr) {}
            const char* const BackendPlatformName;
        }; }""")

        io = cppyy.gbl.ConstCharStar.ImGuiIO1()

        io.BackendPlatformName = "aap"
        assert io.BackendPlatformName == "aap"

        io.BackendPlatformName = "aap\0noot"
        io.BackendPlatformName = "aap\0noot"

        io = cppyy.gbl.ConstCharStar.ImGuiIO2()
        with raises(TypeError):
            io.BackendPlatformName = "aap"

    def test26_exception_by_value(self):
        """Proper memory management of exception return by value"""

        import cppyy, gc

        cppyy.cppdef("""\
        namespace ExceptionByValue {
        class Countable : std::exception {
        public:
            static int s_count;
            Countable() : fMsg("error") { ++s_count; }
            Countable(const Countable&) { ++s_count; }
            Countable& operator=(const Countable&) { return *this; }
            ~Countable() { --s_count; }
            const char* what() const throw() override { return fMsg.c_str(); }
        private:
            std::string fMsg;
        };

        int Countable::s_count = 0;

        Countable create_one() { return Countable{}; }
        int count() { return Countable::s_count; }
        }""")

        ns = cppyy.gbl.ExceptionByValue

        assert ns.count() == 0
        c = ns.create_one()
        assert ns.count() == 1

        del c
        gc.collect()
        assert ns.count() == 0

    def test27_exception_as_shared_ptr(self):
        """shared_ptr of an exception object null-checking"""

        import cppyy

        cppyy.cppdef("""\
        namespace exception_as_shared_ptr {
            std::shared_ptr<std::exception> get_shared_null() {
                return std::shared_ptr<std::exception>();
            }
        }""")

        null = cppyy.gbl.exception_as_shared_ptr.get_shared_null()
        assert not null

    def test28_callback_pointer_values(self):
        """Make sure pointer comparisons in callbacks work as expected"""

        import cppyy

        cppyy.cppdef("""\
        namespace addressof_regression {
        class ChangeBroadcaster;

        class ChangeListener {
        public:
            virtual ~ChangeListener() = default;
            virtual void changeCallback(ChangeBroadcaster*) = 0;
        };

        class ChangeBroadcaster {
        public:
            virtual ~ChangeBroadcaster() = default;
            void triggerChange() {
                std::for_each(l.begin(), l.end(), [this](auto* p) { p->changeCallback(this); });
            }

            void addChangeListener(ChangeListener* x) {
                l.push_back(x);
            }

        private:
            std::vector<ChangeListener*> l;
        };

        class BaseClass {
        public:
            virtual ~BaseClass() = default;
        };

        class DerivedClass : public BaseClass, public ChangeBroadcaster {
            /* empty */
        };

        class Implementation {
        public:
            Implementation() { }
            virtual ~Implementation() = default;
            DerivedClass derived;
        }; }""")

        ns = cppyy.gbl.addressof_regression

        class Glue(cppyy.multi(ns.Implementation, ns.ChangeListener)):
            def __init__(self):
                super(ns.Implementation, self).__init__()
                self.derived.addChangeListener(self)
                self.success = False

            def triggerChange(self):
                self.derived.triggerChange()

            def changeCallback(self, b):
                assert type(b) == type(self.derived)
                assert b == self.derived
                cast = cppyy.gbl.std.addressof[type(b)]
                assert cast(b) == cast(self.derived)
                self.success = True

        g = Glue()
        assert not g.success

        g.triggerChange()
        assert g.success

    def test29_float2d_callback(self):
        """Passing of 2-dim float arguments"""

        import cppyy

        cppyy.cppdef("""\
        namespace FloatDim2 {
        #include <thread>

        struct Buffer {
            Buffer() = default;

            void setData(float** newData) {
                data = newData;
            }

            void setSample(int newChannel, int newSample, float value) {
                data[newChannel][newSample] = value;
            }

            float** data = nullptr;
        };

        struct Processor {
            virtual ~Processor() = default;
            virtual void process(float** data, int channels, int samples) = 0;
        };

        void callback(Processor& p) {
            std::thread t([&p] {
                int channels = 2;
                int samples = 32;

                float** data = new float*[channels];
                for (int i = 0; i < channels; ++i)
                    data[i] = new float[samples];

                p.process(data, channels, samples);

                for (int i = 0; i < channels; ++i)
                    delete[] data[i];

                delete[] data;
            });

            t.join();
        } }""")

        cppyy.gbl.FloatDim2.callback.__release_gil__ = True

        class Processor(cppyy.gbl.FloatDim2.Processor):
            buffer = cppyy.gbl.FloatDim2.Buffer()

            def process(self, data, channels, samples):
                self.buffer.setData(data)

                try:
                    for c in range(channels):
                        for s in range(samples):
                            self.buffer.setSample(c, s, 0.0) # < used to crash here
                except Exception as e:
                    print(e)

        p = Processor()
        cppyy.gbl.FloatDim2.callback(p)

    def test30_uint64_t(self):
        """Failure due to typo"""

        import cppyy

        cppyy.cppdef("""\
        #include <limits>
        namespace UInt64_Typo {
            uint64_t Test(uint64_t v) { return v; }
            template <typename T> struct Struct { Struct(T t) : fT(t) {}; T fT; };
            template <typename T> Struct<T> TTest(T t) { return Struct<T>{t}; }
        }""")

        from cppyy.gbl import UInt64_Typo as ns

        std = cppyy.gbl.std
        uint64_t = cppyy.gbl.uint64_t
        umax64   = std.numeric_limits[uint64_t].max()
        int64_t  = cppyy.gbl.int64_t
        max64    = std.numeric_limits[int64_t].max()
        min64    = std.numeric_limits[int64_t].min()

        assert max64 < umax64
        assert min64 < max64
        assert umax64 == ns.Test(umax64)

        assert ns.TTest(umax64).fT == umax64
        assert ns.TTest(max64).fT  ==  max64
        assert ns.TTest(min64).fT  ==  min64
        assert ns.TTest(1.01).fT == 1.01
        assert ns.TTest(True).fT == True
        assert type(ns.TTest(True).fT) == bool

    def test31_enum_in_dir(self):
        """Failed to pick up enum data"""

        import cppyy

        cppyy.cppdef("""\
        namespace enum_in_dir {
            long prod (long a, long b) { return a * b; }
            long prod (long a, long b, long c) { return a * b * c; }

            int a = 10;
            int b = 40;

            enum smth { ONE, };
            enum smth my_enum = smth::ONE;
        }""")

        all_names = set(dir(cppyy.gbl.enum_in_dir))

        required = {'prod', 'a', 'b', 'smth', 'my_enum'}
        assert all_names.intersection(required) == required

    def test32_explicit_template_in_namespace(self):
        """Lookup of explicit template in namespace"""

        import cppyy

        cppyy.cppdef("""\
        namespace libchemist {
        namespace type {
            template<typename T> class tensor {};
        } // namespace type

        template<typename element_type = double, typename tensor_type = type::tensor<element_type>>
        class CanonicalMO {};

        template class CanonicalMO<double, type::tensor<double>>;
        } // namespace libchemist

        namespace property_types {
        namespace type {
            template<typename T>
            using canonical_mos = libchemist::CanonicalMO<T>;
        } } // namespace type, property_types""")

        assert cppyy.gbl.property_types.type.canonical_mos['double']
