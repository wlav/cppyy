#include <string>


//===========================================================================
namespace CrossInheritance {

class Base1 {                // for overridden method checking
public:
    Base1() : m_int(42) {}
    Base1(int i) : m_int(i) {}
    virtual ~Base1();

    virtual int get_value() { return m_int; }
    static int call_get_value(Base1* b);

    virtual int sum_value(int i) { return m_int + i; }
    static int call_sum_value(Base1* b, int);

    virtual int sum_all(int i) { return m_int + i; }
    virtual int sum_all(int i, int j) { return m_int + i + j; }
    static int call_sum_all(Base1* b, int);
    static int call_sum_all(Base1* b, int, int);

public:
    int m_int;
};

class IBase2 {
public:
    IBase2() {}
    virtual ~IBase2() {}
    virtual int get_value() = 0;
    static int call_get_value(IBase2* b);
};

class IBase3 : IBase2 {
public:
    IBase3(int);
};

class CBase2 : public IBase2 {
public:
    int get_value();
};

} // namespace CrossInheritance
