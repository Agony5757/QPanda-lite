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

    bool _assert_u22(const u22_t& u);

    std::map<size_t, size_t> preprocess_measure_list(const std::vector<size_t>& measure_list, size_t total_qubit);

    size_t get_state_with_qubit(size_t i, const std::map<size_t, size_t>& measure_map);

    size_t make_controller_mask(const std::vector<size_t>& global_controller);

    namespace statevector_simulator_impl
    {
        void hadamard_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn,
            complex_t u00, complex_t u01, complex_t u10, complex_t u11, size_t total_qubit, size_t controller_mask);

        void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn, u22_t unitary, size_t total_qubit, size_t controller_mask);

        void u3_unsafe_impl(std::vector<complex_t>& state, size_t qn,
            double theta, double phi, double lambda,
            size_t total_qubit, size_t controller_mask, bool is_dagger);

        void x_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void y_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void z_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void s_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void sdg_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void t_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void tdg_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void cz_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t total_qubit, size_t controller_mask);

        void swap_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t total_qubit, size_t controller_mask);

        void iswap_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t total_qubit, size_t controller_mask, bool is_dagger);

        /* H = 1/2 * (XX+YY)

           XY(theta) = exp(-i*theta/2 * H)
              = [ 1 0 0 0 ]
                [ 0 cos(theta/2) -i sin(theta/2) 0 ]
                [ 0 -i sin(theta/2) cos(theta/2) 0 ]
                [ 0 0 0 1 ]
        */
        void xy_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger);

        void cnot_unsafe_impl(std::vector<complex_t>& state, size_t controller, size_t target, size_t total_qubit, size_t controller_mask);

        void rz_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger);

        void u1_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger);

        void toffoli_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t target, size_t total_qubit, size_t controller_mask);

        void cswap_unsafe_impl(std::vector<complex_t>& state, size_t controller, size_t target1, size_t target2, size_t total_qubit, size_t controller_mask);

        /* ZZ interaction
        * exp(-i*theta/2 * ZZ)
        *    |00> -> exp(-i*theta/2) * |00>
        *    |01> -> exp(i*theta/2) * |01>
        *    |10> -> exp(i*theta/2) * |10>
        *    |11> -> exp(-i*theta/2) * |11>
        */
        void zz_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask);


        /* XX interaction
        * exp(-i*theta/2 * XX)
        *    |00> -> [ cos(t)    0       0      isin(t) ]
        *    |01> -> [   0     cos(t)  isin(t)    0     ]
        *    |10> -> [   0     isin(t)  cos(t)    0     ]
        *    |11> -> [ isin(t)   0       0       cos(t) ] where t=-theta/2
        */
        void xx_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask);

        /* YY interaction
        *
        * exp(-i*theta/2 * YY)
       *    |00> -> [ cos(t)    0       0      -isin(t) ]
       *    |01> -> [   0     cos(t)  isin(t)    0     ]
       *    |10> -> [   0     isin(t)  cos(t)    0     ]
       *    |11> -> [ -isin(t)   0       0       cos(t) ] where t=-theta/2
       */
        void yy_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask);

        /* phase2q gate =
           u1(qn1, theta1),
           u1(qn2, theta2),
           zz(qn1, qn2, thetazz)
        */
        void phase2q_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta1, double theta2, double thetazz,
            size_t total_qubit, size_t controller_mask);

        /* uu15 gate using KAK decomposition

            U is implemented by

            U3(q1, parameters[0:3])
            U3(q2, parameters[3:6])
            XX(q1, q2, parameters[6])
            YY(q1, q2, parameters[7])
            ZZ(q1, q2, parameters[8])
            U3(q1, parameters[9:12])
            U3(q2, parameters[12:15])

            where parameters[0:15] are the 15 parameters of the gate.
        */
        void uu15_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2,
            const std::vector<double>& parameters, size_t total_qubit, size_t controller_mask, bool is_dagger);
    } // namespace statevector_simulator_impl

    namespace density_operator_simulator_impl
    {
        complex_t& val(std::vector<complex_t>& state, size_t i, size_t j, size_t N);
        complex_t val(const std::vector<complex_t>& state, size_t i, size_t j, size_t N);

        void evolve_u22(const u22_t& mat, complex_t& i0j0, complex_t& i1j0, complex_t& i0j1, complex_t& i1j1);

        void evolve_u22(const complex_t& U00, const complex_t& U01, const complex_t& U10, const complex_t& U11,
            complex_t& i0j0, complex_t& i1j0, complex_t& i0j1, complex_t& i1j1);

        void hadamard_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn,
            complex_t u00, complex_t u01, complex_t u10, complex_t u11, size_t total_qubit, size_t controller_mask);
        
        void u44_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn1, size_t qn2,
            complex_t u00, complex_t u01, complex_t u02, complex_t u03,
            complex_t u10, complex_t u11, complex_t u12, complex_t u13,
            complex_t u20, complex_t u21, complex_t u22, complex_t u23,
            complex_t u30, complex_t u31, complex_t u32, complex_t u33,
            size_t total_qubit, size_t controller_mask);

        void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn, u22_t unitary, size_t total_qubit, size_t controller_mask);

        void u3_unsafe_impl(std::vector<complex_t>& state, size_t qn,
            double theta, double phi, double lambda,
            size_t total_qubit, size_t controller_mask, bool is_dagger);

        void x_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void y_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void z_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void s_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void sdg_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void t_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void tdg_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void cz_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t total_qubit, size_t controller_mask);

        void swap_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t total_qubit, size_t controller_mask);

        void iswap_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t total_qubit, size_t controller_mask, bool is_dagger);

        /* H = 1/2 * (XX+YY)

           XY(theta) = exp(-i*theta/2 * H)
              = [ 1 0 0 0 ]
                [ 0 cos(theta/2) -i sin(theta/2) 0 ]
                [ 0 -i sin(theta/2) cos(theta/2) 0 ]
                [ 0 0 0 1 ]
        */
        void xy_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger);

        void cnot_unsafe_impl(std::vector<complex_t>& state, size_t controller, size_t target, size_t total_qubit, size_t controller_mask);

        void rz_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger);

        void u1_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger);

        void toffoli_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t target, size_t total_qubit, size_t controller_mask);

        void cswap_unsafe_impl(std::vector<complex_t>& state, size_t controller, size_t target1, size_t target2, size_t total_qubit, size_t controller_mask);

        /* ZZ interaction
        * exp(-i*theta/2 * ZZ)
        *    |00> -> exp(-i*theta/2) * |00>
        *    |01> -> exp(i*theta/2) * |01>
        *    |10> -> exp(i*theta/2) * |10>
        *    |11> -> exp(-i*theta/2) * |11>
        */
        void zz_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask);


        /* XX interaction
        * exp(-i*theta/2 * XX)
        *    |00> -> [ cos(t)    0       0      isin(t) ]
        *    |01> -> [   0     cos(t)  isin(t)    0     ]
        *    |10> -> [   0     isin(t)  cos(t)    0     ]
        *    |11> -> [ isin(t)   0       0       cos(t) ] where t=-theta/2
        */
        void xx_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask);

        /* YY interaction
        *
        * exp(-i*theta/2 * YY)
       *    |00> -> [ cos(t)    0       0      -isin(t) ]
       *    |01> -> [   0     cos(t)  isin(t)    0     ]
       *    |10> -> [   0     isin(t)  cos(t)    0     ]
       *    |11> -> [ -isin(t)   0       0       cos(t) ] where t=-theta/2
       */
        void yy_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask);

        /* phase2q gate =
           u1(qn1, theta1),
           u1(qn2, theta2),
           zz(qn1, qn2, thetazz)
        */
        void phase2q_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta1, double theta2, double thetazz,
            size_t total_qubit, size_t controller_mask);

        /* uu15 gate using KAK decomposition

            U is implemented by

            U3(q1, parameters[0:3])
            U3(q2, parameters[3:6])
            XX(q1, q2, parameters[6])
            YY(q1, q2, parameters[7])
            ZZ(q1, q2, parameters[8])
            U3(q1, parameters[9:12])
            U3(q2, parameters[12:15])

            where parameters[0:15] are the 15 parameters of the gate.
        */
        void uu15_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2,
            const std::vector<double>& parameters, size_t total_qubit, size_t controller_mask, bool is_dagger);
    }

} // namespace qpandalite