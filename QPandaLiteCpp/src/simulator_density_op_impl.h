#pragma once

#include "simulator_common.h"

namespace qpandalite {
    namespace density_operator_simulator_impl
    {
        complex_t& val(std::vector<complex_t>& state, size_t i, size_t j, size_t N);
        complex_t val(const std::vector<complex_t>& state, size_t i, size_t j, size_t N);

        void evolve_u22(const u22_t& mat, complex_t& i0j0, complex_t& i1j0, complex_t& i0j1, complex_t& i1j1);

        void evolve_u22(const complex_t& U00, const complex_t& U01, const complex_t& U10, const complex_t& U11,
            complex_t& i0j0, complex_t& i1j0, complex_t& i0j1, complex_t& i1j1);

        void apply_irho_udag_u22(
            const complex_t& U00, const complex_t& U01,
            const complex_t& U10, const complex_t& U11,
            complex_t& i0j0, complex_t& i0j1,
            complex_t& i1j0, complex_t& i1j1
        );

        void apply_urho_i_u22(
            const complex_t& U00, const complex_t& U01,
            const complex_t& U10, const complex_t& U11,
            complex_t& i0j0, complex_t& i0j1,
            complex_t& i1j0, complex_t& i1j1
        );

        void hadamard_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask);

        void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn,
            complex_t u00, complex_t u01, complex_t u10, complex_t u11, size_t total_qubit, size_t controller_mask);

        void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn, u22_t unitary, size_t total_qubit, size_t controller_mask);

        void evolve_u44(
            const complex_t& U00, const complex_t& U01, const complex_t& U02, const complex_t& U03,
            const complex_t& U10, const complex_t& U11, const complex_t& U12, const complex_t& U13,
            const complex_t& U20, const complex_t& U21, const complex_t& U22, const complex_t& U23,
            const complex_t& U30, const complex_t& U31, const complex_t& U32, const complex_t& U33,
            complex_t& i00j00, complex_t& i00j01, complex_t& i00j10, complex_t& i00j11,
            complex_t& i01j00, complex_t& i01j01, complex_t& i01j10, complex_t& i01j11,
            complex_t& i10j00, complex_t& i10j01, complex_t& i10j10, complex_t& i10j11,
            complex_t& i11j00, complex_t& i11j01, complex_t& i11j10, complex_t& i11j11);

        void apply_irho_udag_u44(const complex_t& U00, const complex_t& U01, const complex_t& U02, const complex_t& U03, const complex_t& U10, const complex_t& U11, const complex_t& U12, const complex_t& U13, const complex_t& U20, const complex_t& U21, const complex_t& U22, const complex_t& U23, const complex_t& U30, const complex_t& U31, const complex_t& U32, const complex_t& U33, complex_t& i00j00, complex_t& i00j01, complex_t& i00j10, complex_t& i00j11, complex_t& i01j00, complex_t& i01j01, complex_t& i01j10, complex_t& i01j11, complex_t& i10j00, complex_t& i10j01, complex_t& i10j10, complex_t& i10j11, complex_t& i11j00, complex_t& i11j01, complex_t& i11j10, complex_t& i11j11);

        void apply_urho_i_u44(const complex_t& U00, const complex_t& U01, const complex_t& U02, const complex_t& U03, const complex_t& U10, const complex_t& U11, const complex_t& U12, const complex_t& U13, const complex_t& U20, const complex_t& U21, const complex_t& U22, const complex_t& U23, const complex_t& U30, const complex_t& U31, const complex_t& U32, const complex_t& U33, complex_t& i00j00, complex_t& i00j01, complex_t& i00j10, complex_t& i00j11, complex_t& i01j00, complex_t& i01j01, complex_t& i01j10, complex_t& i01j11, complex_t& i10j00, complex_t& i10j01, complex_t& i10j10, complex_t& i10j11, complex_t& i11j00, complex_t& i11j01, complex_t& i11j10, complex_t& i11j11);

        void _u44_unsafe_impl_ctrl(std::vector<std::complex<double>>& state, size_t qn1, size_t qn2, complex_t u00, complex_t u01, complex_t u02, complex_t u03, complex_t u10, complex_t u11, complex_t u12, complex_t u13, complex_t u20, complex_t u21, complex_t u22, complex_t u23, complex_t u30, complex_t u31, complex_t u32, complex_t u33, size_t total_qubit, size_t controller_mask);

        void u44_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn1, size_t qn2,
            complex_t u00, complex_t u01, complex_t u02, complex_t u03,
            complex_t u10, complex_t u11, complex_t u12, complex_t u13,
            complex_t u20, complex_t u21, complex_t u22, complex_t u23,
            complex_t u30, complex_t u31, complex_t u32, complex_t u33,
            size_t total_qubit, size_t controller_mask);

        void u44_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn1, size_t qn2, u44_t unitary, size_t total_qubit, size_t controller_mask);

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

        /* H = 1/2 * (XX+YY) */
        void xy_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger);

        void cnot_unsafe_impl(std::vector<complex_t>& state, size_t controller, size_t target, size_t total_qubit, size_t controller_mask);

        void rz_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger);

        void u1_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger);

        void toffoli_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t target, size_t total_qubit, size_t controller_mask);

        void cswap_unsafe_impl(std::vector<complex_t>& state, size_t controller, size_t target1, size_t target2, size_t total_qubit, size_t controller_mask);

        void cu1_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger);

        /* ZZ interaction */
        void zz_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask);

        /* XX interaction */
        void xx_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask);

        /* YY interaction */
        void yy_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask);

        /* phase2q gate */
        void phase2q_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta1, double theta2, double thetazz,
            size_t total_qubit, size_t controller_mask);

        /* uu15 gate using KAK decomposition */
        void uu15_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2,
            const std::vector<double>& parameters, size_t total_qubit, size_t controller_mask, bool is_dagger);

        template<typename Container, typename Scalar, typename BinaryOpType>
        auto generic_operator_scalar(const Container& state, Scalar val, BinaryOpType op)
            -> Container
        {
            Container ret(state);
            for (auto& v : ret)
            {
                v = op(v, val);
            }
            return ret;
        }

        template<typename Container, typename Scalar>
        auto multiply_scalar(const Container& state, Scalar val)
            -> Container
        {
            using Scalar2 = decltype(*(std::begin(state)));
            auto mult = [](Scalar2 v1, Scalar v2) { return v1 * v2; };
            return generic_operator_scalar(state, val, mult);
        }

        void merge_state(std::vector<complex_t>& target_state, const std::vector<complex_t>& add_state, double coef = 1.0);

        void kraus1q_unsafe_impl(std::vector<complex_t>& state, size_t qn, const Kraus1Q& kraus1q, size_t total_qubit);

        void pauli_error_2q_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, const std::vector<double>& p, size_t total_qubit);
        
    } // namespace density_operator_simulator_impl
} // namespace qpandalite
