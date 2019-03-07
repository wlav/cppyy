#include <vector>


namespace CNS {

//===========================================================================
double sumit(const std::vector<double>&);
double sumit(const std::vector<double>&, const std::vector<double>&);

class Counter {
public:
    Counter();
    Counter(const Counter&);
    Counter& operator=(const Counter&);
    ~Counter();

    static int s_count;
};

double howmany(const std::vector<Counter>&);
double howmany(const std::vector<Counter>&, const std::vector<Counter>&);

} // namespace CNS
