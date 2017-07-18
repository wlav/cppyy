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

print 'abstract class'
from cppyy.gbl import AbstractClass, ConcreteClass
try:
   a = AbstractClass()
   raise RuntimeError("failed to raise TypeError")
except TypeError:
   pass
assert issubclass(ConcreteClass, AbstractClass) == True
c = ConcreteClass()
assert isinstance(c, AbstractClass) == True

print 'array (should print "1 2 3 4")'
from cppyy.gbl import ConcreteClass
from array import array
c = ConcreteClass()
c.array_method(array('d', [1., 2., 3., 4.]), 4)
try:
   c.m_data[4] # out of bounds
   raise RuntimeError("failed to raise IndexError")
except IndexError:
   pass

print 'builtin data types'
assert cppyy.gbl.gUint == 0
try:
   cppyy.gbl.gUint = -1
   raise RuntimeError("failed to raise ValueError")
except ValueError:
   pass

print 'casting'
from cppyy.gbl import AbstractClass, ConcreteClass
c = ConcreteClass()
assert 'AbstractClass' in ConcreteClass.show_autocast.__doc__
d = c.show_autocast()
assert type(d) == cppyy.gbl.ConcreteClass

from cppyy import addressof, bind_object
e = bind_object(addressof(d), AbstractClass)
assert type(e) == cppyy.gbl.AbstractClass

print 'classes and structs'
from cppyy.gbl import ConcreteClass, Namespace
assert ConcreteClass != Namespace.ConcreteClass
n = Namespace.ConcreteClass.NestedClass()
assert 'Namespace::ConcreteClass::NestedClass' in str(type(n))

print 'data members'
from cppyy.gbl import ConcreteClass
c = ConcreteClass()
assert c.m_int == 42
try:
   c.m_const_int = 71
   raise RuntimeError("failed to raise TypeError")
except TypeError:
   pass
