﻿#include "basic_math.h"

namespace qpandalite
{
    size_t extract_digit(size_t i, size_t digit)
    {
        return (i >> digit) & 1;
    }
    size_t extract_digits(size_t index, const std::vector<size_t>& qubits)
    {
        size_t ret = 0;
        for (int i = 0; i < qubits.size(); ++i)
        {
            size_t digit_i = extract_digit(index, qubits[i]) ? pow2(i) : 0;
            ret += digit_i;
        }
        return ret;
    }
    dtype abs_sqr(complex_t c)
    {
        return std::norm(c);
    }
    bool _assert_u22(const u22_t& u)
    {
        // u00 u01
        // u10 u11
        // U * U^dag = I
        auto a00 = u[0], a01 = u[1], a10 = u[2], a11 = u[3];
        auto b00 = std::conj(u[0]), b01 = std::conj(u[2]), b10 = std::conj(u[1]), b11 = std::conj(u[3]);
        if (!complex_equal(a00 * b00 + a01 * b10, 1))
        {
            return false;
        }
        if (!complex_equal(a00 * b01 + a01 * b11, 0))
        {
            return false;
        }
        if (!complex_equal(a10 * b00 + a11 * b10, 0))
        {
            return false;
        }
        if (!complex_equal(a10 * b01 + a11 * b11, 1))
        {
            return false;
        }
        return true;
    }

    u22_t matmul(const u22_t& u1, const u22_t& u2)
    {
        // 0 1
        // 2 3

        const complex_t& a00 = u1[0]; // 第一行第一列
        const complex_t& a01 = u1[1]; // 第一行第二列
        const complex_t& a10 = u1[2]; // 第二行第一列
        const complex_t& a11 = u1[3]; // 第二行第二列

        const complex_t& b00 = u2[0]; // 第一行第一列
        const complex_t& b01 = u2[1]; // 第一行第二列
        const complex_t& b10 = u2[2]; // 第二行第一列
        const complex_t& b11 = u2[3]; // 第二行第二列

        // 明确标注行列运算
        const complex_t c00 = a00 * b00 + a01 * b10; // 行1 × 列1
        const complex_t c01 = a00 * b01 + a01 * b11; // 行1 × 列2
        const complex_t c10 = a10 * b00 + a11 * b10; // 行2 × 列1
        const complex_t c11 = a10 * b01 + a11 * b11; // 行2 × 列2

        return { c00, c01, c10, c11 };
    }

    u44_t matmul(const u44_t& u1, const u44_t& u2)
    {
        u44_t ret;
        for (int i = 0; i < 4; ++i) {
            for (int j = 0; j < 4; ++j) {
                val(ret, i, j) = 0;
                for (int k = 0; k < 4; ++k) {
                    val(ret, i, j) += val(u1, i, k) * val(u2, k, j);
                }
            }
        }
        return ret;
    }

    u22_t dag(const u22_t& u)
    {
        complex_t u00 = u[0];
        complex_t u01 = u[1];
        complex_t u10 = u[2];
        complex_t u11 = u[3];

        complex_t udag00 = std::conj(u[0]);
        complex_t udag10 = std::conj(u[1]);
        complex_t udag01 = std::conj(u[2]);
        complex_t udag11 = std::conj(u[3]);

        u22_t udag = { udag00, udag01, udag10, udag11 };
        return udag;
    }


    u44_t dag(const u44_t& u)
    {
        u44_t udag;
        for (int i = 0; i < 4; ++i) {
            for (int j = 0; j < 4; ++j) {
                val(udag, i, j) = std::conj(val(u, j, i));
            }
        }
        return udag;
    }

    bool validate_kraus(const std::vector<u22_t>& kraus_ops) {
        // 计算sum(E†E)
        u22_t sum = { 0, 0, 0, 0 };
        for (const auto& E : kraus_ops) {
            u22_t E_dag = dag(E);      // 共轭转置
            u22_t product = matmul(E_dag, E);

            // 累加到sum
            sum[0] += product[0];
            sum[1] += product[1];
            sum[2] += product[2];
            sum[3] += product[3];
        }

        // 检查是否近似单位矩阵
        return (std::abs(sum[0] - 1.0) < eps) &&
            (std::abs(sum[1]) < eps) &&
            (std::abs(sum[2]) < eps) &&
            (std::abs(sum[3] - 1.0) < eps);
    }


    bool validate_kraus(const std::vector<u44_t>& kraus_ops) {
        // 计算sum(E†E)
        u44_t sum;
        sum.fill(0);
        for (const auto& E : kraus_ops) {
            u44_t E_dag = dag(E);      // 共轭转置
            u44_t product = matmul(E_dag, E);

            for (int i = 0; i < 16; ++i) {
                sum[i] += product[i];
            }
        }

        // 检查是否近似单位矩阵
        for (int i = 0; i < 4; ++i) {
            for (int j = 0; j < 4; ++j) {
                if (std::abs(sum[i * 4 + j] - (i == j? 1.0 : 0.0)) > eps) {
                    return false;
                }
            }
        }
        return true;
    }
}