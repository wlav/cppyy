#include "functioncalls.h"

#include <math.h>


//- group: empty -------------------------------------------------------------
void empty_call() {
/* empty, to measure pure call overhead */
}

void EmptyCall::empty_call() {
/* empty, to measure pure call overhead */
}


//- group: builtin-args ------------------------------------------------------
void take_an_int(int /* unused */) {
/* empty, to measure pure call overhead */
}

void take_a_double(double /* unused */) {
/* empty, to measure pure call overhead */
}

void TakeAValue::take_an_int(int /* unused */) {
/* empty, to measure pure call overhead */
}

void TakeAValue::take_a_double(double /* unused */) {
/* empty, to measure pure call overhead */
}


//- group: do-work -----------------------------------------------------------
double do_work(double arg) {
    return atan(arg);
}

double DoWork::do_work(double arg) {
    return atan(arg);
}
