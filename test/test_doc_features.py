import py, os, sys
from pytest import raises


class TestDOCFEATURES:
    def setup_class(cls):
        import cppyy

        cppyy.cppdef("""
#include <iostream>
#include <vector>

unsigned int gUint = 0;

class AbstractClass {
public:
    virtual ~AbstractClass() {}
    virtual void abstract_method() = 0;
};

class ConcreteClass : AbstractClass {
public:
    ConcreteClass(int n=42) : m_int(n), m_const_int(17) {}
    ~ConcreteClass() {}

    virtual void abstract_method() {
        std::cout << "called concrete method" << std::endl;
    }

    void array_method(int* ad, int size) {
        for (int i=0; i < size; ++i)
            std::cout << ad[i] << ' ';
        std::cout << std::endl;
    }

    void array_method(double* ad, int size) {
        for (int i=0; i < size; ++i)
            std::cout << ad[i] << ' ';
        std::cout << std::endl;
    }

    AbstractClass* show_autocast() {
        return this;
    }

    operator const char*() {
        return "Hello operator const char*!";
    }

public:
    double m_data[4];
    int m_int;
    const int m_const_int;
};

namespace Namespace {

    class ConcreteClass {
    public:
        class NestedClass {
        public:
            std::vector<int> m_v;
        };

    };

} // namespace Namespace
""")

    def test_abstract_class(self):
        import cppyy
        from cppyy.gbl import AbstractClass, ConcreteClass

        raises(TypeError, AbstractClass)
        assert issubclass(ConcreteClass, AbstractClass)
        c = ConcreteClass()
        assert isinstance(c, AbstractClass)

    def test_array(self):
        import cppyy
        from cppyy.gbl import ConcreteClass
        from array import array

        c = ConcreteClass()
        c.array_method(array('d', [1., 2., 3., 4.]), 4)
        raises(IndexError, c.m_data.__getitem__, 4)

    def test_builtin_data(self):
        import cppyy

        assert cppyy.gbl.gUint == 0
        raises(ValueError, setattr, cppyy.gbl, 'gUint', -1)
        
    def test_casting(self):
        import cppyy
        from cppyy.gbl import AbstractClass, ConcreteClass

        c = ConcreteClass()
        assert 'AbstractClass' in ConcreteClass.show_autocast.__doc__
        d = c.show_autocast()
        assert type(d) == cppyy.gbl.ConcreteClass

        from cppyy import addressof, bind_object
        e = bind_object(addressof(d), AbstractClass)
        assert type(e) == cppyy.gbl.AbstractClass

    def test_classes_and_structs(self):
        import cppyy
        from cppyy.gbl import ConcreteClass, Namespace

        assert ConcreteClass != Namespace.ConcreteClass
        n = Namespace.ConcreteClass.NestedClass()
        assert 'Namespace.ConcreteClass.NestedClass' in str(type(n))
        assert 'NestedClass' == type(n).__name__
        assert 'cppyy.gbl.Namespace.ConcreteClass' == type(n).__module__
        assert 'Namespace::ConcreteClass::NestedClass' == type(n).__cppname__

    def test_data_members(self):
        import cppyy
        from cppyy.gbl import ConcreteClass

        c = ConcreteClass()
        assert c.m_int == 42
        raises(TypeError, setattr, c, 'm_const_int', 71)

    def test_default_arguments(self):
        import cppyy
        from cppyy.gbl import ConcreteClass

        c = ConcreteClass()
        assert c.m_int == 42
        c = ConcreteClass(13)
        assert c.m_int == 13

    def test_doc_strings(self):
        import cppyy
        from cppyy.gbl import ConcreteClass
        assert 'void ConcreteClass::array_method(int* ad, int size)' in ConcreteClass.array_method.__doc__
        assert 'void ConcreteClass::array_method(double* ad, int size)' in ConcreteClass.array_method.__doc__

    def test_enums(self):
        import cppyy

        pass

    def test_functions(self):
        import cppyy

        pass

    def test_inheritance(self):
        import cppyy

        pass

    def test_memory(self):
        import cppyy
        from cppyy.gbl import ConcreteClass

        c = ConcreteClass()
        assert c.__python_owns__ == True

    def test_methods(self):
        import cppyy

        pass

    def test_namespaces(self):
        import cppyy

        pass

    def test_null(self):
        import cppyy

        assert hasattr(cppyy, 'nullptr')
        assert not cppyy.nullptr

    def test_operator_conversions(self):
        import cppyy
        from cppyy.gbl import ConcreteClass

        assert str(ConcreteClass()) == 'Hello operator const char*!'

    def test_operator_overloads(self):
        import cppyy
        
        pass
        
    def test_pointers(self):
        import cppyy

        pass

    def test_pyobject(self):
        import cppyy

        pass

    def test_static_data_members(self):
        import cppyy

    def test_static_methods(self):
        import cppyy

        pass

    def test_strings(self):
        import cppyy

        pass

    def test_templated_classes(self):
        import cppyy

        assert cppyy.gbl.std.vector
        assert isinstance(cppyy.gbl.std.vector(int), type)
        assert type(cppyy.gbl.std.vector(int)()) == cppyy.gbl.std.vector(int)

    def test_templated_functions(self):
        import cppyy

        pass

    def test_templated_methods(self):
        import cppyy

        pass

    def test_typedefs(self):
        import cppyy

        pass

    def test_unary_operators(sef):
        import cppyy

        pass
