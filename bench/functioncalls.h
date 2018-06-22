#ifndef CPPYY_FUNCTIONCALLS_H
#define CPPYY_FUNCTIONCALLS_H

//- group: empty -------------------------------------------------------------
void empty_call();

class EmptyCall {
public:
    void empty_call();
};

//- group: builtin-args ------------------------------------------------------
void take_an_int(int);
void take_a_double(double);

class TakeAValue {
public:
    void take_an_int(int);
    void take_a_double(double);
};

//- group: do-work -----------------------------------------------------------
double do_work(double);

class DoWork {
public:
    double do_work(double);
};

#endif // !CPPYY_FUNCTIONCALLS_H
