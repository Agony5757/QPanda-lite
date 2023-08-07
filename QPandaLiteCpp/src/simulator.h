#pragma once

#include <iostream>
#include <vector>
#include <complex>
#include "errors.h"

namespace qpandalite {
    using dtype = double;
    using complex_t = std::complex<dtype>;
    constexpr size_t max_qubit_num = 30;

    std::vector<complex_t> init_n_qubit(size_t nqubit);
}
