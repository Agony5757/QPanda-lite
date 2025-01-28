#pragma once

#include "errors.h"

namespace qpandalite {
    using dtype = double;
    using complex_t = std::complex<dtype>;
    using u22_t = std::array<complex_t, 4>;
    using Kraus1Q = std::vector<u22_t>;

    constexpr dtype SQRT2 = 1.4142135623730951;
    constexpr dtype INVSQRT2 = 1.0 / SQRT2;
    constexpr dtype eps = 1e-7;

    constexpr unsigned long long pow2(size_t n) { return 1ull << n; }
    constexpr auto abs_sqr(complex_t c)
    {
        return std::norm(c);
    }

    constexpr auto float_equal(dtype a, dtype b)
    {
        dtype compare = a - b;
        if (compare > eps) return false;
        if (compare < -eps) return false;
        return true;
    }

    constexpr auto complex_equal(complex_t a, complex_t b)
    {
        dtype compare_real = a.real() - b.real();
        if (compare_real > eps) return false;
        if (compare_real < -eps) return false;

        dtype compare_imag = a.imag() - b.imag();
        if (compare_imag > eps) return false;
        if (compare_imag < -eps) return false;
        return true;
    }

    bool _assert_u22(const u22_t& u);

    constexpr auto val(const u22_t& u, int i, int j)
    {
        constexpr int rowsz = 2;
        int pos = i * rowsz + j;
        return u[pos];
    }

    u22_t matmul(const u22_t& u1, const u22_t& u2);

    u22_t dag(const u22_t& u);

    bool validate_kraus(const std::vector<u22_t>& kraus_ops);
}