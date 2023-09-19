#pragma once

#include <array>
#include <complex>
#include <iostream>
#include <vector>

#include "errors.h"

namespace qpandalite {
    using dtype = double;
    using complex_t = std::complex<dtype>;
    constexpr dtype SQRT2 = 1.4142135623730951;
    constexpr dtype INVSQRT2 = 1.0 / SQRT2;
    
    constexpr unsigned long long pow2(size_t n) { return 1ull << n; }
    constexpr auto abs_sqr(complex_t c)
    {
        return c.real() * c.real() + c.imag() * c.imag();
    }

    struct Simulator
    { 
        static constexpr size_t max_qubit_num = 30;
        size_t total_qubit;
        std::vector<complex_t> state;

        void init_n_qubit(size_t nqubit);
        void hadamard(size_t qn);
        void u22(size_t qn, const std::array<complex_t, 4> &unitary);
        void x(size_t qn);
        void z(size_t qn);
        void cz(size_t qn1, size_t qn2);
        void cnot(size_t controller, size_t target);

        void get_prob(const std::map<size_t, int> &measure_qubits);
        void get_prob(size_t qn, int state);
    };
}
