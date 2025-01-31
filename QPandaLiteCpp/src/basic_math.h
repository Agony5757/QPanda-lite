#pragma once

#include "errors.h"

namespace qpandalite {
    using dtype = double;
    using complex_t = std::complex<dtype>;
    using u22_t = std::array<complex_t, 4>;
    using u44_t = std::array<complex_t, 16>;
    using Kraus1Q = std::vector<u22_t>;
    using Kraus2Q = std::vector<u44_t>;

    constexpr dtype SQRT2 = 1.4142135623730951;
    constexpr dtype INVSQRT2 = 1.0 / SQRT2;
    constexpr dtype eps = 1e-7;

    constexpr unsigned long long pow2(size_t n) { return 1ull << n; }
    
    size_t extract_digit(size_t i, size_t digit);

    size_t extract_digits(size_t index, const std::vector<size_t>& qubits);

    dtype abs_sqr(complex_t c);

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

    constexpr auto val(const u44_t& u, int i, int j)
    {
        constexpr int rowsz = 4;
        int pos = i * rowsz + j;
        return u[pos];
    }

    u22_t matmul(const u22_t& u1, const u22_t& u2);
    u44_t matmul(const u44_t& u1, const u44_t& u2);

    u22_t dag(const u22_t& u);
    u44_t dag(const u44_t& u);

    bool validate_kraus(const std::vector<u22_t>& kraus_ops);
    bool validate_kraus(const std::vector<u44_t>& kraus_ops);

    constexpr u22_t pauli_x{ 0, 1, 1, 0 };
    constexpr u22_t pauli_y{ 0, (0, -1), (0, 1), 0};
    constexpr u22_t pauli_z{ 1, 0, 0, -1 };
    constexpr u22_t pauli_id{ 1, 0, 0, 1 };

    constexpr complex_t operator*(const complex_t& a, const complex_t& b)
    {
        return { a.real() * b.real() - a.imag() * b.imag(), a.real() * b.imag() + a.imag() * b.real() };
    }

    // 编译期计算 2x2 矩阵的 Kronecker 积（张量积）
    constexpr u44_t kronecker_product(const u22_t& a, const u22_t& b) noexcept {
        return { {
                // 第一行: a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]
                a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1],
                // 第二行: a[0] * b[2], a[0] * b[3], a[1] * b[2], a[1] * b[3]
                a[0] * b[2], a[0] * b[3], a[1] * b[2], a[1] * b[3],
                // 第三行: a[2] * b[0], a[2] * b[1], a[3] * b[0], a[3] * b[1]
                a[2] * b[0], a[2] * b[1], a[3] * b[0], a[3] * b[1],
                // 第四行: a[2] * b[2], a[2] * b[3], a[3] * b[2], a[3] * b[3]
                a[2] * b[2], a[2] * b[3], a[3] * b[2], a[3] * b[3]
            } };
    }

    // 生成所有组合：II, IX, IY, IZ, XI, XX, ..., ZZ
    constexpr u44_t pauli_ii = kronecker_product(pauli_id, pauli_id);
    constexpr u44_t pauli_ix = kronecker_product(pauli_id, pauli_x);
    constexpr u44_t pauli_iy = kronecker_product(pauli_id, pauli_y);
    constexpr u44_t pauli_iz = kronecker_product(pauli_id, pauli_z);

    constexpr u44_t pauli_xi = kronecker_product(pauli_x, pauli_id);
    constexpr u44_t pauli_xx = kronecker_product(pauli_x, pauli_x);
    constexpr u44_t pauli_xy = kronecker_product(pauli_x, pauli_y);
    constexpr u44_t pauli_xz = kronecker_product(pauli_x, pauli_z);

    constexpr u44_t pauli_yi = kronecker_product(pauli_y, pauli_id);
    constexpr u44_t pauli_yx = kronecker_product(pauli_y, pauli_x);
    constexpr u44_t pauli_yy = kronecker_product(pauli_y, pauli_y);
    constexpr u44_t pauli_yz = kronecker_product(pauli_y, pauli_z);

    constexpr u44_t pauli_zi = kronecker_product(pauli_z, pauli_id);
    constexpr u44_t pauli_zx = kronecker_product(pauli_z, pauli_x);
    constexpr u44_t pauli_zy = kronecker_product(pauli_z, pauli_y);
    constexpr u44_t pauli_zz = kronecker_product(pauli_z, pauli_z);
}