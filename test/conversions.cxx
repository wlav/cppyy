#include "conversions.h"

#include <numeric>


//===========================================================================
double CNS::sumit(const std::vector<double>& vec) {
    return std::accumulate(vec.begin(), vec.end(), 0.);
}
