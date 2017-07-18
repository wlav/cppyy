File features.h
===============

.. code-block:: C++

    #include <iostream>
    #include <vector>

    //-----
    unsigned int gUint = 0;

    //-----
    class AbstractClass {
    public:
        virtual ~AbstractClass() {}
        virtual void abstract_method() = 0;
    };


    //-----
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
