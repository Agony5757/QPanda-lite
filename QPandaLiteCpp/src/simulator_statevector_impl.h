#pragma once

#include "simulator_common.h"

namespace qpandalite {
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
        
        double prob_0(const std::vector<complex_t>& state, size_t qn, size_t total_qubit);

        double prob_1(const std::vector<complex_t>& state, size_t qn, size_t total_qubit);

        void rescale_state(std::vector<complex_t>& state, double norm);

        void amplitude_damping_unsafe_impl(std::vector<complex_t>& state, size_t qn, double gamma, size_t total_qubit);

        void kraus1q_unsafe_impl(std::vector<complex_t>& state, size_t qn, const std::vector<u22_t>& kraus, size_t total_qubit);

        dtype get_prob_unsafe_impl(const std::vector<complex_t>& state, size_t qn, int qstate, size_t total_qubit);

        dtype get_prob_unsafe_impl(const std::vector<complex_t>& state, const std::map<size_t, int> measure_map, size_t total_qubit);

    } // namespace statevector_simulator_impl
} // namespace qpandalite
