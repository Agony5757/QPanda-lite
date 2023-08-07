#include "simulator.h"

namespace qpandalite{
    std::vector<complex_t> init_n_qubit(size_t nqubit)
    {
        if (nqubit > max_qubit_num)
            ThrowRuntimeError(fmt::format("Exceed max_qubit_num (nqubit = {}, limit = {})", nqubit, max_qubit_num));

        std::vector<complex_t> ret(1ull << nqubit, 0);
        ret[0] = 1;
        return ret;
    }
}