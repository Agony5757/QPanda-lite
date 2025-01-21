#pragma once

#include <array>
#include <complex>
#include <iostream>
#include <vector>
#include <set>
#include <map>
#include <cstdint>

#include "errors.h"

#define CHECK_QUBIT_RANGE(qn) \
        if (qn >= total_qubit)\
        {\
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input = {})", total_qubit, qn);\
            ThrowInvalidArgument(errstr);\
        }

#define CHECK_QUBIT_RANGE2(qn, name) \
        if (qn >= total_qubit)\
        {\
            auto errstr = fmt::format("Exceed total (total_qubit = {}, {} = {})", total_qubit, #name, qn);\
            ThrowInvalidArgument(errstr);\
        }

#define CHECK_DUPLICATE_QUBIT(qn1, qn2) \
    if (qn1 == qn2)\
    {\
        auto errstr = fmt::format("qn1 = qn2");\
        ThrowInvalidArgument(errstr);\
    }

namespace qpandalite {
    using dtype = double;
    using complex_t = std::complex<dtype>;
    using u22_t = std::array<complex_t, 4>;

    constexpr dtype SQRT2 = 1.4142135623730951;
    constexpr dtype INVSQRT2 = 1.0 / SQRT2;
    constexpr dtype eps = 1e-7;

    constexpr unsigned long long pow2(size_t n) { return 1ull << n; }
    constexpr auto abs_sqr(complex_t c)
    {
        return c.real() * c.real() + c.imag() * c.imag();
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

    inline bool _assert_u22(const u22_t& u)
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

    inline std::map<size_t, size_t> preprocess_measure_list(const std::vector<size_t>& measure_list, size_t total_qubit)
    {
        if (measure_list.size() > total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, measure_list size = {})", total_qubit, measure_list.size());
            ThrowInvalidArgument(errstr);
        }

        std::map<size_t, size_t> qlist;
        for (size_t i = 0; i < measure_list.size(); ++i)
        {
            size_t qn = measure_list[i];
            if (qn >= total_qubit)
            {
                auto errstr = fmt::format("Exceed total (total_qubit = {}, measure_qubit = {})", total_qubit, qn);
                ThrowInvalidArgument(errstr);
            }
            if (qlist.find(qn) != qlist.end())
            {
                auto errstr = fmt::format("Duplicate measure qubit ({})", qn);
                ThrowInvalidArgument(errstr);
            }
            qlist.insert({ qn,i });
        }
        return qlist;
    }

    inline size_t get_state_with_qubit(size_t i, const std::map<size_t, size_t>& measure_map)
    {
        size_t ret = 0;
        for (auto&& [qn, j] : measure_map)
        {
            // put "digit qn" of i to "digit j"
            ret += (((i >> qn) & 1) << j);
        }
        return ret;
    }

    inline size_t make_controller_mask(const std::vector<size_t>& global_controller)
    {
        size_t mask = 0;
        for (size_t qn : global_controller)
        {
            mask |= (1ull << qn);
        }
        return mask;
    }

    inline void hadamard_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask) 
                continue;
            if ((i >> qn) & 1) 
                continue;

            size_t i0 = i;
            size_t i1 = i + pow2(qn);

            complex_t a0 = state[i0];
            complex_t a1 = state[i1];

            complex_t new_a0 = (a0 + a1) * INVSQRT2;
            complex_t new_a1 = (a0 - a1) * INVSQRT2;

            state[i0] = new_a0;
            state[i1] = new_a1;
        }
    }

    inline void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn, 
        complex_t u00, complex_t u01, complex_t u10, complex_t u11, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;
            if ((i >> qn) & 1)
                continue;

            size_t i0 = i;
            size_t i1 = i + pow2(qn);

            complex_t a0 = state[i0];
            complex_t a1 = state[i1];

            complex_t new_a0 = u00 * a0 + u01 * a1;
            complex_t new_a1 = u10 * a0 + u11 * a1;

            state[i0] = new_a0;
            state[i1] = new_a1;
        }
    }

    inline void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn, u22_t unitary, size_t total_qubit, size_t controller_mask)
    {
        return u22_unsafe_impl(state, qn, unitary[0], unitary[1], unitary[2], unitary[3], total_qubit, controller_mask);
    }

    inline void x_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                std::swap(state[i], state[i - pow2(qn)]);
            }
        }
    }

    inline void y_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                std::swap(state[i], state[i - pow2(qn)]);
                state[i - pow2(qn)] *= -1i;
                state[i] *= 1i;
            }
        }
    }

    inline void z_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                state[i] *= -1;
            }
        }
    }


    inline void s_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                state[i] *= 1i;
            }
        }
    }


    inline void sdg_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                state[i] *= -1i;
            }
        }
    }

    inline void t_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                state[i] *= complex_t(INVSQRT2, INVSQRT2);
            }
        }
    }

    inline void tdg_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                state[i] *= complex_t(INVSQRT2, -INVSQRT2);
            }
        }
    }

    inline void cz_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if (((i >> qn1) & 1) && ((i >> qn2) & 1))
            {
                state[i] *= -1;
            }
        }
    }

    inline void swap_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            bool v1 = (i >> qn1) & 1;
            bool v2 = (i >> qn2) & 1;
            if (v1 && (!v2))
            {
                // |10>
                // let it swap with |01>
                std::swap(state[i - pow2(qn1) + pow2(qn2)], state[i]);
            }

        }
    }

    inline void iswap_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t total_qubit, size_t controller_mask, bool is_dagger)
    {
        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if (((i >> qn1) & 1) == 0 && ((i >> qn2) & 1) == 1)
            {
                std::swap(state[i], state[i + pow2(qn1) - pow2(qn2)]);
                if (is_dagger)
                {
                    state[i] *= -1i;
                    state[i + pow2(qn1) - pow2(qn2)] *= -1i;
                }
                else
                {
                    state[i] *= 1i;
                    state[i + pow2(qn1) - pow2(qn2)] *= 1i;
                }
            }
        }
    }

    /* H = 1/2 * (XX+YY) 
    
       XY(theta) = exp(-i*theta/2 * H)
          = [ 1 0 0 0 ]
            [ 0 cos(theta/2) -i sin(theta/2) 0 ]
            [ 0 -i sin(theta/2) cos(theta/2) 0 ]
            [ 0 0 0 1 ]
    
    */
    inline void xy_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger)
    {
        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;
            // |01>
            if (((i >> qn1) & 0) && ((i >> qn2) & 1))
            {
                size_t i2 = i + pow2(qn1) - pow2(qn2);
                complex_t s1 = state[i];
                complex_t s2 = state[i2];
                if (is_dagger)
                {
                    state[i] = s1 * cos(theta / 2) + s2 * 1i * sin(theta / 2);
                    state[i2] = s1 * 1i * sin(theta / 2) + cos(theta / 2) * s2;
                }
                else
                {
                    state[i] = s1 * cos(theta / 2) - s2 * 1i * sin(theta / 2);
                    state[i2] = -s1 * 1i * sin(theta / 2) + cos(theta / 2) * s2;
                }
            }
        }
    }

    inline void cnot_unsafe_impl(std::vector<complex_t>& state, size_t controller, size_t target, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if (((i >> controller) & 1) && ((i >> target) & 1))
            {
                std::swap(state[i], state[i - pow2(target)]);
            }
        }
    }

    inline void rz_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if (((i >> qn) & 1) ^ is_dagger)
            {
                // 0 and not dagger -> exp(-it/2)
                // 1 and dagger -> exp(-it/2)
                state[i] *= std::complex(cos(theta / 2), sin(theta / 2));
            }
            else
            {
                // 0 and dagger -> exp(it/2)
                // 1 and not dagger -> exp(it/2)
                state[i] *= std::complex(cos(theta / 2), -sin(theta / 2));
            }
        }
    }

    inline void u1_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                if (is_dagger)
                    state[i] *= std::complex(cos(theta), -sin(theta));
                else
                    state[i] *= std::complex(cos(theta), sin(theta));
            }
        }
    }

    inline void toffoli_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t target, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if (((i >> qn1) & 1) && ((i >> qn2) & 1) && ((i >> target) & 1))
            {
                std::swap(state[i], state[i - pow2(target)]);
            }
        }
    }

    inline void cswap_unsafe_impl(std::vector<complex_t>& state, size_t controller, size_t target1, size_t target2, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if (!((i >> controller) & 1))
                continue;

            bool v1 = (i >> target1) & 1;
            bool v2 = (i >> target2) & 1;
            if (v1 && (!v2))
            {
                // |10>
                // let it swap with |01>
                std::swap(state[i - pow2(target1) + pow2(target2)], state[i]);
            }
        }
    }

    /* ZZ interaction
    * exp(-i*theta/2 * ZZ)
    *    |00> -> exp(-i*theta/2) * |00>
    *    |01> -> exp(i*theta/2) * |01>
    *    |10> -> exp(i*theta/2) * |10>
    *    |11> -> exp(-i*theta/2) * |11>
    */
    inline void zz_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;
            bool v1 = (i >> qn1) & 1;
            bool v2 = (i >> qn2) & 1;
            if (v1 == v2) /* 00 or 11 */
            {
                state[i] *= complex_t(cos(theta / 2), sin(-theta / 2));
            }
            else /* 01 or 10 */
            {
                state[i] *= complex_t(cos(theta / 2), sin(theta / 2));
            }
        }
    }


    /* XX interaction
    * exp(-i*theta/2 * XX)
    *    |00> -> [ cos(t)    0       0      isin(t) ]
    *    |01> -> [   0     cos(t)  isin(t)    0     ]
    *    |10> -> [   0     isin(t)  cos(t)    0     ]
    *    |11> -> [ isin(t)   0       0       cos(t) ] where t=-theta/2
    */
    inline void xx_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;

        /* the RXX will be implemented as exp(-i*theta/2 * XX) */
        theta = -theta / 2;

        complex_t ctheta = cos(theta);
        complex_t stheta = sin(theta);
        complex_t istheta = 1i * stheta;

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;
            bool v1 = (i >> qn1) & 1;
            bool v2 = (i >> qn2) & 1;
            if (v1 == false && v2 == false) /* 00 */
            {
                /* only 00 will be operated */
                size_t i00 = i;
                size_t i01 = i + pow2(qn1);
                size_t i10 = i + pow2(qn2);
                size_t i11 = i + pow2(qn1) + pow2(qn2);

                complex_t a00 = state[i00];
                complex_t a01 = state[i01];
                complex_t a10 = state[i10];
                complex_t a11 = state[i11];

                state[i00] = a00 * ctheta + a11 * istheta;
                state[i01] = a01 * ctheta + a10 * istheta;
                state[i10] = a01 * istheta + a10 * ctheta;
                state[i11] = a00 * istheta + a11 * ctheta;
            }
        }
    } 

    /* YY interaction
    *
    * exp(-i*theta/2 * YY)
   *    |00> -> [ cos(t)    0       0      -isin(t) ]
   *    |01> -> [   0     cos(t)  isin(t)    0     ]
   *    |10> -> [   0     isin(t)  cos(t)    0     ]
   *    |11> -> [ -isin(t)   0       0       cos(t) ] where t=-theta/2
   */
    inline void yy_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;

        /* the RYY will be implemented as exp(-i*theta/2 * YY) */
        theta = -theta / 2;

        complex_t ctheta = cos(theta);
        complex_t stheta = sin(theta);
        complex_t istheta = 1i * stheta;

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;
            bool v1 = (i >> qn1) & 1;
            bool v2 = (i >> qn2) & 1;
            if (v1 == false && v2 == false) /* 00 */
            {
                /* only 00 will be operated */
                size_t i00 = i;
                size_t i01 = i + pow2(qn1);
                size_t i10 = i + pow2(qn2);
                size_t i11 = i + pow2(qn1) + pow2(qn2);

                complex_t a00 = state[i00];
                complex_t a01 = state[i01];
                complex_t a10 = state[i10];
                complex_t a11 = state[i11];

                state[i00] = a00 * ctheta - a11 * istheta;
                state[i01] = a01 * ctheta + a10 * istheta;
                state[i10] = a01 * istheta + a10 * ctheta;
                state[i11] = -a00 * istheta + a11 * ctheta;
            }
        }
    }
}