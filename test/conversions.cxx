#include "conversions.h"

#include <numeric>


//===========================================================================
double CNS::sumit(const std::vector<double>& v) {
    return std::accumulate(v.begin(), v.end(), 0.);
}

double CNS::sumit(const std::vector<double>& v1, const std::vector<double>& v2) {
    return std::accumulate(v1.begin(), v1.end(), std::accumulate(v2.begin(), v2.end(), 0.));
}

int CNS::Counter::s_count;

CNS::Counter::Counter() {
    ++s_count;
}

CNS::Counter::Counter(const Counter&) {
    ++s_count;
}

CNS::Counter& CNS::Counter::operator=(const Counter&) {
    /* empty */
}

CNS::Counter::~Counter() {
    --s_count;
}

double CNS::howmany(const std::vector<Counter>& v) {
    return v.size();
}

double CNS::howmany(const std::vector<Counter>& v1, const std::vector<Counter>& v2) {
    return v1.size() + v2.size();
}
