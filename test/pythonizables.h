#include <memory>


namespace pyzables {

//===========================================================================
class NakedBuffers {
public:
    NakedBuffers(int size, double valx, double valy);
    NakedBuffers(const NakedBuffers&) = delete;
    NakedBuffers& operator=(const NakedBuffers&) = delete;
    ~NakedBuffers();

public:
    int GetN();
    double* GetX();
    double* GetY();

private:
    double* m_Xbuf;
    double* m_Ybuf;
    int m_size;
};


//===========================================================================
class MyBase {
public:
    virtual ~MyBase();
};
class MyDerived : public MyBase {
public:
    virtual ~MyDerived();
};

MyBase* GimeDerived();


//===========================================================================
class Countable {
public:
    Countable() { ++sInstances; }
    Countable(const Countable&) { ++sInstances; }
    Countable& operator=(const Countable&) { return *this; }
    ~Countable() { --sInstances; }

public:
    virtual const char* say_hi() { return "Hi!"; }

public:
    static int sInstances;
};

typedef std::shared_ptr<Countable> SharedCountable_t; 
extern SharedCountable_t mine;

void renew_mine();

SharedCountable_t gime_mine();
SharedCountable_t* gime_mine_ptr();
SharedCountable_t& gime_mine_ref();

void pass_mine_sp(SharedCountable_t p);
void pass_mine_sp_ref(SharedCountable_t& p);
void pass_mine_sp_ptr(SharedCountable_t* p);

void pass_mine_rp(Countable);
void pass_mine_rp_ref(const Countable&);
void pass_mine_rp_ptr(const Countable*);

} // namespace pyzables
